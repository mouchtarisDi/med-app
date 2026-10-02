import { fireEvent, render, screen, waitFor } from '@testing-library/react';
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
});

test('successful login redirects to /dashboard and displays the current user', async () => {
  showApp('/login');
  await signIn();
  expect(loginMock).toHaveBeenCalledWith(credentials);
  expect(meMock).toHaveBeenCalledWith(token.access_token);
  expect(screen.getByText(user.full_name)).toBeTruthy();
  expect(screen.getByText(user.email)).toBeTruthy();
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
