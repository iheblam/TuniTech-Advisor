import { useState } from 'react';
import { GitCompare, Plus, X, BarChart2, Trophy, Zap, Camera, HardDrive, Battery, DollarSign, Star } from 'lucide-react';
import { searchSmartphones } from '../api/client';
import type { SmartphoneDetail } from '../types';
import Spinner from '../components/Spinner';
import ErrorMsg from '../components/ErrorMsg';

// higherIsBetter = true means the phone with the highest value wins
// higherIsBetter = false means the phone with the lowest value wins (price)
const SPEC_KEYS: {
  key: keyof SmartphoneDetail;
  label: string;
  unit?: string;
  higherIsBetter?: boolean; // undefined = text/bool, no numeric winner logic needed beyond presence
  boolWinner?: boolean; // true = having it (true) is the winner
}[] = [
  { key: 'price',        label: 'Price',        unit: 'TND',  higherIsBetter: false },
  { key: 'brand',        label: 'Brand' },
  { key: 'store',        label: 'Store' },
  { key: 'ram',          label: 'RAM',          unit: 'GB',   higherIsBetter: true },
  { key: 'storage',      label: 'Storage',      unit: 'GB',   higherIsBetter: true },
  { key: 'battery',      label: 'Battery',      unit: 'mAh',  higherIsBetter: true },
  { key: 'screen_size',  label: 'Screen',       unit: '"',    higherIsBetter: true },
  { key: 'main_camera',  label: 'Main Camera',  unit: 'MP',   higherIsBetter: true },
  { key: 'front_camera', label: 'Front Camera', unit: 'MP',   higherIsBetter: true },
  { key: 'processor',    label: 'Processor' },
  { key: 'is_5g',        label: '5G',           boolWinner: true },
  { key: 'has_nfc',      label: 'NFC',          boolWinner: true },
];

// Returns the index(es) of the winning phone(s) for a given spec row
function getWinnerIndexes(
  phones: SmartphoneDetail[],
  key: keyof SmartphoneDetail,
  higherIsBetter?: boolean,
  boolWinner?: boolean
): number[] {
  if (higherIsBetter !== undefined) {
    const vals = phones.map((p) => (p[key] as number | null | undefined) ?? null);
    const validVals = vals.filter((v) => v !== null) as number[];
    if (validVals.length === 0) return [];
    const best = higherIsBetter ? Math.max(...validVals) : Math.min(...validVals);
    return vals.map((v, i) => (v === best ? i : -1)).filter((i) => i !== -1);
  }
  if (boolWinner) {
    const winners = phones.map((p, i) => (p[key] === true ? i : -1)).filter((i) => i !== -1);
    return winners;
  }
  return [];
}

// Score each phone: count how many spec rows it wins
function scorePhones(phones: SmartphoneDetail[]): number[] {
  const scores = new Array(phones.length).fill(0);
  for (const { key, higherIsBetter, boolWinner } of SPEC_KEYS) {
    const winners = getWinnerIndexes(phones, key, higherIsBetter, boolWinner);
    if (winners.length === 1) scores[winners[0]]++;
  }
  return scores;
}

// Nickname for a phone in the summary
function nick(p: SmartphoneDetail) {
  return p.brand && p.brand !== 'Unknown' ? `${p.brand} (${p.store})` : p.name.split('/')[0].trim();
}

interface SummaryCard {
  icon: React.ReactNode;
  title: string;
  winner: string;
  reason: string;
  color: string;
}

