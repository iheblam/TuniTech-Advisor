import { useState } from 'react';
import { Wallet, Sliders, Zap, Cpu, HardDrive, Battery } from 'lucide-react';
import { getRecommendations } from '../api/client';
import type { SmartphoneDetail } from '../types';
import PhoneCard from '../components/PhoneCard';
import Spinner from '../components/Spinner';

const PRESETS = [
  { label: 'Entry (< 500 TND)',    min: 0,    max: 500  },
  { label: 'Mid (500–1200 TND)',   min: 500,  max: 1200 },
  { label: 'High (1200–2500 TND)', min: 1200, max: 2500 },
  { label: 'Flagship (> 2500 TND)',min: 2500, max: 99999 },
];

export default function BudgetOptimizerPage() {
  const [budgetMin, setBudgetMin]     = useState('');
  const [budgetMax, setBudgetMax]     = useState('');
  const [minRam, setMinRam]           = useState('');
  const [minStorage, setMinStorage]   = useState('');
  const [minBattery, setMinBattery]   = useState('');
  const [needs5g, setNeeds5g]         = useState(false);
  const [brand, setBrand]             = useState('');
  const [results, setResults]         = useState<SmartphoneDetail[]>([]);
  const [total, setTotal]             = useState<number | null>(null);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState('');
  const [searched, setSearched]       = useState(false);

  const applyPreset = (min: number, max: number) => {
    setBudgetMin(String(min === 0 ? '' : min));
    setBudgetMax(String(max === 99999 ? '' : max));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const min = budgetMin ? Number(budgetMin) : 0;
    const max = budgetMax ? Number(budgetMax) : 99999;
    if (min > max) { setError('Min budget cannot exceed max budget.'); return; }
    setLoading(true);
    setError('');
    setSearched(true);
    try {
      const data = await getRecommendations({
        budget_min: min,
        budget_max: max,
        min_ram:     minRam     ? Number(minRam)     : undefined,
        min_storage: minStorage ? Number(minStorage) : undefined,
        min_battery: minBattery ? Number(minBattery) : undefined,
        requires_5g: needs5g || undefined,
        brand:       brand.trim() || undefined,
        limit: 24,
      });
      setResults(data.recommendations ?? []);
      setTotal(data.total_found ?? 0);
    } catch {
      setError('Could not fetch recommendations. Is the API running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-primary-100 text-primary-700">
            <Wallet size={22} />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">Budget Optimizer</h1>
        </div>
        <p className="text-gray-500 max-w-xl">
          Set your budget and preferences — we'll find the best value phones available in Tunisia right now.
        </p>
      </div>

      {/* Filter card */}
      <form onSubmit={handleSubmit} className="card mb-8 space-y-6">
        {/* Budget preset chips */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Budget Preset</label>
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((p) => (
              <button
                key={p.label}
                type="button"
                onClick={() => applyPreset(p.min, p.max)}
                className={`text-sm px-4 py-1.5 rounded-full border transition-colors ${
                  budgetMin === String(p.min === 0 ? '' : p.min) && budgetMax === String(p.max === 99999 ? '' : p.max)
                    ? 'bg-primary-600 text-white border-primary-600'
                    : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Budget inputs */}
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Min Budget (TND)</label>
            <input
              type="number" min={0} value={budgetMin}
              onChange={(e) => setBudgetMin(e.target.value)}
              placeholder="0"
              className="input w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Max Budget (TND)</label>
            <input
              type="number" min={0} value={budgetMax}
              onChange={(e) => setBudgetMax(e.target.value)}
              placeholder="No limit"
              className="input w-full"
            />
          </div>
        </div>

        {/* Advanced filters */}
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
            <Sliders size={14} /> Advanced Filters
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                <Cpu size={12} /> Min RAM (GB)
              </label>
              <select value={minRam} onChange={(e) => setMinRam(e.target.value)} className="input w-full">
                <option value="">Any</option>
                {[4,6,8,12,16].map(v => <option key={v} value={v}>{v} GB</option>)}
              </select>
            </div>
            <div>
              <label className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                <HardDrive size={12} /> Min Storage (GB)
              </label>
              <select value={minStorage} onChange={(e) => setMinStorage(e.target.value)} className="input w-full">
                <option value="">Any</option>
                {[32,64,128,256,512].map(v => <option key={v} value={v}>{v} GB</option>)}
              </select>
            </div>
            <div>
              <label className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                <Battery size={12} /> Min Battery (mAh)
              </label>
              <select value={minBattery} onChange={(e) => setMinBattery(e.target.value)} className="input w-full">
                <option value="">Any</option>
                {[3000,4000,5000,6000].map(v => <option key={v} value={v}>{v.toLocaleString()}</option>)}
              </select>
            </div>
            <div>
              <label className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                Brand
              </label>
              <input
                type="text" value={brand}
                onChange={(e) => setBrand(e.target.value)}
                placeholder="Any brand"
                className="input w-full"
              />
            </div>
          </div>

          <label className="flex items-center gap-2 mt-3 cursor-pointer w-fit">
            <input type="checkbox" checked={needs5g} onChange={(e) => setNeeds5g(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-400" />
            <Zap size={13} className="text-blue-500" />
            <span className="text-sm text-gray-700">5G only</span>
          </label>
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full sm:w-auto">
          {loading ? <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : <Wallet size={14} />}
          {loading ? 'Finding best deals…' : 'Find Best Phones'}
        </button>
      </form>

      {/* Error */}
      {error && <p className="text-red-600 text-sm mb-4 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>}

      {/* Results */}
      {loading && (
        <div className="flex justify-center py-20"><Spinner text="Optimizing for your budget…" /></div>
      )}

      {!loading && searched && (
        <>
          <div className="mb-4 text-sm text-gray-500">
            {total != null ? <><span className="font-bold text-gray-800">{total}</span> phones found</> : null}
          </div>
          {results.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <Wallet size={48} className="mx-auto mb-3 opacity-30" />
              <p className="font-medium">No phones match your criteria.</p>
              <p className="text-sm mt-1">Try relaxing your filters or increasing the budget.</p>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              {results.map((p, i) => <PhoneCard key={i} phone={p} />)}
            </div>
          )}
        </>
      )}
    </div>
  );
}
