import { useEffect, useRef } from 'react';
import { useAuth } from '../auth/useAuth.js';

// Dashboard functionality will be added when operational data is available.
export function DashboardPage() {
  const { user } = useAuth();
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, []);

  return (
    <section aria-labelledby="dashboard-heading">
      <h1 id="dashboard-heading" ref={heading} tabIndex={-1}>Dashboard</h1>
      <p>Καλώς ήρθες, {user?.full_name}.</p>
    </section>
  );
}
