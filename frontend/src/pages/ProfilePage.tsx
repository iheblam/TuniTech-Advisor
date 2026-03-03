import { useState, useEffect, FormEvent } from 'react';
import {
  User, Mail, Hash, Briefcase, Heart, Phone,
  HelpCircle, Save, Lock, Eye, EyeOff, CheckCircle,
  AlertCircle, Settings,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getProfile, updateProfile, changePassword } from '../api/client';
import type { UserProfile, Occupation, JoinReason } from '../types';
import AvatarPicker from '../components/AvatarPicker';

// ── Constants (mirrored from RegisterPage) ─────────────────────────────────
const OCCUPATIONS: { value: Occupation; label: string }[] = [
  { value: 'student',       label: '🎓 Student' },
  { value: 'employee',      label: '💼 Employee' },
  { value: 'freelancer',    label: '💻 Freelancer' },
  { value: 'self_employed', label: '🏢 Self-employed' },
  { value: 'other',         label: '✨ Other' },
];

const JOIN_REASONS: { value: JoinReason; label: string; desc: string }[] = [
  { value: 'searching_phone',  label: 'Searching for a phone',  desc: 'I want to find my next device' },
  { value: 'comparing_prices', label: 'Comparing prices',       desc: 'I want the best deal across stores' },
  { value: 'reading_reviews',  label: 'Reading reviews',        desc: 'I want community opinions' },
  { value: 'browsing',         label: 'Just browsing',          desc: "Exploring what's available" },
];

const BRANDS = ['Samsung', 'Apple', 'Huawei', 'Xiaomi', 'Oppo', 'Realme', 'OnePlus', 'Nokia', 'Sony', 'Other'];

// ── Toast helper ────────────────────────────────────────────────────────────
function Toast({ type, msg }: { type: 'success' | 'error'; msg: string }) {
  return (
    <div className={`flex items-center gap-2 px-4 py-3 rounded-lg text-sm
      ${type === 'success'
        ? 'bg-green-50 border border-green-200 text-green-700'
        : 'bg-red-50 border border-red-200 text-red-700'}`}
    >
      {type === 'success'
        ? <CheckCircle size={15} className="shrink-0" />
        : <AlertCircle size={15} className="shrink-0" />}
      {msg}
    </div>
  );
}

