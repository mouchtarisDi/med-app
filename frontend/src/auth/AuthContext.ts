import { createContext } from 'react';
import type { CurrentUser, LoginCredentials } from '../types/auth.js';

export interface AuthContextValue {
  user: CurrentUser | null;
  status: 'idle' | 'authenticating' | 'authenticated';
  isAuthenticated: boolean;
  login(credentials: LoginCredentials): Promise<void>;
  logout(): void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
