import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { loginAdmin, loginUser, registerUser, getMe, getProfile } from '../api/client';
import type { RegisterPayload } from '../types';

interface AppUser {
  username: string;
  role: 'admin' | 'user';
}

interface AuthContextValue {
  user: AppUser | null;
  token: string | null;
  loading: boolean;
  /** Current user's avatar URL (preset or undefined) */
  avatar: string | undefined;
  /** Update avatar in context (called after profile save) */
  setAvatar: (url: string | undefined) => void;
  /** Admin login (used by /admin/login page) */
  login: (username: string, password: string) => Promise<void>;
  /** Regular user login */
  userLogin: (username: string, password: string) => Promise<void>;
  /** Unified login – tries user first, falls back to admin. Returns the role. */
  unifiedLogin: (username: string, password: string) => Promise<'user' | 'admin'>;
  /** Register a new user account */
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  isAdmin: boolean;
  isLoggedIn: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = 'tunitech_token';
const AVATAR_KEY = 'tunitech_avatar';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true);
  const [avatar, _setAvatar] = useState<string | undefined>(
    () => localStorage.getItem(AVATAR_KEY) ?? undefined
  );

  const setAvatar = (url: string | undefined) => {
    _setAvatar(url);
    if (url) localStorage.setItem(AVATAR_KEY, url);
    else localStorage.removeItem(AVATAR_KEY);
  };

  // Restore session on mount
  useEffect(() => {
    const restore = async () => {
      const stored = localStorage.getItem(TOKEN_KEY);
      if (!stored) { setLoading(false); return; }
      try {
        const me = await getMe(stored);
        setUser({ username: me.username, role: me.role as 'admin' | 'user' });
        setToken(stored);
        // Also fetch avatar for regular users
        if (me.role === 'user') {
          try {
            const profile = await getProfile(stored);
            setAvatar(profile.avatar ?? undefined);
          } catch { /* avatar fetch is non-critical */ }
        }
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
      } finally {
        setLoading(false);
      }
    };
    restore();
  }, []);

  const _applyToken = (data: { access_token: string; username: string; role: string }) => {
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    setUser({ username: data.username, role: data.role as 'admin' | 'user' });
  };

  /** Admin login */
  const login = async (username: string, password: string) => {
    const data = await loginAdmin(username, password);
    _applyToken(data);
  };

  /** Regular user login – also fetches avatar */
  const userLogin = async (username: string, password: string) => {
    const data = await loginUser(username, password);
    _applyToken(data);
    try {
      const profile = await getProfile(data.access_token);
      setAvatar(profile.avatar ?? undefined);
    } catch { /* non-critical */ }
  };

  /** Unified login: tries user first, falls back to admin. Returns the role. */
  const unifiedLogin = async (username: string, password: string): Promise<'user' | 'admin'> => {
    try {
      const data = await loginUser(username, password);
      _applyToken(data);
      try {
        const profile = await getProfile(data.access_token);
        setAvatar(profile.avatar ?? undefined);
      } catch { /* non-critical */ }
      return 'user';
    } catch {
      // fallback: try admin login
      const data = await loginAdmin(username, password);
      _applyToken(data);
      return 'admin';
    }
  };

  /** Register + auto-login */
  const register = async (payload: RegisterPayload) => {
    const data = await registerUser(payload);
    _applyToken(data);
    if (payload.avatar) setAvatar(payload.avatar);
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(AVATAR_KEY);
    setToken(null);
    setUser(null);
    _setAvatar(undefined);
  };

  return (
    <AuthContext.Provider value={{
      user, token, loading,
      avatar, setAvatar,
      login, userLogin, unifiedLogin, register, logout,
      isAdmin: user?.role === 'admin',
      isLoggedIn: !!user,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
