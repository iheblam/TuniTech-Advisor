import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import RecommendPage from './pages/RecommendPage';
import PredictPage from './pages/PredictPage';
import SearchPage from './pages/SearchPage';
import ComparePage from './pages/ComparePage';
import LoginPage from './pages/LoginPage';
import UserLoginPage from './pages/UserLoginPage';
import RegisterPage from './pages/RegisterPage';
import AdminPage from './pages/AdminPage';
import ProfilePage from './pages/ProfilePage';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/recommend" element={<RecommendPage />} />
              <Route path="/predict" element={<PredictPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/compare" element={<ComparePage />} />
              {/* User auth */}
              <Route path="/login" element={<UserLoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              {/* User profile */}
              <Route path="/profile" element={
                <ProtectedRoute requireAdmin={false}>
                  <ProfilePage />
                </ProtectedRoute>
              } />
              {/* Admin (URL known only to admins – no link in UI) */}
              <Route path="/admin/login" element={<LoginPage />} />
              <Route path="/admin" element={
                <ProtectedRoute>
                  <AdminPage />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
          <Footer />
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
