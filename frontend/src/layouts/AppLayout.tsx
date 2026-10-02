import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../auth/useAuth.js';
import './AppLayout.css';

const futureItems = ['Ασθενείς', 'Ραντεβού', 'Ημερολόγιο', 'Πληρωμές', 'Ρυθμίσεις'];

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-layout">
      <a className="app-skip-link" href="#app-content">Μετάβαση στο περιεχόμενο</a>
      <aside className="app-sidebar" aria-label="Πλαϊνή μπάρα">
        <p className="app-brand">Medical Practice</p>
        <nav aria-label="Κύρια πλοήγηση">
          <ul className="app-nav-list">
            <li><NavLink className="app-nav-link" to="/dashboard" end>Dashboard</NavLink></li>
            {futureItems.map((label) => (
              <li className="app-nav-unavailable" key={label}>
                <span>{label}</span>
                <span className="app-nav-availability">Μη διαθέσιμο ακόμη</span>
              </li>
            ))}
          </ul>
        </nav>
        <div className="app-account">
          <p className="app-account-name">{user?.full_name}</p>
          <p className="app-account-email">{user?.email}</p>
          <button className="button" type="button" onClick={logout}>Αποσύνδεση</button>
        </div>
      </aside>
      <main id="app-content" className="app-content" tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  );
}
