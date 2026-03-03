import { useState, useRef } from 'react';
import { Search } from 'lucide-react';
import { searchSmartphones } from '../api/client';
import type { SmartphoneDetail } from '../types';
import PhoneCard from '../components/PhoneCard';
import Spinner from '../components/Spinner';
import ErrorMsg from '../components/ErrorMsg';

const STORES = ['All Stores', 'Tunisianet', 'SpaceNet', 'Mytek', 'BestBuyTunisie', 'BestPhone'];

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [selectedStore, setSelectedStore] = useState('All Stores');
  const [results, setResults] = useState<SmartphoneDetail[]>([]);
  const [total, setTotal] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    setSearched(true);
    try {
      const data = await searchSmartphones(
        query,
        minPrice ? Number(minPrice) : undefined,
        maxPrice ? Number(maxPrice) : undefined,
        50,
        selectedStore !== 'All Stores' ? selectedStore : undefined
      );
      setResults(data.results as SmartphoneDetail[]);
      setTotal(data.total_found);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? 'Search failed. Is the API running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900">Search Smartphones</h1>
        <p className="text-gray-500 mt-1">Search by model name or brand across all Tunisian stores.</p>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex flex-wrap gap-3 mb-8">
        <div className="relative flex-1 min-w-[200px]">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          />
          <input
            ref={inputRef}
            type="text"
            className="input pl-9"
            placeholder='e.g. "Samsung Galaxy" or "iPhone"'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <input
          type="number"
          className="input w-32"
          placeholder="Min price"
          value={minPrice}
          min={0}
          onChange={(e) => setMinPrice(e.target.value)}
        />
        <input
          type="number"
          className="input w-32"
          placeholder="Max price"
          value={maxPrice}
          min={0}
          onChange={(e) => setMaxPrice(e.target.value)}
        />
        <select
          className="input w-40"
          value={selectedStore}
          onChange={(e) => setSelectedStore(e.target.value)}
        >
          {STORES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button type="submit" className="btn-primary flex items-center gap-2">
          <Search size={16} />
          Search
        </button>
      </form>

      {/* Results */}
      {loading && <Spinner text="Searching…" />}
      {!loading && error && <ErrorMsg message={error} />}
      {!loading && !error && searched && (
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            {total != null && (
              <>
                {total === 0 ? 'No results' : (
                  <>Found <strong>{total}</strong> phone{total !== 1 ? 's' : ''}</>
                )}
                {query && <> for "<strong>{query}</strong>"</>}
                {selectedStore !== 'All Stores' && <> in <strong>{selectedStore}</strong></>}
              </>
            )}
          </p>
          {results.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              No smartphones matched your query. Try a different keyword.
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {results.map((p, i) => (
                <PhoneCard key={i} phone={p} />
              ))}
            </div>
          )}
        </div>
      )}

      {!searched && !loading && (
        <div className="text-center py-24 text-gray-400">
          <Search size={48} className="mx-auto mb-3 opacity-30" />
          <p>Type a brand or model name to get started.</p>
        </div>
      )}
    </div>
  );
}
