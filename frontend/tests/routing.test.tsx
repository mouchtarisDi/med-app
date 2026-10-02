import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { MemoryRouter, useLocation, useNavigate } from 'react-router-dom';
import { beforeEach, expect, test, vi } from 'vitest';
import App from '../src/App.js';
import { AuthProvider } from '../src/auth/AuthProvider.js';
import { useAuth } from '../src/auth/useAuth.js';
import { getCurrentUser, login as apiLogin } from '../src/api/auth.js';

vi.mock('../src/api/auth.js', () => ({ login: vi.fn(), getCurrentUser: vi.fn() }));
const loginMock = vi.mocked(apiLogin);
const meMock = vi.mocked(getCurrentUser);
const credentials = { email: 'test@example.com', password: 'synthetic-password' };
const token = { access_token: 'synthetic-token', token_type: 'bearer' as const };
const user = { full_name: 'Test User', email: credentials.email, id: 42 };

function RoutingProbe() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { status } = useAuth();
  return <>
    <output data-testid="pathname">{pathname}</output>
    <output data-testid="auth-status">{status}</output>
    <button onClick={() => navigate('/login')}>Visit login</button>
    <button onClick={() => navigate('/unknown')}>Visit unknown</button>
  </>;
}

function showApp(path: string) {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={[path]}>
        <App /><RoutingProbe />
      </MemoryRouter>
    </AuthProvider>,
  );
}

async function expectPath(path: string) {
  await waitFor(() => expect(screen.getByTestId('pathname').textContent).toBe(path));
}

async function signIn() {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: credentials.email } });
  fireEvent.change(screen.getByLabelText('Κωδικός'), { target: { value: credentials.password } });
  fireEvent.click(screen.getByRole('button', { name: 'Σύνδεση' }));
  await expectPath('/dashboard');
  expect(await screen.findByRole('heading', { name: 'Dashboard' })).toBeTruthy();
}

beforeEach(() => {
  vi.resetAllMocks();
  loginMock.mockResolvedValue(token);
  meMock.mockResolvedValue(user);
});

test('unauthenticated /login shows login at /login', async () => {
  showApp('/login');
  await expectPath('/login');
  expect(screen.getByRole('heading', { name: 'Σύνδεση' })).toBeTruthy();
  expect(loginMock).not.toHaveBeenCalled();
  expect(meMock).not.toHaveBeenCalled();
});

test('unauthenticated /dashboard redirects to /login without dashboard', async () => {
  showApp('/dashboard');
  await expectPath('/login');
  expect(screen.getByRole('heading', { name: 'Σύνδεση' })).toBeTruthy();
  expect(screen.queryByRole('heading', { name: 'Dashboard' })).toBeNull();
  expect(screen.queryByRole('navigation', { name: 'Κύρια πλοήγηση' })).toBeNull();
});

test('successful login redirects to /dashboard and displays the current user', async () => {
  showApp('/login');
  await signIn();
  expect(loginMock).toHaveBeenCalledWith(credentials);
  expect(meMock).toHaveBeenCalledWith(token.access_token);
  const sidebar = screen.getByRole('complementary', { name: 'Πλαϊνή μπάρα' });
  expect(within(sidebar).getByText(user.full_name)).toBeTruthy();
  expect(within(sidebar).getByText(user.email)).toBeTruthy();
  expect(screen.getByTestId('auth-status').textContent).toBe('authenticated');
});

test('authenticated user visiting /login redirects to /dashboard', async () => {
  showApp('/login');
  await signIn();
  fireEvent.click(screen.getByRole('button', { name: 'Visit login' }));
  await expectPath('/dashboard');
  expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeTruthy();
  expect(screen.queryByRole('heading', { name: 'Σύνδεση' })).toBeNull();
});

test('logout clears auth and redirects to /login', async () => {
  showApp('/login');
  await signIn();
  fireEvent.click(screen.getByRole('button', { name: 'Αποσύνδεση' }));
  await expectPath('/login');
  expect(screen.getByRole('heading', { name: 'Σύνδεση' })).toBeTruthy();
  expect(screen.queryByRole('heading', { name: 'Dashboard' })).toBeNull();
  expect(screen.getByTestId('auth-status').textContent).toBe('idle');
  expect(screen.queryByRole('navigation', { name: 'Κύρια πλοήγηση' })).toBeNull();
});

