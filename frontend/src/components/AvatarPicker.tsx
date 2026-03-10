import { useState } from 'react';
import { CheckCircle2, X } from 'lucide-react';

// ── Avatar catalogue ──────────────────────────────────────────────────────────
const db = (style: string, seed: string, extra = '') =>
  `https://api.dicebear.com/7.x/${style}/svg?seed=${seed}${extra}`;

const CATEGORIES = [
  {
    id: 'emoji',
    label: '😄 Fun',
    avatars: [
      { url: db('fun-emoji', 'Felix'),   label: 'Felix'   },
      { url: db('fun-emoji', 'Aneka'),   label: 'Aneka'   },
      { url: db('fun-emoji', 'Luna'),    label: 'Luna'    },
      { url: db('fun-emoji', 'Mango'),   label: 'Mango'   },
      { url: db('fun-emoji', 'Kiki'),    label: 'Kiki'    },
      { url: db('fun-emoji', 'Niko'),    label: 'Niko'    },
      { url: db('fun-emoji', 'Zara'),    label: 'Zara'    },
      { url: db('fun-emoji', 'Pixel'),   label: 'Pixel'   },
    ],
  },
  {
    id: 'human',
    label: '🧑 Human',
    avatars: [
      { url: db('avataaars', 'Leo',   '&backgroundColor=b6e3f4'), label: 'Leo'   },
      { url: db('avataaars', 'Sara',  '&backgroundColor=ffd5dc'), label: 'Sara'  },
      { url: db('avataaars', 'Max',   '&backgroundColor=c0aede'), label: 'Max'   },
      { url: db('avataaars', 'Zoe',   '&backgroundColor=d1f4cc'), label: 'Zoe'   },
      { url: db('avataaars', 'Amir',  '&backgroundColor=b6e3f4'), label: 'Amir'  },
      { url: db('avataaars', 'Nadia', '&backgroundColor=ffd5dc'), label: 'Nadia' },
      { url: db('avataaars', 'Jake',  '&backgroundColor=ffdfbf'), label: 'Jake'  },
      { url: db('avataaars', 'Sofia', '&backgroundColor=c0aede'), label: 'Sofia' },
    ],
  },
  {
    id: 'robot',
    label: '🤖 Robot',
    avatars: [
      { url: db('bottts', 'R2D2',    '&backgroundColor=b6e3f4'), label: 'R2D2'    },
      { url: db('bottts', 'Cyborg',  '&backgroundColor=c0aede'), label: 'Cyborg'  },
      { url: db('bottts', 'Bolt',    '&backgroundColor=d1f4cc'), label: 'Bolt'    },
      { url: db('bottts', 'Circuit', '&backgroundColor=ffd5dc'), label: 'Circuit' },
      { url: db('bottts', 'Nova',    '&backgroundColor=ffdfbf'), label: 'Nova'    },
      { url: db('bottts', 'Glitch',  '&backgroundColor=b6e3f4'), label: 'Glitch'  },
      { url: db('bottts', 'Pixel',   '&backgroundColor=c0aede'), label: 'Pixel'   },
      { url: db('bottts', 'Zeta',    '&backgroundColor=d1f4cc'), label: 'Zeta'    },
    ],
  },
  {
    id: 'pixel',
    label: '👾 Pixel',
    avatars: [
      { url: db('pixel-art', 'Jasper', '&backgroundColor=b6e3f4'), label: 'Jasper'  },
      { url: db('pixel-art', 'Ruby',   '&backgroundColor=ffd5dc'), label: 'Ruby'    },
      { url: db('pixel-art', 'Storm',  '&backgroundColor=c0aede'), label: 'Storm'   },
      { url: db('pixel-art', 'Forge',  '&backgroundColor=d1f4cc'), label: 'Forge'   },
      { url: db('pixel-art', 'Blaze',  '&backgroundColor=ffdfbf'), label: 'Blaze'   },
      { url: db('pixel-art', 'Ember',  '&backgroundColor=ffd5dc'), label: 'Ember'   },
      { url: db('pixel-art', 'Atlas',  '&backgroundColor=b6e3f4'), label: 'Atlas'   },
      { url: db('pixel-art', 'Vex',    '&backgroundColor=c0aede'), label: 'Vex'     },
    ],
  },
  {
    id: 'lorelei',
    label: '🎨 Art',
    avatars: [
      { url: db('lorelei', 'Alice', '&backgroundColor=b6e3f4'), label: 'Alice'   },
      { url: db('lorelei', 'Bruno', '&backgroundColor=d1f4cc'), label: 'Bruno'   },
      { url: db('lorelei', 'Cleo',  '&backgroundColor=ffd5dc'), label: 'Cleo'    },
      { url: db('lorelei', 'Diego', '&backgroundColor=c0aede'), label: 'Diego'   },
      { url: db('lorelei', 'Elena', '&backgroundColor=ffdfbf'), label: 'Elena'   },
      { url: db('lorelei', 'Finn',  '&backgroundColor=b6e3f4'), label: 'Finn'    },
      { url: db('lorelei', 'Gaia',  '&backgroundColor=d1f4cc'), label: 'Gaia'    },
      { url: db('lorelei', 'Hiro',  '&backgroundColor=ffd5dc'), label: 'Hiro'    },
    ],
  },
  {
    id: 'micah',
    label: '✏️ Sketch',
    avatars: [
      { url: db('micah', 'Aria',  '&backgroundColor=b6e3f4'), label: 'Aria'    },
      { url: db('micah', 'Blake', '&backgroundColor=ffd5dc'), label: 'Blake'   },
      { url: db('micah', 'Cairo', '&backgroundColor=c0aede'), label: 'Cairo'   },
      { url: db('micah', 'Dani',  '&backgroundColor=d1f4cc'), label: 'Dani'    },
      { url: db('micah', 'Echo',  '&backgroundColor=ffdfbf'), label: 'Echo'    },
      { url: db('micah', 'Fable', '&backgroundColor=b6e3f4'), label: 'Fable'   },
      { url: db('micah', 'Grid',  '&backgroundColor=ffd5dc'), label: 'Grid'    },
      { url: db('micah', 'Hero',  '&backgroundColor=c0aede'), label: 'Hero'    },
    ],
  },
];