// ── Component ───────────────────────────────────────────────────────────────
export default function ProfilePage() {
  const { token, setAvatar: setContextAvatar } = useAuth();

  const [profile, setProfile]   = useState<UserProfile | null>(null);
  const [loadErr, setLoadErr]   = useState('');

  // Profile form state
  const [avatar, setAvatar]           = useState<string | undefined>(undefined);
  const [email, setEmail]             = useState('');
  const [age, setAge]                 = useState('');
  const [occupation, setOccupation]   = useState<Occupation | ''>('');
  const [favBrand, setFavBrand]       = useState('');
  const [currentPhone, setCurrentPhone] = useState('');
  const [joinReason, setJoinReason]   = useState<JoinReason | ''>('');

  // Profile save state
  const [saving, setSaving]       = useState(false);
  const [profileMsg, setProfileMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Password form state
  const [currentPw, setCurrentPw]       = useState('');
  const [newPw, setNewPw]               = useState('');
  const [confirmPw, setConfirmPw]       = useState('');
  const [showPw, setShowPw]             = useState(false);
  const [pwSaving, setPwSaving]         = useState(false);
  const [pwMsg, setPwMsg]               = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // ── Load profile ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!token) return;
    getProfile(token)
      .then((p) => {
        setProfile(p);
        setAvatar(p.avatar ?? undefined);
        setEmail(p.email ?? '');
        setAge(p.age?.toString() ?? '');
        setOccupation((p.occupation as Occupation) ?? '');
        setFavBrand(p.favourite_brand ?? '');
        setCurrentPhone(p.current_phone ?? '');
        setJoinReason((p.join_reason as JoinReason) ?? '');
      })
      .catch(() => setLoadErr('Failed to load profile. Please refresh.'));
  }, [token]);

  // ── Save profile info ─────────────────────────────────────────────────────
  const handleSaveProfile = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setProfileMsg(null);
    setSaving(true);
    try {
      const updated = await updateProfile(token, {
        avatar,
        email: email || undefined,
        age: age ? parseInt(age, 10) : undefined,
        occupation: occupation || undefined,
        favourite_brand: favBrand || undefined,
        current_phone: currentPhone || undefined,
        join_reason: joinReason || undefined,
      });
      setProfile(updated);
      setContextAvatar(updated.avatar ?? undefined);
      setProfileMsg({ type: 'success', text: 'Profile updated successfully!' });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setProfileMsg({ type: 'error', text: msg || 'Failed to update profile.' });
    } finally {
      setSaving(false);
    }
  };

  // ── Change password ───────────────────────────────────────────────────────
  const handleChangePassword = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setPwMsg(null);
    if (newPw !== confirmPw) {
      setPwMsg({ type: 'error', text: 'New passwords do not match.' });
      return;
    }
    if (newPw.length < 6) {
      setPwMsg({ type: 'error', text: 'Password must be at least 6 characters.' });
      return;
    }
    setPwSaving(true);
    try {
      await changePassword(token, { current_password: currentPw, new_password: newPw });
      setPwMsg({ type: 'success', text: 'Password changed successfully!' });
      setCurrentPw(''); setNewPw(''); setConfirmPw('');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setPwMsg({ type: 'error', text: msg || 'Failed to change password.' });
    } finally {
      setPwSaving(false);
    }
  };

  // ── Loading / error states ────────────────────────────────────────────────
  if (loadErr) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center text-red-500">{loadErr}</div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 flex justify-center">
        <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
      </div>
    );
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto px-4 py-10 space-y-8">

      {/* Page header */}
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-full overflow-hidden bg-primary-50 border-2 border-primary-200 flex items-center justify-center shrink-0">
          {profile.avatar
            ? <img src={profile.avatar} alt={profile.username} className="w-full h-full object-cover" />
            : <User size={26} className="text-primary-400" />}
        </div>
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 flex items-center gap-2">
            <Settings size={20} className="text-primary-500" />
            Account Settings
          </h1>
          <p className="text-sm text-gray-400">
            @{profile.username} · Member since {new Date(profile.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* ── Profile info form ───────────────────────────────────────────── */}
      <div className="card shadow-md">
        <h2 className="text-lg font-semibold text-gray-800 mb-5 flex items-center gap-2">
          <User size={18} className="text-primary-500" />
          Profile Information
        </h2>

        {profileMsg && <Toast type={profileMsg.type} msg={profileMsg.text} />}

        <form onSubmit={handleSaveProfile} className="space-y-5 mt-4">

          {/* Avatar */}
          <AvatarPicker value={avatar} onChange={setAvatar} />

          {/* Email */}
          <div>
            <label className="label">Email</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="email"
                className="input pl-9"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          {/* Age */}
          <div>
            <label className="label">
              Age <span className="text-gray-400 text-xs">(optional)</span>
            </label>
            <div className="relative">
              <Hash size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="number"
                className="input pl-9"
                placeholder="e.g. 24"
                min={13}
                max={100}
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </div>
          </div>

          {/* Occupation */}
          <div>
            <label className="label">
              Occupation <span className="text-gray-400 text-xs">(optional)</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-1">
              {OCCUPATIONS.map((o) => (
                <button
                  key={o.value}
                  type="button"
                  onClick={() => setOccupation(occupation === o.value ? '' : o.value)}
                  className={`rounded-xl border px-3 py-2.5 text-sm font-medium text-left transition-all
                    ${occupation === o.value
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'}`}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </div>

          {/* Favourite Brand */}
          <div>
            <label className="label">
              Favourite Brand <span className="text-gray-400 text-xs">(optional)</span>
            </label>
            <div className="relative">
              <Heart size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <select
                className="input pl-9 appearance-none bg-white"
                value={favBrand}
                onChange={(e) => setFavBrand(e.target.value)}
              >
                <option value="">— Select a brand —</option>
                {BRANDS.map((b) => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
          </div>

          {/* Current Phone */}
          <div>
            <label className="label">
              Current Phone <span className="text-gray-400 text-xs">(optional)</span>
            </label>
            <div className="relative">
              <Phone size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                className="input pl-9"
                placeholder="e.g. Samsung Galaxy A52"
                value={currentPhone}
                onChange={(e) => setCurrentPhone(e.target.value)}
              />
            </div>
          </div>

          {/* Join Reason */}
          <div>
            <label className="label flex items-center gap-1">
              <HelpCircle size={14} className="text-gray-400" />
              Why are you here?
            </label>
            <div className="space-y-2 mt-1">
              {JOIN_REASONS.map((r) => (
                <label
                  key={r.value}
                  className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all
                    ${joinReason === r.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'}`}
                >
                  <input
                    type="radio"
                    name="join_reason"
                    value={r.value}
                    checked={joinReason === r.value}
                    onChange={() => setJoinReason(r.value)}
                    className="mt-0.5 accent-primary-600"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-800">{r.label}</p>
                    <p className="text-xs text-gray-500">{r.desc}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="btn-primary w-full flex items-center justify-center gap-2 py-2.5"
          >
            {saving
              ? <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              : <><Save size={16} /> Save Profile</>}
          </button>
        </form>
      </div>

      {/* ── Change Password ─────────────────────────────────────────────── */}
      <div className="card shadow-md">
        <h2 className="text-lg font-semibold text-gray-800 mb-5 flex items-center gap-2">
          <Lock size={18} className="text-primary-500" />
          Change Password
        </h2>

        {pwMsg && <Toast type={pwMsg.type} msg={pwMsg.text} />}

        <form onSubmit={handleChangePassword} className="space-y-4 mt-4">

          {/* Current password */}
          <div>
            <label className="label">Current Password</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type={showPw ? 'text' : 'password'}
                className="input pl-9 pr-10"
                placeholder="••••••••"
                value={currentPw}
                onChange={(e) => setCurrentPw(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                tabIndex={-1}
              >
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* New password */}
          <div>
            <label className="label">New Password</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type={showPw ? 'text' : 'password'}
                className="input pl-9"
                placeholder="••••••••"
                value={newPw}
                onChange={(e) => setNewPw(e.target.value)}
                required
                minLength={6}
              />
            </div>
          </div>

          {/* Confirm new password */}
          <div>
            <label className="label">Confirm New Password</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type={showPw ? 'text' : 'password'}
                className="input pl-9"
                placeholder="••••••••"
                value={confirmPw}
                onChange={(e) => setConfirmPw(e.target.value)}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={pwSaving}
            className="btn-primary w-full flex items-center justify-center gap-2 py-2.5"
          >
            {pwSaving
              ? <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              : <><Lock size={16} /> Update Password</>}
          </button>
        </form>
      </div>

      {/* Read-only info */}
      <div className="card shadow-sm bg-gray-50">
        <h2 className="text-sm font-semibold text-gray-500 mb-3 flex items-center gap-1">
          <Briefcase size={14} /> Account Details
        </h2>
        <div className="space-y-1 text-sm text-gray-600">
          <p><span className="font-medium text-gray-700">Username:</span> @{profile.username}</p>
          <p><span className="font-medium text-gray-700">Member since:</span> {new Date(profile.created_at).toLocaleDateString('en-GB', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
        </div>
      </div>

    </div>
  );
}
