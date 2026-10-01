import { useCallback, useEffect, useRef, useState } from 'react';
import type { PropsWithChildren } from 'react';
import { getCurrentUser, login as apiLogin } from '../api/auth.js';
import type { CurrentUser, LoginCredentials } from '../types/auth.js';
import { AuthContext } from './AuthContext.js';

type AuthState =
  | { status: 'idle' | 'authenticating'; token: null; user: null }
  | { status: 'authenticated'; token: string; user: CurrentUser };

const idle: AuthState = { status: 'idle', token: null, user: null };

export function AuthProvider({ children }: PropsWithChildren) {
  const [state, setState] = useState<AuthState>(idle);
  const pending = useRef<{ id: symbol; promise: Promise<void> } | null>(null);

  useEffect(() => () => { pending.current = null; }, []);

  const logout = useCallback(() => {
    pending.current = null;
    setState(idle);
  }, []);

  const login = useCallback((credentials: LoginCredentials): Promise<void> => {
    if (pending.current) return pending.current.promise;

    setState({ status: 'authenticating', token: null, user: null });
    const id = Symbol('login');
    // Defer execution until the shared pending operation is registered.
    const promise = Promise.resolve().then(async () => {
      try {
        if (pending.current?.id !== id) return;
        const tokenResponse = await apiLogin(credentials);
        if (pending.current?.id !== id) return;
        const user = await getCurrentUser(tokenResponse.access_token);
        if (pending.current?.id === id) {
          setState({ status: 'authenticated', token: tokenResponse.access_token, user });
        }
      } catch (error) {
        if (pending.current?.id === id) setState(idle);
        throw error;
      } finally {
        if (pending.current?.id === id) pending.current = null;
      }
    });
    pending.current = { id, promise };
    return promise;
  }, []);

  return (
    <AuthContext.Provider value={{
      user: state.user,
      status: state.status,
      isAuthenticated: state.status === 'authenticated',
      login,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}
