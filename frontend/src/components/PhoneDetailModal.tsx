import { useEffect, useState, useCallback } from 'react';
import {
  X,
  ExternalLink,
  Wifi,
  Nfc,
  Battery,
  HardDrive,
  Cpu,
  Monitor,
  Camera,
  Star,
  Loader2,
  MessageSquare,
  Trash2,
  Smartphone,
  Search,
} from 'lucide-react';
import type { SmartphoneDetail } from '../types';
import { getPhoneImage, trackEvent, getReviews, addReview, deleteReview } from '../api/client';
import { useAuth } from '../context/AuthContext';

interface Props {
  phone: SmartphoneDetail;
  onClose: () => void;
}

export default function PhoneDetailModal({ phone, onClose }: Props) {
  const { isLoggedIn, token, user } = useAuth();
  const [candidates, setCandidates] = useState<string[]>([]);
  const [urlIndex, setUrlIndex] = useState(0);
  const [imgLoading, setImgLoading] = useState(true);
  const [allFailed, setAllFailed] = useState(false);

  // ── Reviews state ─────────────────────────────────────────────────────────
  type Review = { id: string; username: string; rating: number; comment: string; date: string };
  const [reviews, setReviews]       = useState<Review[]>([]);
  const [stats, setStats]           = useState<{ count: number; avg_rating: number | null } | null>(null);
  const [myRating, setMyRating]     = useState(0);
  const [myComment, setMyComment]   = useState('');
  const [revLoading, setRevLoading] = useState(false);
  const [revMsg, setRevMsg]         = useState('');

  const refreshReviews = useCallback(() => {
    getReviews(phone.name).then((d) => { setReviews(d.reviews); setStats(d.stats); }).catch(() => {});
  }, [phone.name]);

  const handleSubmitReview = async () => {
    if (!token || myRating === 0) return;
    setRevLoading(true);
    try {
      await addReview(token, phone.name, myRating, myComment);
      refreshReviews();
      setMyRating(0); setMyComment('');
      setRevMsg('\u2713 Review submitted!');
    } catch { setRevMsg('Failed to submit.'); }
    finally { setRevLoading(false); setTimeout(() => setRevMsg(''), 3000); }
  };

  const handleDeleteReview = async (id: string) => {
    if (!token) return;
    try { await deleteReview(token, phone.name, id); refreshReviews(); } catch {}
  };

  // fetch candidates on mount
  useEffect(() => {
    let cancelled = false;
    setImgLoading(true);
    setAllFailed(false);
    setUrlIndex(0);
    setCandidates([]);
    getPhoneImage(phone.name, phone.brand, phone.url)
      .then((res) => {
        if (!cancelled) {
          const urls = res.image_urls ?? [];
          setCandidates(urls);
          if (urls.length === 0) setAllFailed(true);
        }
      })
      .catch(() => {
        if (!cancelled) setAllFailed(true);
      })
      .finally(() => {
        if (!cancelled) setImgLoading(false);
      });
    return () => { cancelled = true; };
  }, [phone.name, phone.brand, phone.url]);

  // Track view + load reviews when modal opens
  useEffect(() => {
    trackEvent(phone.name, 'view');
    refreshReviews();
  }, [phone.name, refreshReviews]);

  const currentUrl = candidates[urlIndex] ?? null;

  const handleImgError = () => {
    if (urlIndex + 1 < candidates.length) {
      // try next candidate
      setUrlIndex((i) => i + 1);
    } else {
      // all candidates exhausted — show placeholder
      setAllFailed(true);
    }
  };

  // close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  const handleBackdrop = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      onClick={handleBackdrop}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-gray-100">
          <div>
            <h2 className="text-xl font-bold text-gray-900 leading-tight">{phone.name}</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              {phone.brand} &middot; {phone.store}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors shrink-0 ml-3"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Image */}
        <div className="bg-gray-50 flex items-center justify-center h-60 overflow-hidden">
          {imgLoading ? (
            <div className="flex flex-col items-center gap-2 text-gray-400">
              <Loader2 size={32} className="animate-spin" />
              <span className="text-xs">Loading image…</span>
            </div>
          ) : allFailed || !currentUrl ? (
            <div className="flex flex-col items-center gap-2.5 text-gray-400 px-4 text-center">
              <Smartphone size={44} className="text-gray-300" />
              <span className="text-sm font-medium text-gray-400">No image available</span>
              <a
                href={`https://www.google.com/search?tbm=isch&q=${encodeURIComponent(phone.brand + ' ' + phone.name)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-blue-500 hover:text-blue-700 hover:underline font-medium"
              >
                <Search size={12} />
                Search on Google Images
              </a>
            </div>
          ) : (
            <img
              key={urlIndex}
              src={currentUrl}
              alt={phone.name}
              className="h-full w-full object-contain p-4"
              onError={handleImgError}
            />
          )}
        </div>

        {/* Price & badges */}
        <div className="px-5 pt-4 pb-2 flex items-center justify-between flex-wrap gap-2">
          <span className="text-2xl font-extrabold text-primary-700">
            {phone.price?.toLocaleString()}{' '}
            <span className="text-base font-semibold">TND</span>
          </span>
          <div className="flex flex-wrap gap-1.5">
            {phone.match_score != null && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">
                <Star size={10} /> {phone.match_score.toFixed(0)}% match
              </span>
            )}
            {phone.is_5g && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-medium">
                <Wifi size={10} /> 5G
              </span>
            )}
            {phone.has_nfc && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 font-medium">
                <Nfc size={10} /> NFC
              </span>
            )}
          </div>
        </div>

        {/* Specs */}
        <div className="px-5 pb-4 grid grid-cols-2 gap-3 mt-2">
          {phone.ram != null && (
            <SpecRow icon={<HardDrive size={15} />} label="RAM" value={`${phone.ram} GB`} />
          )}
          {phone.storage != null && (
            <SpecRow icon={<HardDrive size={15} />} label="Storage" value={`${phone.storage} GB`} />
          )}
          {phone.battery != null && (
            <SpecRow icon={<Battery size={15} />} label="Battery" value={`${phone.battery} mAh`} />
          )}
          {phone.screen_size != null && (
            <SpecRow icon={<Monitor size={15} />} label="Screen" value={`${phone.screen_size}"`} />
          )}
          {phone.main_camera != null && (
            <SpecRow icon={<Camera size={15} />} label="Rear Camera" value={`${phone.main_camera} MP`} />
          )}
          {phone.front_camera != null && (
            <SpecRow icon={<Camera size={15} />} label="Front Camera" value={`${phone.front_camera} MP`} />
          )}
          {phone.processor && (
            <div className="col-span-2">
              <SpecRow icon={<Cpu size={15} />} label="Processor" value={phone.processor} />
            </div>
          )}
          {phone.availability && (
            <div className="col-span-2 text-xs text-gray-500">
              Availability: <strong>{phone.availability}</strong>
            </div>
          )}
        </div>

        {/* Footer CTA */}
        {phone.url && (
          <div className="px-5 pb-5">
            <a
              href={phone.url}
              target="_blank"
              rel="noreferrer"
              className="btn-primary flex items-center justify-center gap-2 w-full"
            >
              <ExternalLink size={15} />
              View on {phone.store}
            </a>
          </div>
        )}

        {/* ── Community Reviews ──────────────────────────────────────────── */}
        <div className="px-5 pb-6 border-t border-gray-100 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <MessageSquare size={15} className="text-gray-400" /> Community Reviews
            </h3>
            {stats && stats.count > 0 && (
              <span className="flex items-center gap-1 text-xs text-gray-500">
                {[1,2,3,4,5].map(n => (
                  <Star key={n} size={11}
                    fill={n <= Math.round(stats.avg_rating ?? 0) ? 'currentColor' : 'none'}
                    className={n <= Math.round(stats.avg_rating ?? 0) ? 'text-yellow-400' : 'text-gray-200'}
                  />
                ))}
                <span className="ml-1 font-semibold">{stats.avg_rating}</span>
                <span className="text-gray-300">({stats.count})</span>
              </span>
            )}
          </div>

          {/* Write review */}
          {isLoggedIn && (
            <div className="mb-4 p-3 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-xs font-semibold text-gray-600 mb-2">Rate this phone</p>
              <div className="flex gap-1 mb-2">
                {[1,2,3,4,5].map(n => (
                  <button key={n} type="button" onClick={() => setMyRating(n)}
                    className={`transition-colors ${
                      n <= myRating ? 'text-yellow-400' : 'text-gray-300'
                    } hover:text-yellow-400`}
                  >
                    <Star size={22} fill={n <= myRating ? 'currentColor' : 'none'} />
                  </button>
                ))}
              </div>
              <textarea
                value={myComment}
                onChange={(e) => setMyComment(e.target.value)}
                placeholder="Share your experience (optional)"
                className="w-full text-sm border border-gray-200 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-primary-400"
                rows={2}
              />
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-primary-600">{revMsg}</span>
                <button
                  onClick={handleSubmitReview}
                  disabled={myRating === 0 || revLoading}
                  className="btn-primary text-xs py-1.5 px-3 disabled:opacity-40"
                >
                  {revLoading ? 'Saving…' : 'Submit'}
                </button>
              </div>
            </div>
          )}

          {/* Reviews list */}
          {reviews.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-3">
              {isLoggedIn ? 'No reviews yet — be the first!' : 'No reviews yet.'}
            </p>
          ) : (
            <div className="space-y-3">
              {reviews.map((r) => (
                <div key={r.id} className="flex gap-3">
                  <div className="w-7 h-7 rounded-full bg-primary-100 flex items-center justify-center text-xs font-bold text-primary-600 shrink-0">
                    {r.username[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-gray-700 truncate">{r.username}</span>
                      <div className="flex items-center gap-1.5 shrink-0">
                        <span className="flex">
                          {[1,2,3,4,5].map(n => (
                            <Star key={n} size={10}
                              fill={n <= r.rating ? 'currentColor' : 'none'}
                              className={n <= r.rating ? 'text-yellow-400' : 'text-gray-200'}
                            />
                          ))}
                        </span>
                        {user?.username === r.username && (
                          <button onClick={() => handleDeleteReview(r.id)}
                            className="text-gray-300 hover:text-red-400 transition-colors" title="Delete my review"
                          >
                            <Trash2 size={11} />
                          </button>
                        )}
                      </div>
                    </div>
                    {r.comment && <p className="text-xs text-gray-500 mt-0.5 break-words">{r.comment}</p>}
                    <p className="text-[10px] text-gray-300 mt-0.5">{new Date(r.date).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SpecRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-2 text-sm text-gray-700">
      <span className="text-gray-400 shrink-0">{icon}</span>
      <span className="text-gray-400 shrink-0">{label}:</span>
      <span className="font-medium truncate">{value}</span>
    </div>
  );
}