function buildSummary(phones: SmartphoneDetail[]): SummaryCard[] {
  const cards: SummaryCard[] = [];

  // Best value for money
  const priceWinners = getWinnerIndexes(phones, 'price', false);
  if (priceWinners.length === 1) {
    cards.push({
      icon: <DollarSign size={18} />,
      title: 'Best for Budget',
      winner: nick(phones[priceWinners[0]]),
      reason: `Lowest price at ${phones[priceWinners[0]].price?.toLocaleString()} TND`,
      color: 'bg-green-50 border-green-200',
    });
  }

  // Best storage
  const storWinners = getWinnerIndexes(phones, 'storage', true);
  if (storWinners.length === 1 && phones[storWinners[0]].storage) {
    cards.push({
      icon: <HardDrive size={18} />,
      title: 'Best for Storage',
      winner: nick(phones[storWinners[0]]),
      reason: `Most storage: ${phones[storWinners[0]].storage} GB`,
      color: 'bg-blue-50 border-blue-200',
    });
  }

  // Best camera
  const camWinners = getWinnerIndexes(phones, 'main_camera', true);
  if (camWinners.length === 1 && phones[camWinners[0]].main_camera) {
    cards.push({
      icon: <Camera size={18} />,
      title: 'Best for Photos',
      winner: nick(phones[camWinners[0]]),
      reason: `Highest rear camera: ${phones[camWinners[0]].main_camera} MP`,
      color: 'bg-purple-50 border-purple-200',
    });
  }

  // Best battery
  const batWinners = getWinnerIndexes(phones, 'battery', true);
  if (batWinners.length === 1 && phones[batWinners[0]].battery) {
    cards.push({
      icon: <Battery size={18} />,
      title: 'Best Battery Life',
      winner: nick(phones[batWinners[0]]),
      reason: `Largest battery: ${phones[batWinners[0]].battery?.toLocaleString()} mAh`,
      color: 'bg-yellow-50 border-yellow-200',
    });
  }

  // Best performance (RAM)
  const ramWinners = getWinnerIndexes(phones, 'ram', true);
  if (ramWinners.length === 1 && phones[ramWinners[0]].ram) {
    cards.push({
      icon: <Zap size={18} />,
      title: 'Best for Performance',
      winner: nick(phones[ramWinners[0]]),
      reason: `Most RAM: ${phones[ramWinners[0]].ram} GB`,
      color: 'bg-orange-50 border-orange-200',
    });
  }

  // Overall winner
  const scores = scorePhones(phones);
  const maxScore = Math.max(...scores);
  const overallWinnerIdxs = scores.map((s, i) => (s === maxScore ? i : -1)).filter((i) => i !== -1);
  if (overallWinnerIdxs.length === 1) {
    cards.push({
      icon: <Star size={18} />,
      title: 'Best Overall',
      winner: nick(phones[overallWinnerIdxs[0]]),
      reason: `Wins ${maxScore} out of ${SPEC_KEYS.filter(s => s.higherIsBetter !== undefined || s.boolWinner).length} comparable specs`,
      color: 'bg-indigo-50 border-indigo-200',
    });
  }

  return cards;
}

