import { useEffect, useState } from 'react';
import { TrendingUp, Eye, Search, Flame, Clock } from 'lucide-react';
import { getTrending, searchSmartphones } from '../api/client';
import type { SmartphoneDetail } from '../types';
import PhoneCard from '../components/PhoneCard';
import Spinner from '../components/Spinner';

interface TrendingEntry {
  phone_name: string;
  views: number;
  searches: number;
  score: number;
  last_seen: string;
}

function fmtRelative(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function TrendingPage() {
  const [trending, setTrending]         = useState<TrendingEntry[]>([]);
  const [phones, setPhones]             = useState<Record<string, SmartphoneDetail>>({});
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState('');

  useEffect(() => {
    setLoading(true);
    getTrending(12)
      .then(async (data) => {
        const entries = data.trending ?? [];
        setTrending(entries);
        // Resolve phone details for top entries (fire parallel searches)
        const resolved: Record<string, SmartphoneDetail> = {};
        await Promise.allSettled(
          entries.slice(0, 12).map(async (e) => {
            try {
              const res = await searchSmartphones(e.phone_name, undefined, undefined, 1);
              const phone = (res.results as SmartphoneDetail[])[0];
              if (phone) resolved[e.phone_name] = phone;
            } catch { /* silent */ }
          })
        );
        setPhones(resolved);
      })
      .catch(() => setError('Could not load trending data.'))
      .finally(() => setLoading(false));
  }, []);

  const rankColor = (i: number) => {
    if (i === 0) return 'bg-yellow-400 text-yellow-900';
    if (i === 1) return 'bg-gray-300 text-gray-700';
    if (i === 2) return 'bg-amber-500 text-amber-900';
    return 'bg-gray-100 text-gray-500';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-orange-100 text-orange-600">
            <Flame size={22} />
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900">Trending in Tunisia</h1>
        </div>
        <p className="text-gray-500 max-w-xl">
          The most viewed and searched phones by Tunisian users right now.
        </p>
      </div>

      {loading && <div className="flex justify-center py-20"><Spinner text="Loading trending phones…" /></div>}
      {error && <p className="text-red-500 text-sm">{error}</p>}

      {!loading && trending.length === 0 && (
        <div className="text-center py-20 text-gray-400">
          <TrendingUp size={56} className="mx-auto mb-4 opacity-25" />
          <p className="font-semibold text-lg">No trending data yet</p>
          <p className="text-sm mt-1">
            Start browsing and searching phones — the most popular ones will appear here.
          </p>
        </div>
      )}

      {!loading && trending.length > 0 && (
        <>
          {/* Top 3 podium */}
          {trending.slice(0, 3).length > 0 && (
            <div className="grid sm:grid-cols-3 gap-4 mb-10">
              {trending.slice(0, 3).map((entry, i) => (
                <div key={entry.phone_name} className="card relative overflow-hidden">
                  <div className={`absolute top-3 left-3 w-7 h-7 rounded-full flex items-center justify-center text-xs font-black ${rankColor(i)}`}>
                    {i + 1}
                  </div>
                  <div className="pt-6">
                    {phones[entry.phone_name] ? (
                      <PhoneCard phone={phones[entry.phone_name]} />
                    ) : (
                      <div className="p-4 pt-2">
                        <p className="font-semibold text-gray-800 text-sm leading-tight">{entry.phone_name}</p>
                      </div>
                    )}
                  </div>
                  <div className="px-4 pb-3 flex items-center gap-4 text-xs text-gray-400 border-t border-gray-100 pt-2 mt-1">
                    <span className="flex items-center gap-1"><Eye size={12} /> {entry.views} views</span>
                    <span className="flex items-center gap-1"><Search size={12} /> {entry.searches} searches</span>
                    <span className="flex items-center gap-1 ml-auto"><Clock size={12} /> {fmtRelative(entry.last_seen)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Full ranked list (4–12) */}
          {trending.slice(3).length > 0 && (
            <div className="card">
              <h2 className="font-bold text-gray-800 mb-4">More Trending</h2>
              <div className="divide-y divide-gray-100">
                {trending.slice(3).map((entry, i) => (
                  <div key={entry.phone_name} className="flex items-center gap-4 py-3">
                    <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${rankColor(i + 3)}`}>
                      {i + 4}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-800 text-sm truncate">{entry.phone_name}</p>
                      <p className="text-xs text-gray-400">
                        {phones[entry.phone_name]?.brand ?? ''}{phones[entry.phone_name]?.price ? ` · ${phones[entry.phone_name].price?.toLocaleString()} TND` : ''}
                      </p>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-400 shrink-0">
                      <span className="flex items-center gap-0.5"><Eye size={11} /> {entry.views}</span>
                      <span className="flex items-center gap-0.5"><Search size={11} /> {entry.searches}</span>
                    </div>
                    <span className="text-xs text-gray-300">{fmtRelative(entry.last_seen)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