export const PRESET_AVATARS = CATEGORIES.flatMap((c) => c.avatars);

interface AvatarPickerProps {
  value: string | undefined;
  onChange: (url: string | undefined) => void;
}

export default function AvatarPicker({ value, onChange }: AvatarPickerProps) {
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(CATEGORIES[0].id);

  const currentCategory = CATEGORIES.find((c) => c.id === activeTab)!;

  return (
    <div>
      <label className="label">
        Profile Avatar{' '}
        <span className="text-gray-400 text-xs">(optional)</span>
      </label>

      {/* Preview row */}
      <div className="flex items-center gap-4 mt-1">
        <div
          className="w-16 h-16 rounded-full border-2 border-dashed border-primary-300 bg-gray-50
                     flex items-center justify-center overflow-hidden shrink-0 shadow-sm
                     transition-all hover:border-primary-500 cursor-pointer"
          onClick={() => setOpen(true)}
        >
          {value ? (
            <img src={value} alt="avatar" className="w-full h-full object-contain" />
          ) : (
            <span className="text-3xl select-none">🙂</span>
          )}
        </div>

        <div className="flex flex-col gap-1">
          <button
            type="button"
            onClick={() => setOpen(true)}
            className="btn-secondary text-sm py-1.5 px-3"
          >
            {value ? 'Change avatar' : 'Choose avatar'}
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
          <p className="text-xs text-gray-400">
            {CATEGORIES.length} styles · {PRESET_AVATARS.length}+ avatars
          </p>
        </div>
      </div>

      {/* Modal */}
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
          onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
        >
          <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-neutral-100">
              <div>
                <p className="font-bold text-neutral-900">Choose your avatar</p>
                <p className="text-xs text-neutral-400 mt-0.5">{CATEGORIES.length} styles available</p>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="p-1.5 rounded-lg text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Category tabs */}
            <div className="flex gap-1 px-4 pt-3 pb-1 overflow-x-auto scrollbar-none">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => setActiveTab(cat.id)}
                  className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap ${
                    activeTab === cat.id
                      ? 'bg-primary-600 text-white shadow-sm'
                      : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Avatar grid */}
            <div className="flex-1 overflow-y-auto p-4">
              <div className="grid grid-cols-4 gap-3">
                {currentCategory.avatars.map((av) => {
                  const selected = value === av.url;
                  return (
                    <button
                      key={av.url}
                      type="button"
                      onClick={() => { onChange(av.url); setOpen(false); }}
                      className="flex flex-col items-center gap-1.5 group"
                    >
                      <div
                        className={`relative w-16 h-16 rounded-2xl overflow-hidden border-2 transition-all duration-200 ${
                          selected
                            ? 'border-primary-500 ring-4 ring-primary-100 scale-105'
                            : 'border-transparent group-hover:border-primary-300 group-hover:scale-105'
                        }`}
                      >
                        <img
                          src={av.url}
                          alt={av.label}
                          loading="lazy"
                          className="w-full h-full object-contain"
                          onError={(e) => { (e.target as HTMLImageElement).style.opacity = '0.2'; }}
                        />
                        {selected && (
                          <div className="absolute inset-0 bg-primary-600/15 flex items-center justify-center">
                            <CheckCircle2 size={20} className="text-primary-600 drop-shadow" />
                          </div>
                        )}
                      </div>
                      <span className={`text-xs font-medium transition-colors ${
                        selected ? 'text-primary-600' : 'text-neutral-500 group-hover:text-neutral-800'
                      }`}>
                        {av.label}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Footer */}
            {value && (
              <div className="px-4 py-3 border-t border-neutral-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <img src={value} alt="current" className="w-7 h-7 rounded-full border border-neutral-200 object-contain" />
                  <span className="text-xs text-neutral-500">Current selection</span>
                </div>
                <button
                  type="button"
                  onClick={() => { onChange(undefined); setOpen(false); }}
                  className="text-xs text-red-500 hover:text-red-600 font-medium"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

