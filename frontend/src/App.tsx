import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import RecommendPage from './pages/RecommendPage';
import PredictPage from './pages/PredictPage';
import SearchPage from './pages/SearchPage';
import ComparePage from './pages/ComparePage';
import UserLoginPage from './pages/UserLoginPage';
import RegisterPage from './pages/RegisterPage';
import AdminPage from './pages/AdminPage';
import ProfilePage from './pages/ProfilePage';
import BrandAnalyticsPage from './pages/BrandAnalyticsPage';
import MarketDashboardPage from './pages/MarketDashboardPage';
import BudgetOptimizerPage from './pages/BudgetOptimizerPage';
import UseCasePage from './pages/UseCasePage';
import TrendingPage from './pages/TrendingPage';
import ProtectedRoute from './components/ProtectedRoute';
import RequireLogin from './components/RequireLogin';
import PhoneReviewPrompt from './components/PhoneReviewPrompt';
import { AuthProvider } from './context/AuthContext';

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              {/* ── Public routes (no login needed) ── */}
              <Route path="/login" element={<UserLoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/admin/login" element={<Navigate to="/login" replace />} />

              {/* ── All other routes require login ── */}
              <Route element={<RequireLogin />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/recommend" element={<RecommendPage />} />
                <Route path="/predict" element={<PredictPage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/compare" element={<ComparePage />} />
                <Route path="/brands" element={<BrandAnalyticsPage />} />
                <Route path="/market" element={<MarketDashboardPage />} />
                <Route path="/trending" element={<TrendingPage />} />
                <Route path="/budget" element={<BudgetOptimizerPage />} />
                <Route path="/use-case" element={<UseCasePage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/admin" element={
                  <ProtectedRoute>
                    <AdminPage />
                  </ProtectedRoute>
                } />
              </Route>
            </Routes>
          </main>
          <Footer />
          <PhoneReviewPrompt />
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