test('fresh provider at /dashboard loses memory-only authentication', async () => {
  const previous = showApp('/login');
  await signIn();
  previous.unmount();
  vi.clearAllMocks();
  showApp('/dashboard');
  await expectPath('/login');
  expect(screen.getByRole('heading', { name: 'Σύνδεση' })).toBeTruthy();
  expect(screen.queryByRole('heading', { name: 'Dashboard' })).toBeNull();
  expect(screen.getByTestId('auth-status').textContent).toBe('idle');
  expect(loginMock).not.toHaveBeenCalled();
  expect(meMock).not.toHaveBeenCalled();
});

test('unknown URL redirects unauthenticated user to /login', async () => {
  showApp('/unknown');
  await expectPath('/login');
  expect(screen.getByRole('heading', { name: 'Σύνδεση' })).toBeTruthy();
});

test('unknown URL redirects authenticated user to /dashboard', async () => {
  showApp('/login');
  await signIn();
  fireEvent.click(screen.getByRole('button', { name: 'Visit unknown' }));
  await expectPath('/dashboard');
  expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeTruthy();
});

test('authenticated shell surrounds dashboard with real navigation and account controls', async () => {
  const { container } = showApp('/login');
  await signIn();
  const sidebar = screen.getByRole('complementary', { name: 'Πλαϊνή μπάρα' });
  const navigation = within(sidebar).getByRole('navigation', { name: 'Κύρια πλοήγηση' });
  const links = within(navigation).getAllByRole('link');
  expect(links).toHaveLength(1);
  expect(links[0].getAttribute('href')).toBe('/dashboard');
  expect(links[0].getAttribute('aria-current')).toBe('page');
  expect(within(sidebar).getByText(user.full_name)).toBeTruthy();
  expect(within(sidebar).getByText(user.email)).toBeTruthy();
  expect(within(sidebar).getByRole('button', { name: 'Αποσύνδεση' })).toBeTruthy();
  expect(screen.getAllByRole('main')).toHaveLength(1);
  const main = screen.getByRole('main');
  const heading = within(main).getByRole('heading', { name: 'Dashboard' });
  expect(within(main).getByText(`Καλώς ήρθες, ${user.full_name}.`)).toBeTruthy();
  expect(document.activeElement).toBe(heading);
  expect(within(main).queryByText(user.email)).toBeNull();
  expect(within(main).queryByRole('button', { name: 'Αποσύνδεση' })).toBeNull();
  expect(container.innerHTML).not.toContain(token.access_token);
  expect(container.innerHTML).not.toContain(credentials.password);
  expect(screen.getByRole('link', { name: 'Μετάβαση στο περιεχόμενο' }).getAttribute('href'))
    .toBe('#' + main.id);
  fireEvent.click(links[0]);
  await expectPath('/dashboard');
  expect(screen.getByTestId('auth-status').textContent).toBe('authenticated');
});

test('future sidebar items indicate unavailability and have no interactive target', async () => {
  showApp('/login');
  await signIn();
  const navigation = screen.getByRole('navigation', { name: 'Κύρια πλοήγηση' });
  expect(within(navigation).getAllByText('Μη διαθέσιμο ακόμη')).toHaveLength(5);
  expect(within(navigation).getAllByRole('list')).toHaveLength(1);
  expect(within(navigation).getAllByRole('listitem')).toHaveLength(6);
  for (const label of ['Ασθενείς', 'Ραντεβού', 'Ημερολόγιο', 'Πληρωμές', 'Ρυθμίσεις']) {
    const item = within(navigation).getByText(label).closest('li')!;
    expect(within(item).getByText('Μη διαθέσιμο ακόμη')).toBeTruthy();
    expect(item.querySelector('a, button, input, [href], [tabindex], [role="link"], [role="button"]'))
      .toBeNull();
    fireEvent.click(within(item).getByText(label));
    await expectPath('/dashboard');
  }
});
