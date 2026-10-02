import type { PropsWithChildren } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './useAuth.js';

// UI protection only; the backend remains authoritative for data access.
export function ProtectedRoute({ children }: PropsWithChildren) {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated || !user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