export default function ComparePage() {
  const [searchQ, setSearchQ] = useState('');
  const [searchResults, setSearchResults] = useState<SmartphoneDetail[]>([]);
  const [selected, setSelected] = useState<SmartphoneDetail[]>([]);
  const [compareData, setCompareData] = useState<SmartphoneDetail[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);
  const [error, setError] = useState('');

  const doSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQ.trim()) return;
    setSearchLoading(true);
    setError('');
    try {
      const data = await searchSmartphones(searchQ);
      setSearchResults(data.results as SmartphoneDetail[]);
    } catch {
      setError('Search failed');
    } finally {
      setSearchLoading(false);
    }
  };

  const addToCompare = (phone: SmartphoneDetail) => {
    if (selected.length >= 4) return;
    if (selected.find((p) => p.name === phone.name && p.store === phone.store)) return;
    setSelected((prev) => [...prev, phone]);
  };

  const removeFromCompare = (i: number) => {
    setSelected((prev) => prev.filter((_, idx) => idx !== i));
    setCompareData([]);
  };

  const doCompare = async () => {
    setCompareLoading(true);
    setError('');
    await new Promise((r) => setTimeout(r, 300));
    setCompareData(selected);
    setCompareLoading(false);
  };

  const renderValue = (phone: SmartphoneDetail, key: keyof SmartphoneDetail, unit?: string) => {
    const val = phone[key];
    if (val == null || val === '') return <span className="text-gray-300">–</span>;
    if (typeof val === 'boolean') return val
      ? <span className="text-green-600 font-bold">✓ Yes</span>
      : <span className="text-red-400">✗ No</span>;
    return `${val}${unit ?? ''}`;
  };

  const summaryCards = compareData.length >= 2 ? buildSummary(compareData) : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900">Compare Smartphones</h1>
        <p className="text-gray-500 mt-1">Pick up to 4 phones and compare them side by side.</p>
      </div>

      {error && <ErrorMsg message={error} />}

      <div className="grid lg:grid-cols-[380px_1fr] gap-8 items-start">
        {/* ── Left: search + selection ── */}
        <div className="space-y-5">
          <div className="card space-y-3">
            <p className="font-semibold text-gray-800 flex items-center gap-2">
              <Plus size={16} className="text-primary-500" /> Add phones
            </p>
            <form onSubmit={doSearch} className="flex gap-2">
              <input
                type="text"
                className="input flex-1"
                placeholder="Search name or brand…"
                value={searchQ}
                onChange={(e) => setSearchQ(e.target.value)}
              />
              <button type="submit" className="btn-primary py-2 px-3">Search</button>
            </form>

            {searchLoading && <Spinner text="Searching…" />}

            {!searchLoading && searchResults.length > 0 && (
              <ul className="divide-y max-h-72 overflow-y-auto rounded-lg border border-gray-100">
                {searchResults.map((p, i) => {
                  const alreadyAdded = !!selected.find((x) => x.name === p.name && x.store === p.store);
                  return (
                    <li key={i} className="flex items-center justify-between px-3 py-2 hover:bg-gray-50">
                      <div>
                        <p className="text-sm font-medium text-gray-800 leading-tight">{p.name}</p>
                        <p className="text-xs text-gray-400">{p.store} · {p.price?.toLocaleString()} TND</p>
                      </div>
                      <button
                        className={`text-xs px-2 py-1 rounded-md font-medium transition-colors ${
                          alreadyAdded || selected.length >= 4
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-primary-600 text-white hover:bg-primary-700'
                        }`}
                        disabled={alreadyAdded || selected.length >= 4}
                        onClick={() => addToCompare(p)}
                      >
                        {alreadyAdded ? 'Added' : '+ Add'}
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div className="card space-y-3">
            <p className="font-semibold text-gray-800">Selected ({selected.length}/4)</p>
            {selected.length === 0 ? (
              <p className="text-sm text-gray-400">No phones selected yet.</p>
            ) : (
              <ul className="space-y-2">
                {selected.map((p, i) => (
                  <li key={i} className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2">
                    <div>
                      <p className="text-sm font-medium text-gray-800">{p.name}</p>
                      <p className="text-xs text-gray-400">{p.store}</p>
                    </div>
                    <button onClick={() => removeFromCompare(i)} className="text-gray-400 hover:text-red-500 transition-colors">
                      <X size={16} />
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <button
              className="btn-primary w-full flex items-center justify-center gap-2 mt-2"
              disabled={selected.length < 2}
              onClick={doCompare}
            >
              <GitCompare size={16} />
              Compare Now
            </button>
            {selected.length < 2 && (
              <p className="text-xs text-gray-400 text-center">Select at least 2 phones</p>
            )}
          </div>
        </div>

        {/* ── Right: comparison table ── */}
        <div className="space-y-6">
          {compareLoading && <Spinner text="Building comparison…" />}

          {!compareLoading && compareData.length === 0 && (
            <div className="card text-center py-24 text-gray-400">
              <BarChart2 size={48} className="mx-auto mb-3 opacity-30" />
              <p>Search phones, add them, then hit <strong>Compare Now</strong>.</p>
            </div>
          )}

          {!compareLoading && compareData.length > 0 && (
            <>
              {/* Comparison table */}
              <div className="overflow-x-auto card p-0">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="text-left px-4 py-3 text-gray-500 font-medium w-28">Spec</th>
                      {compareData.map((p, i) => (
                        <th key={i} className="text-left px-4 py-3 min-w-[160px]">
                          <div className="font-semibold text-gray-900 leading-tight">{p.name}</div>
                          <div className="text-xs text-gray-400 font-normal">{p.store}</div>
                        </th>
                      ))}
                      <th className="text-left px-4 py-3 text-gray-500 font-medium w-28">Winner</th>
                    </tr>
                  </thead>
                  <tbody>
                    {SPEC_KEYS.map(({ key, label, unit, higherIsBetter, boolWinner }) => {
                      const winnerIdxs = getWinnerIndexes(compareData, key, higherIsBetter, boolWinner);
                      const hasClearWinner = winnerIdxs.length === 1;
                      const isTied = winnerIdxs.length > 1;

                      return (
                        <tr key={key} className="border-b last:border-0 hover:bg-gray-50/50">
                          <td className="px-4 py-2.5 text-gray-500 font-medium">{label}</td>
                          {compareData.map((p, i) => {
                            const isWinner = winnerIdxs.includes(i);
                            return (
                              <td
                                key={i}
                                className={`px-4 py-2.5 font-medium transition-colors ${
                                  isWinner && hasClearWinner
                                    ? 'bg-green-50 text-green-800'
                                    : isWinner && isTied
                                    ? 'bg-yellow-50 text-yellow-800'
                                    : 'text-gray-800'
                                }`}
                              >
                                <div className="flex items-center gap-1">
                                  {isWinner && hasClearWinner && (
                                    <Trophy size={13} className="text-yellow-500 shrink-0" />
                                  )}
                                  {renderValue(p, key, unit)}
                                </div>
                              </td>
                            );
                          })}
                          {/* Winner column */}
                          <td className="px-4 py-2.5">
                            {hasClearWinner ? (
                              <span className="inline-flex items-center gap-1 text-xs font-semibold text-green-700 bg-green-100 rounded-full px-2 py-0.5">
                                <Trophy size={11} className="text-yellow-500" />
                                {nick(compareData[winnerIdxs[0]])}
                              </span>
                            ) : isTied ? (
                              <span className="text-xs text-yellow-600 font-medium">Tie</span>
                            ) : (
                              <span className="text-xs text-gray-300">–</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Summary cards */}
              {summaryCards.length > 0 && (
                <div>
                  <h2 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <Star size={18} className="text-yellow-500" />
                    Summary — Pick the right phone for you
                  </h2>
                  <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
                    {summaryCards.map((card, i) => (
                      <div key={i} className={`rounded-xl border p-4 ${card.color}`}>
                        <div className="flex items-center gap-2 mb-1 text-gray-700 font-semibold text-sm">
                          {card.icon}
                          {card.title}
                        </div>
                        <p className="text-base font-bold text-gray-900 truncate">{card.winner}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{card.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
