import { useEffect, useRef } from 'react';
import { useAuth } from './auth/useAuth.js';
import { LoginPage } from './pages/LoginPage.js';

export default function App() {
  const { user, isAuthenticated, logout } = useAuth();
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (isAuthenticated) heading.current?.focus();
  }, [isAuthenticated]);

  if (!isAuthenticated || !user) return <LoginPage />;

  // Temporary account confirmation until protected routing is introduced.
  return (
    <main className="login-viewport">
      <section className="login-card" aria-labelledby="account-heading">
        <h1 id="account-heading" className="login-heading" ref={heading} tabIndex={-1}>
          Συνδεθήκατε επιτυχώς.
        </h1>
        <div className="account-details">
          <p>{user.full_name}</p>
          <p className="account-email">{user.email}</p>
        </div>
        <button className="button" type="button" onClick={logout}>Αποσύνδεση</button>
      </section>
    </main>
  );
}
