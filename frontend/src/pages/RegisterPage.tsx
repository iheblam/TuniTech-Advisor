import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Lock, User, Mail, Smartphone, Eye, EyeOff,
  ChevronRight, ChevronLeft, Briefcase,
  Hash, Heart, Phone, HelpCircle, CheckCircle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import type { Occupation, JoinReason } from '../types';
import AvatarPicker from '../components/AvatarPicker';

// ── Step metadata ──────────────────────────────────────────────────────────
const STEPS = [
  { label: 'Account',     icon: User },
  { label: 'About You',   icon: Briefcase },
  { label: 'Preferences', icon: Heart },
] as const;

const OCCUPATIONS: { value: Occupation; label: string }[] = [
  { value: 'student',       label: '🎓 Student' },
  { value: 'employee',      label: '💼 Employee' },
  { value: 'freelancer',    label: '💻 Freelancer' },
  { value: 'self_employed', label: '🏢 Self-employed' },
  { value: 'other',         label: '✨ Other' },
];

const JOIN_REASONS: { value: JoinReason; label: string; desc: string }[] = [
  { value: 'searching_phone',    label: 'Searching for a phone',  desc: 'I want to find my next device' },
  { value: 'comparing_prices',   label: 'Comparing prices',       desc: 'I want the best deal across stores' },
  { value: 'reading_reviews',    label: 'Reading reviews',        desc: 'I want community opinions' },
  { value: 'browsing',           label: 'Just browsing',          desc: 'Exploring what\'s available' },
];

const BRANDS = ['Samsung', 'Apple', 'Huawei', 'Xiaomi', 'Oppo', 'Realme', 'OnePlus', 'Nokia', 'Sony', 'Other'];

