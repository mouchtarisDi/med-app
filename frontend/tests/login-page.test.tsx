import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, expect, test, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import App from '../src/App.js';
import { AuthProvider } from '../src/auth/AuthProvider.js';
import { login as apiLogin, getCurrentUser } from '../src/api/auth.js';
import { ApiError } from '../src/api/client.js';

vi.mock('../src/api/auth.js', () => ({ login: vi.fn(), getCurrentUser: vi.fn() }));
const loginMock = vi.mocked(apiLogin);
const meMock = vi.mocked(getCurrentUser);
const credentials = { email: 'test@example.com', password: 'synthetic-password' };
const token = { access_token: 'synthetic-private-token', token_type: 'bearer' as const };
const user = { full_name: 'Δοκιμαστικός Χρήστης', email: credentials.email, id: 42 };

function showApp() {
  return render(<AuthProvider><MemoryRouter initialEntries={['/login']}><App /></MemoryRouter></AuthProvider>);
}

function fillAndSubmit() {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: credentials.email } });
  fireEvent.change(screen.getByLabelText('Κωδικός'), { target: { value: credentials.password } });
  fireEvent.click(screen.getByRole('button', { name: 'Σύνδεση' }));
}

beforeEach(() => {
  vi.resetAllMocks();
  loginMock.mockResolvedValue(token);
  meMock.mockResolvedValue(user);
});

test('renders Greek login form with associated labels and native input semantics', () => {
  showApp();
  expect(screen.getByRole('heading', { name: 'Σύνδεση' })).toBeTruthy();
  expect(screen.getByText('Συνδεθείτε για να συνεχίσετε.')).toBeTruthy();
  const email = screen.getByLabelText('Email') as HTMLInputElement;
  const password = screen.getByLabelText('Κωδικός') as HTMLInputElement;
  expect(email.type).toBe('email');
  expect(email.autocomplete).toBe('email');
  expect(email.required).toBe(true);
  expect(password.type).toBe('password');
  expect(password.autocomplete).toBe('current-password');
  expect(password.required).toBe(true);
  expect((screen.getByRole('button', { name: 'Σύνδεση' }) as HTMLButtonElement).type).toBe('submit');
});

test('credentials go through provider; pending current user keeps form busy and disabled', async () => {
  let resolveMe!: (value: typeof user) => void;
  meMock.mockReturnValue(new Promise((resolve) => { resolveMe = resolve; }));
  showApp();
  fillAndSubmit();
  await waitFor(() => expect(meMock).toHaveBeenCalledWith(token.access_token));
  expect(loginMock).toHaveBeenCalledWith(credentials);
  const pendingButton = screen.getByRole('button', { name: 'Σύνδεση...' }) as HTMLButtonElement;
  expect(pendingButton.disabled).toBe(true);
  expect((screen.getByLabelText('Email') as HTMLInputElement).disabled).toBe(true);
  expect((screen.getByLabelText('Κωδικός') as HTMLInputElement).disabled).toBe(true);
  expect(pendingButton.closest('form')?.getAttribute('aria-busy')).toBe('true');
  expect(screen.queryByRole('heading', { name: 'Dashboard' })).toBeNull();
  fireEvent.click(pendingButton);
  expect(loginMock).toHaveBeenCalledTimes(1);
  await act(async () => { resolveMe(user); });
  expect(await screen.findByRole('heading', { name: 'Dashboard' })).toBeTruthy();
});

const generic = 'Δεν ήταν δυνατή η σύνδεση. Δοκιμάστε ξανά.';
test.each([
  [new ApiError('authentication', 401), 'Λανθασμένο email ή κωδικός.'],
  [new ApiError('forbidden', 403), 'Ο λογαριασμός σας είναι ανενεργός.'],
  [new ApiError('network', null), 'Δεν ήταν δυνατή η σύνδεση. Ελέγξτε τη σύνδεσή σας στο διαδίκτυο και δοκιμάστε ξανά.'],
  [new ApiError('server', 500), 'Παρουσιάστηκε προσωρινό πρόβλημα στον διακομιστή. Δοκιμάστε ξανά αργότερα.'],
  [new ApiError('validation', 422, [{ msg: 'synthetic-sensitive-detail' }]), generic],
  [new ApiError('http', 400), generic],
  [new ApiError('response', 200), generic],
  [new Error('synthetic-technical-message'), generic],
])('shows safe Greek error for %s', async (error, message) => {
  loginMock.mockRejectedValue(error);
  const { container } = showApp();
  fillAndSubmit();
  expect((await screen.findByRole('alert')).textContent).toBe(message);
  expect(container.textContent).not.toContain(error.message);
  expect(container.textContent).not.toContain('synthetic-sensitive-detail');
  expect(container.textContent).not.toContain(token.access_token);
  expect(container.textContent).not.toContain(credentials.password);
  expect(container.textContent).not.toMatch(/401|403|422|500/);
  const password = screen.getByLabelText('Κωδικός') as HTMLInputElement;
  expect(password.type).toBe('password');
  expect(password.value).toBe('');
  expect((screen.getByLabelText('Email') as HTMLInputElement).value).toBe(credentials.email);
  expect((screen.getByRole('button', { name: 'Σύνδεση' }) as HTMLButtonElement).disabled).toBe(false);
});

test('successful current user shows account details without token and logout clears form', async () => {
  const { container } = showApp();
  fillAndSubmit();
  const heading = await screen.findByRole('heading', { name: 'Dashboard' });
  const sidebar = screen.getByRole('complementary', { name: 'Πλαϊνή μπάρα' });
  expect(within(sidebar).getByText(user.full_name)).toBeTruthy();
  expect(within(sidebar).getByText(user.email)).toBeTruthy();
  expect(container.innerHTML).not.toContain(token.access_token);
  expect(container.innerHTML).not.toContain(credentials.password);
  expect(document.activeElement).toBe(heading);
  fireEvent.click(screen.getByRole('button', { name: 'Αποσύνδεση' }));
  expect(await screen.findByRole('heading', { name: 'Σύνδεση' })).toBeTruthy();
  expect((screen.getByLabelText('Email') as HTMLInputElement).value).toBe('');
  expect((screen.getByLabelText('Κωδικός') as HTMLInputElement).value).toBe('');
});
