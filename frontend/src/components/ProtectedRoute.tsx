import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Spinner from './Spinner';
import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  /** When true (default), requires admin role. When false, any logged-in user is allowed. */
  requireAdmin?: boolean;
}

export default function ProtectedRoute({ children, requireAdmin = true }: Props) {
  const { isAdmin, isLoggedIn, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Spinner text="Checking session…" />
      </div>
    );
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  if (!requireAdmin && !isLoggedIn) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
