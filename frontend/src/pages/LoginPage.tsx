import { useState } from 'react';
import type { FormEvent } from 'react';
import { ApiError } from '../api/client.js';
import { useAuth } from '../auth/useAuth.js';
import './LoginPage.css';

function loginErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.kind) {
      case 'authentication': return 'Λανθασμένο email ή κωδικός.';
      case 'forbidden': return 'Ο λογαριασμός σας είναι ανενεργός.';
      case 'network': return 'Δεν ήταν δυνατή η σύνδεση. Ελέγξτε τη σύνδεσή σας στο διαδίκτυο και δοκιμάστε ξανά.';
      case 'server': return 'Παρουσιάστηκε προσωρινό πρόβλημα στον διακομιστή. Δοκιμάστε ξανά αργότερα.';
    }
  }
  return 'Δεν ήταν δυνατή η σύνδεση. Δοκιμάστε ξανά.';
}

export function LoginPage() {
  const { login, status } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const authenticating = status === 'authenticating';

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (authenticating) return;
    setError(null);
    try {
      await login({ email, password });
    } catch (failure) {
      setError(loginErrorMessage(failure));
    } finally {
      setPassword('');
    }
  }

  return (
    <main className="login-viewport">
      <section className="login-card" aria-labelledby="login-heading">
        <h1 id="login-heading" className="login-heading">Σύνδεση</h1>
        <p className="login-subtitle">Συνδεθείτε για να συνεχίσετε.</p>
        <form className="login-form" onSubmit={handleSubmit} aria-busy={authenticating}>
          <div className="form-field">
            <label htmlFor="login-email">Email</label>
            <input id="login-email" name="email" className="form-input" type="email"
              required autoComplete="email" value={email} disabled={authenticating}
              onChange={(event) => setEmail(event.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="login-password">Κωδικός</label>
            <input id="login-password" name="password" className="form-input" type="password"
              required autoComplete="current-password" value={password} disabled={authenticating}
              onChange={(event) => setPassword(event.target.value)} />
          </div>
          {error && <p className="login-error" role="alert">{error}</p>}
          <button className="button" type="submit" disabled={authenticating}>
            {authenticating ? 'Σύνδεση...' : 'Σύνδεση'}
          </button>
        </form>
      </section>
    </main>
  );
}
