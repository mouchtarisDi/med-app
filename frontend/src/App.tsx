import { Navigate, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from './auth/ProtectedRoute.js';
import { useAuth } from './auth/useAuth.js';
import { DashboardPage } from './pages/DashboardPage.js';
import { LoginPage } from './pages/LoginPage.js';

export default function App() {
  const { isAuthenticated } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={isAuthenticated
        ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
      <Route path="/dashboard" element={
        <ProtectedRoute><DashboardPage /></ProtectedRoute>
      } />
      <Route path="*" element={
        <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />
      } />
    </Routes>
  );
}
