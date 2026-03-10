import { useState, useEffect, useRef } from 'react';
import { NavLink, useNavigate, Link, useLocation } from 'react-router-dom';
import { Smartphone, BarChart2, Search, Cpu, GitCompare, LogOut, UserCircle, Settings, TrendingUp, LayoutDashboard, Flame, Wallet, Target, Menu, X, ChevronDown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const categories = [
  {
    label: 'Explore',
    links: [
      { to: '/recommend', label: 'Recommend',  icon: <BarChart2 size={15} />,   desc: 'Get personalized picks' },
      { to: '/predict',   label: 'Predictor',  icon: <Cpu size={15} />,         desc: 'Predict phone prices' },
      { to: '/search',    label: 'Search',     icon: <Search size={15} />,      desc: 'Find any smartphone' },
      { to: '/compare',   label: 'Compare',    icon: <GitCompare size={15} />,  desc: 'Side-by-side comparison' },
    ],
  },
  {
    label: 'Tools',
    links: [
      { to: '/trending',  label: 'Trending',   icon: <Flame size={15} />,       desc: 'Hottest phones right now' },
      { to: '/budget',    label: 'Budget',     icon: <Wallet size={15} />,      desc: 'Optimize your budget' },
      { to: '/use-case',  label: 'For Me',     icon: <Target size={15} />,      desc: 'Match your lifestyle' },
    ],
  },
  {
    label: 'Analytics',
    links: [
      { to: '/brands',    label: 'Brands',     icon: <TrendingUp size={15} />,    desc: 'Brand performance data' },
      { to: '/market',    label: 'Market',     icon: <LayoutDashboard size={15} />, desc: 'Market overview' },
    ],
  },
];



/** Fallback DiceBear avatar seeded from username */
const fallbackAvatar = (username: string) =>
  `https://api.dicebear.com/7.x/fun-emoji/svg?seed=${encodeURIComponent(username)}`;

/** Single category dropdown */
function CategoryMenu({ label, links }: { label: string; links: typeof categories[0]['links'] }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const location = useLocation();
  const isAnyActive = links.some(l => location.pathname === l.to || location.pathname.startsWith(l.to + '/'));

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Close on route change
  useEffect(() => { setOpen(false); }, [location.pathname]);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(v => !v)}
        className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all select-none ${
          isAnyActive
            ? 'bg-primary-50 text-primary-700 font-semibold'
            : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
        }`}
      >
        {label}
        <ChevronDown size={13} className={`transition-transform duration-150 ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <div className="absolute top-full left-0 mt-1.5 w-52 bg-white rounded-xl shadow-lg border border-neutral-100 py-1.5 z-50 animate-in fade-in slide-in-from-top-1 duration-100">
          {links.map(l => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `flex items-start gap-3 px-3 py-2.5 mx-1 rounded-lg transition-all ${
                  isActive ? 'bg-primary-50 text-primary-700' : 'text-neutral-700 hover:bg-neutral-50'
                }`
              }
            >
              <span className="mt-0.5 shrink-0 text-primary-500">{l.icon}</span>
              <span>
                <span className="block text-sm font-medium leading-tight">{l.label}</span>
                <span className="block text-xs text-neutral-400 mt-0.5">{l.desc}</span>
              </span>
            </NavLink>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Navbar() {
  const { isAdmin, isLoggedIn, user, avatar, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [mobileOpenCats, setMobileOpenCats] = useState<Record<string, boolean>>({});

  // Close drawer on route change
  useEffect(() => { setMobileOpen(false); setMobileOpenCats({}); }, [location.pathname]);

  const handleLogout = () => { logout(); navigate('/'); };
  const displayAvatar = avatar || (user ? fallbackAvatar(user.username) : undefined);

  return (
    <>
      <nav className="sticky top-0 z-50 bg-cozy-card/95 backdrop-blur-sm border-b border-cozy-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between py-2.5">

          {/* Brand */}
          <NavLink to="/" className="flex items-center gap-2 font-extrabold text-xl text-neutral-900">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shadow-sm">
              <Smartphone className="text-white" size={17} />
            </div>
            <span className="hidden sm:inline">TuniTech<span className="text-primary-600">Advisor</span></span>
            <span className="sm:hidden">T<span className="text-primary-600">A</span></span>
          </NavLink>

          {/* Desktop – Home + category dropdowns */}
          <div className="hidden lg:flex items-center gap-0.5">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive ? 'bg-primary-50 text-primary-700 font-semibold' : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                }`
              }
            >
              <Smartphone size={15} />
              Home
            </NavLink>

            {categories.map(cat => (
              <CategoryMenu key={cat.label} label={cat.label} links={cat.links} />
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

          {/* Mobile hamburger button */}
          <button
            className="lg:hidden p-2 rounded-lg text-neutral-600 hover:bg-neutral-100 transition-colors"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </nav>

      {/* Mobile drawer overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-black/30 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      {/* Mobile slide-out drawer */}
      <div
        className={`fixed top-0 right-0 z-50 h-full w-72 max-w-[85vw] bg-cozy-card shadow-2xl transform transition-transform duration-200 ease-in-out lg:hidden ${
          mobileOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-cozy-border">
          <span className="font-extrabold text-lg text-neutral-900">Menu</span>
          <button onClick={() => setMobileOpen(false)} className="p-2 rounded-lg text-neutral-500 hover:bg-neutral-100">
            <X size={20} />
          </button>
        </div>

        <div className="overflow-y-auto h-[calc(100%-60px)] py-2">
          {/* Nav links grouped by category */}
          <div className="px-2">
            {/* Home */}
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive ? 'bg-primary-50 text-primary-700 font-semibold' : 'text-neutral-600 hover:bg-neutral-100'
                }`
              }
            >
              <Smartphone size={15} />
              Home
            </NavLink>

            {categories.map(cat => (
              <div key={cat.label} className="mt-2">
                <button
                  onClick={() => setMobileOpenCats(prev => ({ ...prev, [cat.label]: !prev[cat.label] }))}
                  className="flex items-center justify-between w-full px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-neutral-400 hover:text-neutral-600"
                >
                  {cat.label}
                  <ChevronDown size={12} className={`transition-transform duration-150 ${mobileOpenCats[cat.label] ? 'rotate-180' : ''}`} />
                </button>
                {mobileOpenCats[cat.label] && (
                  <div className="space-y-0.5 mt-0.5">
                    {cat.links.map(l => (
                      <NavLink
                        key={l.to}
                        to={l.to}
                        className={({ isActive }) =>
                          `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                            isActive ? 'bg-primary-50 text-primary-700 font-semibold' : 'text-neutral-600 hover:bg-neutral-100'
                          }`
                        }
                      >
                        <span className="text-primary-400">{l.icon}</span>
                        {l.label}
                      </NavLink>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Auth section */}
          <div className="mt-3 pt-3 mx-4 border-t border-neutral-200">
            {isLoggedIn ? (
              <div className="space-y-2">
                {isAdmin ? (
                  <NavLink
                    to="/admin"
                    className={({ isActive }) =>
                      `flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                        isActive ? 'bg-accent-100 text-accent-700' : 'text-accent-600 hover:bg-accent-50'
                      }`
                    }
                  >
                    <UserCircle size={16} />
                    {user?.username} (Admin)
                  </NavLink>
                ) : (
                  <Link
                    to="/profile"
                    className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold text-neutral-700 hover:bg-neutral-100"
                  >
                    <div className="w-7 h-7 rounded-full overflow-hidden border-2 border-primary-200 shrink-0">
                      {displayAvatar
                        ? <img src={displayAvatar} alt={user?.username} className="w-full h-full object-cover" />
                        : <div className="w-full h-full bg-primary-100 flex items-center justify-center">
                            <UserCircle size={15} className="text-primary-500" />
                          </div>
                      }
                    </div>
                    <span>{user?.username}</span>
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-all"
                >
                  <LogOut size={15} />
                  Logout
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <Link to="/login" className="block w-full text-center px-3 py-2.5 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-100 transition-all">
                  Sign In
                </Link>
                <Link to="/register" className="block w-full text-center px-4 py-2.5 rounded-xl text-sm font-semibold bg-primary-600 text-white hover:bg-primary-700 transition-all shadow-sm">
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
