import { useState, useEffect } from 'react';
import { ExternalLink, Wifi, Nfc, Star, Eye, Smartphone } from 'lucide-react';
import type { SmartphoneDetail } from '../types';
import PhoneDetailModal from './PhoneDetailModal';
import { getPhoneImage } from '../api/client';

interface Props {
  phone: SmartphoneDetail;
  selectable?: boolean;
  selected?: boolean;
  onSelect?: (p: SmartphoneDetail) => void;
}

export default function PhoneCard({ phone, selectable, selected, onSelect }: Props) {
  const [showModal, setShowModal] = useState(false);
  const [imgUrl, setImgUrl] = useState<string | null>(null);
  const [imgLoaded, setImgLoaded] = useState(false);
  const [imgFetched, setImgFetched] = useState(false);

  // Lazy-fetch image once the card mounts
  useEffect(() => {
    let cancelled = false;
    getPhoneImage(phone.name, phone.brand, phone.url)
      .then((res) => { if (!cancelled && res.image_urls?.length) setImgUrl(res.image_urls[0]); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setImgFetched(true); });
    return () => { cancelled = true; };
  }, [phone.name, phone.brand, phone.url]);

  const handleCardClick = () => {
    if (selectable) {
      onSelect?.(phone);
    } else {
      setShowModal(true);
    }
  };

  return (
    <>
      <div
        className={`card flex flex-col gap-0 overflow-hidden transition-all cursor-pointer hover:shadow-md hover:-translate-y-0.5 p-0 ${
          selected ? 'ring-2 ring-primary-500' : ''
        }`}
        onClick={handleCardClick}
      >
        {/* ── Image banner ── */}
        <div className="relative bg-gray-50 h-44 flex items-center justify-center overflow-hidden">
          {/* Skeleton shimmer while fetching */}
          {!imgFetched && (
            <div className="absolute inset-0 bg-gradient-to-r from-gray-100 via-gray-200 to-gray-100 animate-pulse" />
          )}
          {imgUrl ? (
            <img
              src={imgUrl}
              alt={phone.name}
              className={`h-full w-full object-contain p-3 transition-opacity duration-300 ${imgLoaded ? 'opacity-100' : 'opacity-0'}`}
              onLoad={() => setImgLoaded(true)}
              onError={() => { setImgUrl(null); setImgLoaded(true); }}
            />
          ) : imgFetched ? (
            <div className="flex flex-col items-center gap-1 text-gray-300">
              <Smartphone size={40} />
              <span className="text-xs">No image</span>
            </div>
          ) : null}

          {/* Store badge overlay */}
          <span className="absolute top-2 left-2 text-[10px] px-1.5 py-0.5 rounded-full bg-white/80 text-gray-500 font-medium shadow-sm border border-gray-100">
            {phone.store}
          </span>

          {/* Match score overlay */}
          {phone.match_score != null && (
            <span className="absolute top-2 right-2 inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.5 rounded-full bg-green-100 text-green-700 font-semibold">
              <Star size={9} /> {phone.match_score.toFixed(0)}%
            </span>
          )}
        </div>

        {/* ── Card body ── */}
        <div className="flex flex-col gap-3 p-4">
          {/* Header */}
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold text-gray-900 leading-tight text-sm">{phone.name}</h3>
              <p className="text-xs text-gray-400 mt-0.5">{phone.brand}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-base font-bold text-primary-700">
                {phone.price?.toLocaleString()} <span className="text-xs font-medium">TND</span>
              </p>
            </div>
          </div>

          {/* Specs grid */}
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-600">
            {phone.ram != null && <Spec label="RAM" value={`${phone.ram} GB`} />}
            {phone.storage != null && <Spec label="Storage" value={`${phone.storage} GB`} />}
            {phone.battery != null && <Spec label="Battery" value={`${phone.battery} mAh`} />}
            {phone.screen_size != null && <Spec label="Screen" value={`${phone.screen_size}"`} />}
            {phone.main_camera != null && <Spec label="Camera" value={`${phone.main_camera} MP`} />}
            {phone.front_camera != null && <Spec label="Selfie" value={`${phone.front_camera} MP`} />}
            {phone.processor && <Spec label="CPU" value={phone.processor} full />}
          </div>

          {/* Badges + actions */}
          <div className="flex flex-wrap gap-1.5 mt-auto pt-1">
            {phone.is_5g && (
              <span className="badge bg-blue-100 text-blue-700">
                <Wifi size={10} /> 5G
              </span>
            )}
            {phone.has_nfc && (
              <span className="badge bg-purple-100 text-purple-700">
                <Nfc size={10} /> NFC
              </span>
            )}
            {phone.availability && (
              <span className="badge bg-gray-100 text-gray-600">{phone.availability}</span>
            )}
            <div className="ml-auto flex gap-1">
              {!selectable && (
                <button
                  className="badge bg-primary-50 text-primary-700 hover:bg-primary-100"
                  onClick={(e) => { e.stopPropagation(); setShowModal(true); }}
                  title="View details & image"
                >
                  <Eye size={10} /> Details
                </button>
              )}
              {phone.url && (
                <a
                  href={phone.url}
                  target="_blank"
                  rel="noreferrer"
                  className="badge bg-gray-100 text-gray-600 hover:bg-gray-200"
                  onClick={(e) => e.stopPropagation()}
                  title="Open store page"
                >
                  <ExternalLink size={10} /> View
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <PhoneDetailModal phone={phone} onClose={() => setShowModal(false)} />
      )}
    </>
  );
}

function Spec({ label, value, full }: { label: string; value: string; full?: boolean }) {
  return (
    <div className={full ? 'col-span-2' : ''}>
      <span className="font-medium text-gray-400">{label}: </span>
      <span className="text-gray-700">{value}</span>
    </div>
  );
}