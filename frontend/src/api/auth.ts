import { apiRequest } from './client.js';
import type { CurrentUser, LoginCredentials, TokenResponse } from '../types/auth.js';

export function login(credentials: LoginCredentials): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      username: credentials.email,
      password: credentials.password,
    }),
  });
}

export function getCurrentUser(token: string): Promise<CurrentUser> {
  return apiRequest<CurrentUser>('/auth/me', {
    method: 'GET',
    headers: { Authorization: `Bearer ${token}` },
  });
}