// ── Component ──────────────────────────────────────────────────────────────
export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Step 1
  const [username, setUsername]     = useState('');
  const [email, setEmail]           = useState('');
  const [password, setPassword]     = useState('');
  const [confirm, setConfirm]       = useState('');
  const [showPw, setShowPw]         = useState(false);

  // Step 2
  const [age, setAge]               = useState('');
  const [occupation, setOccupation] = useState<Occupation | ''>('');

  // Step 3
  const [avatar, setAvatar]             = useState<string | undefined>(undefined);
  const [favBrand, setFavBrand]         = useState('');
  const [currentPhone, setCurrentPhone] = useState('');
  const [joinReason, setJoinReason]     = useState<JoinReason | ''>('');

  // ── Step navigation ──────────────────────────────────────────────────────
  const goNext = (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (step === 0) {
      if (password !== confirm) { setError('Passwords do not match.'); return; }
    }
    setStep((s) => s + 1);
  };

  const goBack = () => { setError(''); setStep((s) => s - 1); };

  // ── Final submit ─────────────────────────────────────────────────────────
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (!joinReason) { setError('Please tell us why you are joining.'); return; }
    setLoading(true);
    try {
      await register({
        username,
        email,
        password,
        age: age ? parseInt(age, 10) : undefined,
        occupation: occupation || undefined,
        avatar,
        favourite_brand: favBrand || undefined,
        current_phone: currentPhone || undefined,
        join_reason: joinReason,
      });
      navigate('/', { replace: true });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // ── Progress bar ─────────────────────────────────────────────────────────
  const StepBar = () => (
    <div className="flex items-center justify-between mb-8">
      {STEPS.map((s, i) => {
        const done   = i < step;
        const active = i === step;
        const Icon   = s.icon;
        return (
          <div key={s.label} className="flex-1 flex flex-col items-center gap-1">
            <div className={`w-9 h-9 rounded-full flex items-center justify-center transition-all
              ${done   ? 'bg-green-500 text-white'
              : active ? 'bg-primary-600 text-white ring-4 ring-primary-100'
              :          'bg-gray-100 text-gray-400'}`}>
              {done ? <CheckCircle size={18} /> : <Icon size={16} />}
            </div>
            <span className={`text-xs font-medium hidden sm:block
              ${active ? 'text-primary-600' : done ? 'text-green-600' : 'text-gray-400'}`}>
              {s.label}
            </span>
            {i < STEPS.length - 1 && (
              <div className={`absolute hidden`} />
            )}
          </div>
        );
      })}
    </div>
  );

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-[90vh] flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary-600 text-white mb-3 shadow-lg">
            <Smartphone size={28} />
          </div>
          <h1 className="text-2xl font-extrabold text-gray-900">Create your account</h1>
          <p className="text-sm text-gray-400 mt-1">Step {step + 1} of {STEPS.length} — {STEPS[step].label}</p>
        </div>

        {/* Card */}
        <div className="card shadow-xl space-y-5">

          <StepBar />

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm flex items-center gap-2">
              <Lock size={14} className="shrink-0" />
              {error}
            </div>
          )}

          {/* ── Step 0: Account ──────────────────────────────────── */}
          {step === 0 && (
            <form onSubmit={goNext} className="space-y-4">
              {/* Username */}
              <div>
                <label className="label">Username <span className="text-red-500">*</span></label>
                <div className="relative">
                  <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="text" className="input pl-9" placeholder="john_doe"
                    autoComplete="username" value={username}
                    onChange={(e) => setUsername(e.target.value)} required minLength={3} />
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="label">Email <span className="text-red-500">*</span></label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="email" className="input pl-9" placeholder="you@example.com"
                    autoComplete="email" value={email}
                    onChange={(e) => setEmail(e.target.value)} required />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="label">Password <span className="text-red-500">*</span></label>
                <div className="relative">
                  <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type={showPw ? 'text' : 'password'} className="input pl-9 pr-10"
                    placeholder="••••••••" autoComplete="new-password" value={password}
                    onChange={(e) => setPassword(e.target.value)} required minLength={6} />
                  <button type="button" onClick={() => setShowPw((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" tabIndex={-1}>
                    {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* Confirm */}
              <div>
                <label className="label">Confirm Password <span className="text-red-500">*</span></label>
                <div className="relative">
                  <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type={showPw ? 'text' : 'password'} className="input pl-9"
                    placeholder="••••••••" autoComplete="new-password" value={confirm}
                    onChange={(e) => setConfirm(e.target.value)} required />
                </div>
              </div>

              <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2 py-2.5">
                Next <ChevronRight size={16} />
              </button>
            </form>
          )}

          {/* ── Step 1: About You ────────────────────────────────── */}
          {step === 1 && (
            <form onSubmit={goNext} className="space-y-5">
              {/* Age */}
              <div>
                <label className="label">Age <span className="text-gray-400 text-xs">(optional)</span></label>
                <div className="relative">
                  <Hash size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="number" className="input pl-9" placeholder="e.g. 24"
                    min={13} max={100} value={age}
                    onChange={(e) => setAge(e.target.value)} />
                </div>
              </div>

              {/* Occupation */}
              <div>
                <label className="label">Occupation <span className="text-gray-400 text-xs">(optional)</span></label>
                <div className="grid grid-cols-2 gap-2 mt-1">
                  {OCCUPATIONS.map((o) => (
                    <button key={o.value} type="button"
                      onClick={() => setOccupation(occupation === o.value ? '' : o.value)}
                      className={`rounded-xl border px-3 py-2.5 text-sm font-medium text-left transition-all
                        ${occupation === o.value
                          ? 'border-primary-500 bg-primary-50 text-primary-700'
                          : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'}`}>
                      {o.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3">
                <button type="button" onClick={goBack}
                  className="btn-secondary flex-1 flex items-center justify-center gap-1 py-2.5">
                  <ChevronLeft size={16} /> Back
                </button>
                <button type="submit"
                  className="btn-primary flex-1 flex items-center justify-center gap-1 py-2.5">
                  Next <ChevronRight size={16} />
                </button>
              </div>
            </form>
          )}

          {/* ── Step 2: Preferences ──────────────────────────────── */}
          {step === 2 && (
            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Avatar */}
              <AvatarPicker value={avatar} onChange={setAvatar} />

              {/* Favourite Brand */}
              <div>
                <label className="label">Favourite Brand <span className="text-gray-400 text-xs">(optional)</span></label>
                <div className="relative">
                  <Heart size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <select className="input pl-9 appearance-none bg-white" value={favBrand}
                    onChange={(e) => setFavBrand(e.target.value)}>
                    <option value="">— Select a brand —</option>
                    {BRANDS.map((b) => <option key={b} value={b}>{b}</option>)}
                  </select>
                </div>
              </div>

              {/* Current Phone */}
              <div>
                <label className="label">Current Phone <span className="text-gray-400 text-xs">(optional)</span></label>
                <div className="relative">
                  <Phone size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="text" className="input pl-9" placeholder="e.g. Samsung Galaxy A52"
                    value={currentPhone} onChange={(e) => setCurrentPhone(e.target.value)} />
                </div>
              </div>

              {/* Join Reason */}
              <div>
                <label className="label flex items-center gap-1">
                  <HelpCircle size={14} className="text-gray-400" />
                  Why are you joining? <span className="text-red-500">*</span>
                </label>
                <div className="space-y-2 mt-1">
                  {JOIN_REASONS.map((r) => (
                    <label key={r.value}
                      className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all
                        ${joinReason === r.value
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'}`}>
                      <input type="radio" name="join_reason" value={r.value}
                        checked={joinReason === r.value}
                        onChange={() => setJoinReason(r.value)}
                        className="mt-0.5 accent-primary-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-800">{r.label}</p>
                        <p className="text-xs text-gray-500">{r.desc}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex gap-3">
                <button type="button" onClick={goBack}
                  className="btn-secondary flex-1 flex items-center justify-center gap-1 py-2.5">
                  <ChevronLeft size={16} /> Back
                </button>
                <button type="submit" disabled={loading}
                  className="btn-primary flex-1 flex items-center justify-center gap-2 py-2.5">
                  {loading
                    ? <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                    : <><CheckCircle size={16} /> Create Account</>}
                </button>
              </div>
            </form>
          )}

          <p className="text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 font-semibold hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
