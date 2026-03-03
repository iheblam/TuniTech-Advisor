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
} from 'lucide-react';
import type { SmartphoneDetail } from '../types';
import { getPhoneImage } from '../api/client';

interface Props {
  phone: SmartphoneDetail;
  onClose: () => void;
}

export default function PhoneDetailModal({ phone, onClose }: Props) {
  const [candidates, setCandidates] = useState<string[]>([]);
  const [urlIndex, setUrlIndex] = useState(0);
  const [imgLoading, setImgLoading] = useState(true);
  const [allFailed, setAllFailed] = useState(false);

  const PLACEHOLDER = `https://placehold.co/400x400/f3f4f6/9ca3af?text=${encodeURIComponent(phone.brand + ' ' + phone.name.split(' ').slice(0, 3).join(' '))}`;

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
            <img
              src={PLACEHOLDER}
              alt={phone.name}
              className="h-full w-full object-contain p-4 opacity-60"
            />
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
