import { StrictMode } from 'react';
import type { PropsWithChildren } from 'react';
import { act, renderHook } from '@testing-library/react';
import { beforeEach, expect, test, vi } from 'vitest';
import { getCurrentUser, login as apiLogin } from '../src/api/auth.js';
import { ApiError } from '../src/api/client.js';
import { AuthProvider } from '../src/auth/AuthProvider.js';
import { useAuth } from '../src/auth/useAuth.js';

vi.mock('../src/api/auth.js', () => ({ login: vi.fn(), getCurrentUser: vi.fn() }));
const loginMock = vi.mocked(apiLogin);
const meMock = vi.mocked(getCurrentUser);
const credentials = { email: 'test@example.com', password: 'synthetic-password' };
const token = { access_token: 'synthetic-token', token_type: 'bearer' as const };
const user = { email: credentials.email, full_name: 'Test User', id: 42 };
const wrapper = ({ children }: PropsWithChildren) => (
  <StrictMode><AuthProvider>{children}</AuthProvider></StrictMode>
);

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
}

function expectIdle(value: ReturnType<typeof useAuth>) {
  expect(value.status).toBe('idle');
  expect(value.user).toBeNull();
  expect(value.isAuthenticated).toBe(false);
}

beforeEach(() => {
  vi.resetAllMocks();
  loginMock.mockResolvedValue(token);
  meMock.mockResolvedValue(user);
});

test('initial state is idle and performs no API requests', () => {
  const { result } = renderHook(useAuth, { wrapper });
  expectIdle(result.current);
  expect(loginMock).not.toHaveBeenCalled();
  expect(meMock).not.toHaveBeenCalled();
});

test('login happens first; authentication waits for current user', async () => {
  const loginResponse = deferred<typeof token>();
  const meResponse = deferred<typeof user>();
  loginMock.mockReturnValue(loginResponse.promise);
  meMock.mockReturnValue(meResponse.promise);
  const { result } = renderHook(useAuth, { wrapper });
  let operation!: Promise<void>;
  await act(async () => { operation = result.current.login(credentials); });
  expect(loginMock).toHaveBeenCalledWith(credentials);
  expect(meMock).not.toHaveBeenCalled();
  expect(result.current.status).toBe('authenticating');
  await act(async () => { loginResponse.resolve(token); });
  expect(meMock).toHaveBeenCalledWith(token.access_token);
  expect(result.current.status).toBe('authenticating');
  expect(result.current.user).toBeNull();
  expect(result.current.isAuthenticated).toBe(false);
  await act(async () => { meResponse.resolve(user); await operation; });
  expect(result.current.status).toBe('authenticated');
  expect(result.current.user).toEqual(user);
  expect(result.current.isAuthenticated).toBe(true);
  expect(Object.keys(result.current).sort()).toEqual(['isAuthenticated', 'login', 'logout', 'status', 'user']);
});

test('login API failure clears state and rethrows the same error', async () => {
  const error = new ApiError('authentication', 401);
  loginMock.mockRejectedValue(error);
  const { result } = renderHook(useAuth, { wrapper });
  await act(async () => { await expect(result.current.login(credentials)).rejects.toBe(error); });
  expectIdle(result.current);
  expect(meMock).not.toHaveBeenCalled();
});

test.each([
  new ApiError('authentication', 401),
  new ApiError('forbidden', 403),
  new ApiError('server', 500),
  new ApiError('network', null),
  new ApiError('response', 200),
])('current-user failure ($kind) clears state and preserves error', async (error) => {
  meMock.mockRejectedValue(error);
  const { result } = renderHook(useAuth, { wrapper });
  await act(async () => { await expect(result.current.login(credentials)).rejects.toBe(error); });
  expectIdle(result.current);
});

test('logout clears authenticated state without a backend request', async () => {
  const { result } = renderHook(useAuth, { wrapper });
  await act(async () => { await result.current.login(credentials); });
  act(() => result.current.logout());
  expectIdle(result.current);
  expect(loginMock).toHaveBeenCalledTimes(1);
  expect(meMock).toHaveBeenCalledTimes(1);
});

test('failed re-login does not retain the old authenticated user', async () => {
  const { result } = renderHook(useAuth, { wrapper });
  await act(async () => { await result.current.login(credentials); });
  const pending = deferred<typeof token>();
  loginMock.mockReturnValueOnce(pending.promise);
  const error = new ApiError('forbidden', 403);
  meMock.mockRejectedValueOnce(error);
  let operation!: Promise<void>;
  await act(async () => { operation = result.current.login(credentials); });
  expect(result.current.status).toBe('authenticating');
  expect(result.current.user).toBeNull();
  await act(async () => {
    pending.resolve(token);
    await expect(operation).rejects.toBe(error);
  });
  expectIdle(result.current);
});

test('simultaneous login calls reuse the same request chain', async () => {
  const pending = deferred<typeof user>();
  meMock.mockReturnValue(pending.promise);
  const { result } = renderHook(useAuth, { wrapper });
  let first!: Promise<void>;
  let second!: Promise<void>;
  await act(async () => {
    first = result.current.login(credentials);
    second = result.current.login(credentials);
  });
  expect(first).toBe(second);
  expect(loginMock).toHaveBeenCalledTimes(1);
  expect(meMock).toHaveBeenCalledTimes(1);
  await act(async () => { pending.resolve(user); await first; });
});

test.each(['login', 'me'])('logout during pending %s prevents late authentication', async (stage) => {
  const pendingLogin = deferred<typeof token>();
  const pendingMe = deferred<typeof user>();
  if (stage === 'login') loginMock.mockReturnValue(pendingLogin.promise);
  else meMock.mockReturnValue(pendingMe.promise);
  const { result } = renderHook(useAuth, { wrapper });
  let operation!: Promise<void>;
  await act(async () => { operation = result.current.login(credentials); });
  act(() => result.current.logout());
  expectIdle(result.current);
  await act(async () => {
    pendingLogin.resolve(token);
    pendingMe.resolve(user);
    await operation;
  });
  expectIdle(result.current);
  if (stage === 'login') expect(meMock).not.toHaveBeenCalled();
});

test('a late old result cannot replace a newer login after logout', async () => {
  const oldMe = deferred<typeof user>();
  meMock.mockReturnValueOnce(oldMe.promise);
  const { result } = renderHook(useAuth, { wrapper });
  let oldOperation!: Promise<void>;
  await act(async () => { oldOperation = result.current.login(credentials); });
  act(() => result.current.logout());
  const newUser = { ...user, id: 43 };
  meMock.mockResolvedValueOnce(newUser);
  await act(async () => { await result.current.login(credentials); });
  await act(async () => { oldMe.resolve(user); await oldOperation; });
  expect(result.current.user).toEqual(newUser);
  expect(result.current.isAuthenticated).toBe(true);
});

test('useAuth outside provider throws a clear error', () => {
  const stderr = vi.spyOn(console, 'error').mockImplementation(() => {});
  try {
    expect(() => renderHook(useAuth)).toThrow('useAuth must be used within AuthProvider');
  } finally {
    stderr.mockRestore();
  }
});
