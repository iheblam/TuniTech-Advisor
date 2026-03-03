import { useState } from 'react';
import { CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';

// ── Preset online avatars (DiceBear CDN) ─────────────────────────────────────
export const PRESET_AVATARS: { url: string; label: string }[] = [
  { url: 'https://api.dicebear.com/7.x/fun-emoji/svg?seed=Felix',   label: 'Felix' },
  { url: 'https://api.dicebear.com/7.x/fun-emoji/svg?seed=Aneka',   label: 'Aneka' },
  { url: 'https://api.dicebear.com/7.x/fun-emoji/svg?seed=Luna',    label: 'Luna' },
  { url: 'https://api.dicebear.com/7.x/fun-emoji/svg?seed=Mango',   label: 'Mango' },
  { url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Leo&backgroundColor=b6e3f4',  label: 'Leo' },
  { url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sara&backgroundColor=ffd5dc', label: 'Sara' },
  { url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Max&backgroundColor=c0aede',  label: 'Max' },
  { url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Zoe&backgroundColor=d1f4cc',  label: 'Zoe' },
  { url: 'https://api.dicebear.com/7.x/bottts/svg?seed=R2D2',       label: 'R2D2' },
  { url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Cyborg',     label: 'Cyborg' },
  { url: 'https://api.dicebear.com/7.x/pixel-art/svg?seed=Jasper',  label: 'Jasper' },
  { url: 'https://api.dicebear.com/7.x/pixel-art/svg?seed=Ruby',    label: 'Ruby' },
];

interface AvatarPickerProps {
  value: string | undefined;
  onChange: (url: string | undefined) => void;
}

export default function AvatarPicker({ value, onChange }: AvatarPickerProps) {
  const [open, setOpen] = useState(false);

  return (
    <div>
      <label className="label">
        Profile Avatar{' '}
        <span className="text-gray-400 text-xs">(optional)</span>
      </label>

      {/* Preview + toggle */}
      <div className="flex items-center gap-4 mt-1">
        <div
          className="w-16 h-16 rounded-full border-2 border-dashed border-primary-300 bg-gray-50
                     flex items-center justify-center overflow-hidden shrink-0 shadow-sm"
        >
          {value ? (
            <img src={value} alt="avatar" className="w-full h-full object-cover" />
          ) : (
            <span className="text-3xl select-none">🙂</span>
          )}
        </div>

        <div className="flex flex-col gap-1">
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="btn-secondary text-sm py-1.5 px-3 flex items-center gap-1"
          >
            {value ? 'Change avatar' : 'Choose avatar'}
            {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {value && (
            <button
              type="button"
              onClick={() => onChange(undefined)}
              className="text-xs text-red-500 hover:underline text-left"
            >
              Remove
            </button>
          )}
          <p className="text-xs text-gray-400">Pick from our preset collection</p>
        </div>
      </div>

      {/* Avatar grid */}
      {open && (
        <div className="mt-3 p-3 border border-gray-200 rounded-xl bg-gray-50">
          <p className="text-xs text-gray-500 font-medium mb-2">Select an avatar:</p>
          <div className="grid grid-cols-6 gap-2">
            {PRESET_AVATARS.map((av) => {
              const selected = value === av.url;
              return (
                <button
                  key={av.url}
                  type="button"
                  title={av.label}
                  onClick={() => {
                    onChange(selected ? undefined : av.url);
                    setOpen(false);
                  }}
                  className={`relative rounded-full w-10 h-10 overflow-hidden border-2 transition-all
                    ${selected
                      ? 'border-primary-500 ring-2 ring-primary-200'
                      : 'border-transparent hover:border-primary-300'}`}
                >
                  <img src={av.url} alt={av.label} className="w-full h-full object-cover" />
                  {selected && (
                    <div className="absolute inset-0 bg-primary-600/20 flex items-center justify-center">
                      <CheckCircle size={14} className="text-primary-700" />
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
