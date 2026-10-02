import { useEffect, useRef } from 'react';
import { useAuth } from '../auth/useAuth.js';

// Temporary destination until FRONTEND-01F introduces the dashboard.
export function DashboardPage() {
  const { user, logout } = useAuth();
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, []);

  if (!user) return null;
  return (
    <main aria-labelledby="dashboard-heading">
      <h1 id="dashboard-heading" ref={heading} tabIndex={-1}>Dashboard</h1>
      <p>{user.full_name}</p>
      <p>{user.email}</p>
      <button className="button" type="button" onClick={logout}>Αποσύνδεση</button>
    </main>
  );
}
