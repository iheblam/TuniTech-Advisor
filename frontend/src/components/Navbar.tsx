import { NavLink, useNavigate, Link } from 'react-router-dom';
import { Smartphone, BarChart2, Search, Cpu, GitCompare, LogOut, UserCircle, Settings, TrendingUp, LayoutDashboard, Flame, Wallet, Target } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const links = [
  { to: '/',          label: 'Home',      icon: <Smartphone size={15} /> },
  { to: '/recommend', label: 'Recommend', icon: <BarChart2 size={15} /> },
  { to: '/predict',   label: 'Predictor', icon: <Cpu size={15} /> },
  { to: '/search',    label: 'Search',    icon: <Search size={15} /> },
  { to: '/compare',   label: 'Compare',   icon: <GitCompare size={15} /> },
  { to: '/trending',  label: 'Trending',  icon: <Flame size={15} /> },
  { to: '/budget',    label: 'Budget',    icon: <Wallet size={15} /> },
  { to: '/use-case',  label: 'For Me',    icon: <Target size={15} /> },
  { to: '/brands',    label: 'Brands',    icon: <TrendingUp size={15} /> },
  { to: '/market',    label: 'Market',    icon: <LayoutDashboard size={15} /> },
];

/** Fallback DiceBear avatar seeded from username */
const fallbackAvatar = (username: string) =>
  `https://api.dicebear.com/7.x/fun-emoji/svg?seed=${encodeURIComponent(username)}`;

export default function Navbar() {
  const { isAdmin, isLoggedIn, user, avatar, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/'); };
  const displayAvatar = avatar || (user ? fallbackAvatar(user.username) : undefined);

  return (
    <nav className="sticky top-0 z-50 bg-cozy-card/95 backdrop-blur-sm border-b border-cozy-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between py-2.5">

        {/* Brand */}
        <NavLink to="/" className="flex items-center gap-2 font-extrabold text-xl text-neutral-900">
          <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shadow-sm">
            <Smartphone className="text-white" size={17} />
          </div>
          TuniTech<span className="text-primary-600">Advisor</span>
        </NavLink>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-0.5">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 font-semibold'
                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                }`
              }
            >
              {l.icon}
              {l.label}
            </NavLink>
          ))}

          {/* Auth */}
          <div className="ml-3 pl-3 border-l border-neutral-200 flex items-center gap-1.5">
            {isLoggedIn ? (
              <>
                {isAdmin ? (
                  <NavLink
                    to="/admin"
                    className={({ isActive }) =>
                      `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold transition-all ${
                        isActive ? 'bg-accent-100 text-accent-700' : 'text-accent-600 hover:bg-accent-50'
                      }`
                    }
                  >
                    <UserCircle size={16} />
                    {user?.username}
                  </NavLink>
                ) : (
                  <Link
                    to="/profile"
                    className="flex items-center gap-2 px-2.5 py-1.5 rounded-xl text-sm font-semibold text-neutral-700 hover:bg-neutral-100 transition-all group"
                    title="Account Settings"
                  >
                    <div className="w-7 h-7 rounded-full overflow-hidden border-2 border-primary-200 group-hover:border-primary-400 transition-colors shrink-0">
                      {displayAvatar
                        ? <img src={displayAvatar} alt={user?.username} className="w-full h-full object-cover" />
                        : <div className="w-full h-full bg-primary-100 flex items-center justify-center">
                            <UserCircle size={16} className="text-primary-500" />
                          </div>
                      }
                    </div>
                    <span>{user?.username}</span>
                    <Settings size={13} className="text-neutral-400 group-hover:text-primary-500 transition-colors" />
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-lg text-neutral-400 hover:text-red-500 hover:bg-red-50 transition-all"
                  title="Logout"
                >
                  <LogOut size={15} />
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="px-3 py-2 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 transition-all">
                  Sign In
                </Link>
                <Link to="/register" className="px-4 py-2 rounded-xl text-sm font-semibold bg-primary-600 text-white hover:bg-primary-700 transition-all shadow-sm">
                  Register
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Mobile */}
        <div className="md:hidden flex items-center gap-1">
          {links.slice(1).map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `p-2 rounded-lg transition-colors ${isActive ? 'text-primary-600 bg-primary-50' : 'text-neutral-500'}`
              }
            >
              {l.icon}
            </NavLink>
          ))}
          {isLoggedIn ? (
            <>
              <Link to="/profile" className="p-1">
                <div className="w-7 h-7 rounded-full overflow-hidden border-2 border-primary-200">
                  {displayAvatar
                    ? <img src={displayAvatar} alt="avatar" className="w-full h-full object-cover" />
                    : <div className="w-full h-full bg-primary-100 flex items-center justify-center">
                        <UserCircle size={15} className="text-primary-500" />
                      </div>
                  }
                </div>
              </Link>
              <button onClick={handleLogout} className="p-2 rounded-lg text-neutral-500">
                <LogOut size={18} />
              </button>
            </>
          ) : (
            <Link to="/login" className="p-2 rounded-lg text-primary-500">
              <UserCircle size={18} />
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
