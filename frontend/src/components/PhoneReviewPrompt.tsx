import { useState, useEffect, useRef, useCallback } from 'react';
import { Smartphone, X, Star, Battery, Zap, Clock, MessageSquare, ChevronRight, Loader2, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { identifyPhone, submitUserPhoneReview } from '../api/client';
import type { PhoneSuggestion } from '../api/client';

// ─── Types ────────────────────────────────────────────────────

interface ReviewForm {
  phoneName: string;
  yearsOwned: string;
  performance: number;
  battery: number;
  camera: number;
  durability: number;
  review: string;
}

const PROMPT_DELAY_MS = 45 * 1000; // 45 seconds after login
// localStorage key per user – set only after a successful submission
const doneKey = (username: string) => `tunitech_review_done_${username}`;

// ─── Star Rating ──────────────────────────────────────────────

function StarRating({
  value,
  onChange,
  label,
  icon,
}: {
  value: number;
  onChange: (v: number) => void;
  label: string;
  icon: React.ReactNode;
}) {
  const [hovered, setHovered] = useState(0);
  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center gap-1.5 text-sm text-neutral-600">
        {icon}
        {label}
      </span>
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => onChange(s)}
            onMouseEnter={() => setHovered(s)}
            onMouseLeave={() => setHovered(0)}
            className="p-0.5 transition-transform hover:scale-110"
          >
            <Star
              size={18}
              className={`transition-colors ${
                s <= (hovered || value)
                  ? 'fill-amber-400 text-amber-400'
                  : 'fill-none text-neutral-300'
              }`}
            />
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────

export default function PhoneReviewPrompt() {
  const { isLoggedIn, token, user } = useAuth();

  // Toast visibility
  const [showToast, setShowToast] = useState(false);
  // Modal open
  const [showModal, setShowModal] = useState(false);
  // Submission done
  const [submitted, setSubmitted] = useState(false);
  // Dismissed this session (not persisted – they'll see it again next login)
  const [dismissed, setDismissed] = useState(false);

  // Form state
  const [form, setForm] = useState<ReviewForm>({
    phoneName: '',
    yearsOwned: '',
    performance: 0,
    battery: 0,
    camera: 0,
    durability: 0,
    review: '',
  });

  // Groq suggestion state
  const [suggestion, setSuggestion] = useState<PhoneSuggestion | null>(null);
  const [loadingSuggestion, setLoadingSuggestion] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Trigger toast after delay ──
  useEffect(() => {
    if (!isLoggedIn || !user) return;
    // Skip if user already submitted a review (persisted in localStorage)
    if (localStorage.getItem(doneKey(user.username))) return;
    // Skip if dismissed this session
    if (dismissed) return;
    const timer = setTimeout(() => setShowToast(true), PROMPT_DELAY_MS);
    return () => clearTimeout(timer);
  }, [isLoggedIn, user, dismissed]);

  // ── Groq suggestion while typing (via backend) ──
  const handlePhoneNameChange = useCallback((value: string) => {
    setForm((f) => ({ ...f, phoneName: value }));
    setSuggestion(null);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (value.trim().length < 3 || !token) return;
    debounceRef.current = setTimeout(async () => {
      setLoadingSuggestion(true);
      try {
        const result = await identifyPhone(token, value);
        setSuggestion(result);
      } catch {
        setSuggestion(null);
      } finally {
        setLoadingSuggestion(false);
      }
    }, 500);
  }, [token]);

  const acceptSuggestion = () => {
    if (!suggestion) return;
    setForm((f) => ({ ...f, phoneName: `${suggestion.brand} ${suggestion.model}` }));
    setSuggestion(null);
  };

  const openModal = () => {
    setShowToast(false);
    setShowModal(true);
  };

  const dismiss = () => {
    setShowToast(false);
    // Only hide for this session — user will see it again next login
    setDismissed(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      await submitUserPhoneReview(token, {
        phone_name: form.phoneName,
        years_owned: form.yearsOwned || undefined,
        performance: form.performance,
        battery: form.battery,
        camera: form.camera,
        durability: form.durability,
        review: form.review || undefined,
      });
    } catch {
      // best-effort — still show success to user
    }
    // Mark permanently done for this user so the prompt never shows again
    if (user) localStorage.setItem(doneKey(user.username), '1');
    setSubmitted(true);
    setTimeout(() => {
      setShowModal(false);
      setSubmitted(false);
      setForm({ phoneName: '', yearsOwned: '', performance: 0, battery: 0, camera: 0, durability: 0, review: '' });
    }, 2000);
  };

  const canSubmit =
    form.phoneName.trim().length > 1 &&
    form.performance > 0 &&
    form.battery > 0;

  if (!isLoggedIn) return null;

  return (
    <>
      {/* ── Bottom-right toast ── */}
      {showToast && !showModal && (
        <div className="fixed bottom-6 right-6 z-50 animate-in slide-in-from-bottom-4 fade-in duration-300">
          <div className="relative bg-white rounded-2xl shadow-2xl border border-neutral-100 p-4 w-80 flex gap-3">
            {/* Dismiss */}
            <button
              onClick={dismiss}
              className="absolute top-2 right-2 p-1 rounded-full text-neutral-300 hover:text-neutral-500 hover:bg-neutral-100 transition-colors"
              aria-label="Dismiss"
            >
              <X size={14} />
            </button>

            {/* Icon */}
            <div className="shrink-0 w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
              <Smartphone size={20} className="text-primary-600" />
            </div>

            {/* Text */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-neutral-800 leading-tight">
                Tell us about your phone
              </p>
              <p className="text-xs text-neutral-500 mt-0.5 leading-snug">
                What are you currently using? Share a quick review&nbsp;✨
              </p>

              <button
                onClick={openModal}
                className="mt-2.5 flex items-center gap-1 text-xs font-semibold text-primary-600 hover:text-primary-700 transition-colors group"
              >
                Share your experience
                <ChevronRight size={13} className="group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal overlay ── */}
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-200"
          onClick={(e) => { if (e.target === e.currentTarget) setShowModal(false); }}
        >
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-neutral-100 overflow-hidden animate-in slide-in-from-bottom-4 sm:slide-in-from-bottom-0 duration-200">
            {/* Header */}
            <div className="bg-gradient-to-r from-primary-600 to-primary-500 px-5 py-4 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  <Smartphone size={17} className="text-white" />
                </div>
                <div>
                  <p className="text-white font-semibold text-sm">Your Phone Experience</p>
                  <p className="text-primary-100 text-xs">Help others make better choices</p>
                </div>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="p-1.5 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X size={17} />
              </button>
            </div>

            {submitted ? (
              <div className="py-14 flex flex-col items-center gap-3 animate-in fade-in duration-300">
                <div className="w-14 h-14 rounded-full bg-green-50 flex items-center justify-center">
                  <Sparkles size={26} className="text-green-500" />
                </div>
                <p className="text-base font-semibold text-neutral-800">Thanks for sharing!</p>
                <p className="text-sm text-neutral-500">Your review helps the community.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="p-5 space-y-4 max-h-[75vh] overflow-y-auto">
                {/* Phone name + Groq suggestion */}
                <div>
                  <label className="block text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-1.5">
                    Your current phone
                  </label>
                  <div className="relative">
                    <Smartphone size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none" />
                    <input
                      type="text"
                      value={form.phoneName}
                      onChange={(e) => handlePhoneNameChange(e.target.value)}
                      placeholder="e.g. Samsung A54, iPhone 14…"
                      className="w-full pl-9 pr-9 py-2.5 rounded-xl border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-300 transition"
                      autoFocus
                    />
                    {loadingSuggestion && (
                      <Loader2 size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-primary-400 animate-spin" />
                    )}
                  </div>

                  {/* Groq suggestion pill */}
                  {suggestion && !loadingSuggestion && (
                    <button
                      type="button"
                      onClick={acceptSuggestion}
                      className="mt-1.5 flex items-center gap-2 px-3 py-1.5 bg-primary-50 border border-primary-100 rounded-xl text-xs text-primary-700 hover:bg-primary-100 transition-colors w-full text-left"
                    >
                      <Sparkles size={12} className="text-primary-500 shrink-0" />
                      <span>
                        <span className="font-semibold">{suggestion.brand} {suggestion.model}</span>
                        <span className="text-primary-400 ml-1">· {suggestion.confidence} confidence — tap to use</span>
                      </span>
                    </button>
                  )}
                </div>

                {/* Years owned */}
                <div>
                  <label className="block text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-1.5">
                    <span className="flex items-center gap-1.5"><Clock size={13} /> Years owned</span>
                  </label>
                  <div className="flex gap-2 flex-wrap">
                    {['< 1 year', '1 year', '2 years', '3+ years'].map((opt) => (
                      <button
                        key={opt}
                        type="button"
                        onClick={() => setForm((f) => ({ ...f, yearsOwned: opt }))}
                        className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-all ${
                          form.yearsOwned === opt
                            ? 'bg-primary-600 text-white border-primary-600'
                            : 'bg-neutral-50 text-neutral-600 border-neutral-200 hover:border-primary-300'
                        }`}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Ratings */}
                <div className="space-y-2.5 bg-neutral-50 rounded-xl p-3.5">
                  <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-1">Rate your experience</p>
                  <StarRating
                    label="Performance"
                    icon={<Zap size={13} className="text-yellow-400" />}
                    value={form.performance}
                    onChange={(v) => setForm((f) => ({ ...f, performance: v }))}
                  />
                  <StarRating
                    label="Battery Life"
                    icon={<Battery size={13} className="text-green-400" />}
                    value={form.battery}
                    onChange={(v) => setForm((f) => ({ ...f, battery: v }))}
                  />
                  <StarRating
                    label="Camera"
                    icon={<Smartphone size={13} className="text-blue-400" />}
                    value={form.camera}
                    onChange={(v) => setForm((f) => ({ ...f, camera: v }))}
                  />
                  <StarRating
                    label="Durability"
                    icon={<Star size={13} className="text-purple-400" />}
                    value={form.durability}
                    onChange={(v) => setForm((f) => ({ ...f, durability: v }))}
                  />
                </div>

                {/* Review text */}
                <div>
                  <label className="block text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-1.5">
                    <span className="flex items-center gap-1.5"><MessageSquare size={13} /> Your review (optional)</span>
                  </label>
                  <textarea
                    value={form.review}
                    onChange={(e) => setForm((f) => ({ ...f, review: e.target.value }))}
                    rows={3}
                    placeholder="What do you love or hate about it?"
                    className="w-full px-3 py-2.5 rounded-xl border border-neutral-200 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-300 transition"
                  />
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 py-2.5 rounded-xl text-sm font-medium text-neutral-600 border border-neutral-200 hover:bg-neutral-50 transition-colors"
                  >
                    Maybe later
                  </button>
                  <button
                    type="submit"
                    disabled={!canSubmit}
                    className="flex-1 py-2.5 rounded-xl text-sm font-semibold bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                  >
                    Submit Review
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
