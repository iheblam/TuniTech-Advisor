import { useState, useEffect } from 'react';
import { SlidersHorizontal, RefreshCw } from 'lucide-react';
import { getRecommendations, getBrands } from '../api/client';
import type { RecommendationRequest, SmartphoneDetail } from '../types';
import PhoneCard from '../components/PhoneCard';
import Spinner from '../components/Spinner';
import ErrorMsg from '../components/ErrorMsg';

const DEFAULT_FORM: RecommendationRequest = {
  budget_min: 500,
  budget_max: 2000,
  min_ram: undefined,
  min_storage: undefined,
  min_battery: undefined,
  min_camera: undefined,
  brand: undefined,
  requires_5g: undefined,
  limit: 12,
};

export default function RecommendPage() {
  const [form, setForm] = useState<RecommendationRequest>(DEFAULT_FORM);
  const [brands, setBrands] = useState<string[]>([]);
  const [results, setResults] = useState<SmartphoneDetail[]>([]);
  const [total, setTotal] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    getBrands()
      .then((d) => setBrands(d.brands))
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSubmitted(true);

    // Client-side validation
    if (form.budget_min != null && form.budget_max != null && form.budget_min > form.budget_max) {
      setError('Minimum budget cannot be greater than maximum budget.');
      setLoading(false);
      return;
    }

    try {
      // Strip undefined optional fields
      const payload: RecommendationRequest = {
        budget_min: form.budget_min,
        budget_max: form.budget_max,
        limit: form.limit,
        ...(form.min_ram && { min_ram: form.min_ram }),
        ...(form.min_storage && { min_storage: form.min_storage }),
        ...(form.min_battery && { min_battery: form.min_battery }),
        ...(form.min_camera && { min_camera: form.min_camera }),
        ...(form.brand && { brand: form.brand }),
        ...(form.requires_5g != null && { requires_5g: form.requires_5g }),
      };
      const data = await getRecommendations(payload);
      setResults(data.recommendations);
      setTotal(data.total_found);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      let msg: string;
      if (!detail) {
        msg = 'Failed to fetch recommendations. Is the API running?';
      } else if (typeof detail === 'string') {
        msg = detail;
      } else if (Array.isArray(detail)) {
        // Pydantic 422 validation errors: [{loc, msg, type, ...}]
        msg = detail.map((e: { msg?: string; loc?: string[] }) =>
          `${e.loc?.slice(1).join(' → ') ?? 'field'}: ${e.msg ?? 'invalid'}`
        ).join(' | ');
      } else {
        msg = JSON.stringify(detail);
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const num = (val: string) => (val === '' ? undefined : Number(val));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900">Smartphone Recommendations</h1>
        <p className="text-gray-500 mt-1">Set your budget and preferences — we'll find the best options.</p>
      </div>

      <div className="grid lg:grid-cols-[320px_1fr] gap-8 items-start">
        {/* ── Filter panel ── */}
        <aside>
          <form
            onSubmit={handleSubmit}
            className="card space-y-5 sticky top-20"
          >
            <div className="flex items-center gap-2 font-semibold text-gray-800">
              <SlidersHorizontal size={18} className="text-primary-500" />
              Filters
            </div>

            {/* Budget */}
            <div>
              <label className="label">Budget (TND)</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  className="input"
                  placeholder="Min"
                  value={form.budget_min}
                  min={0}
                  onChange={(e) => setForm({ ...form, budget_min: Number(e.target.value) })}
                />
                <input
                  type="number"
                  className="input"
                  placeholder="Max"
                  value={form.budget_max}
                  min={0}
                  onChange={(e) => setForm({ ...form, budget_max: Number(e.target.value) })}
                />
              </div>
            </div>

            {/* Brand */}
            <div>
              <label className="label">Brand</label>
              <select
                className="input"
                value={form.brand ?? ''}
                onChange={(e) => setForm({ ...form, brand: e.target.value || undefined })}
              >
                <option value="">Any brand</option>
                {brands.map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>

            {/* RAM */}
            <div>
              <label className="label">Minimum RAM (GB)</label>
              <select
                className="input"
                value={form.min_ram ?? ''}
                onChange={(e) => setForm({ ...form, min_ram: num(e.target.value) })}
              >
                <option value="">Any</option>
                {[2, 3, 4, 6, 8, 12, 16].map((v) => (
                  <option key={v} value={v}>{v} GB</option>
                ))}
              </select>
            </div>

            {/* Storage */}
            <div>
              <label className="label">Minimum Storage (GB)</label>
              <select
                className="input"
                value={form.min_storage ?? ''}
                onChange={(e) => setForm({ ...form, min_storage: num(e.target.value) })}
              >
                <option value="">Any</option>
                {[32, 64, 128, 256, 512].map((v) => (
                  <option key={v} value={v}>{v} GB</option>
                ))}
              </select>
            </div>

            {/* Battery */}
            <div>
              <label className="label">Minimum Battery (mAh)</label>
              <select
                className="input"
                value={form.min_battery ?? ''}
                onChange={(e) => setForm({ ...form, min_battery: num(e.target.value) })}
              >
                <option value="">Any</option>
                {[3000, 4000, 5000, 6000].map((v) => (
                  <option key={v} value={v}>{v.toLocaleString()}</option>
                ))}
              </select>
            </div>

            {/* Camera */}
            <div>
              <label className="label">Minimum Camera (MP)</label>
              <select
                className="input"
                value={form.min_camera ?? ''}
                onChange={(e) => setForm({ ...form, min_camera: num(e.target.value) })}
              >
                <option value="">Any</option>
                {[12, 48, 64, 108, 200].map((v) => (
                  <option key={v} value={v}>{v} MP</option>
                ))}
              </select>
            </div>

            {/* 5G */}
            <div>
              <label className="label">5G</label>
              <select
                className="input"
                value={form.requires_5g == null ? '' : form.requires_5g ? 'true' : 'false'}
                onChange={(e) =>
                  setForm({
                    ...form,
                    requires_5g:
                      e.target.value === '' ? undefined : e.target.value === 'true',
                  })
                }
              >
                <option value="">Doesn't matter</option>
                <option value="true">5G required</option>
                <option value="false">No 5G needed</option>
              </select>
            </div>

            {/* Limit */}
            <div>
              <label className="label">Results to show</label>
              <select
                className="input"
                value={form.limit}
                onChange={(e) => setForm({ ...form, limit: Number(e.target.value) })}
              >
                {[6, 12, 24, 48].map((v) => (
                  <option key={v} value={v}>{v}</option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2">
              <RefreshCw size={16} />
              Get Recommendations
            </button>
          </form>
        </aside>

        {/* ── Results ── */}
        <section>
          {loading && <Spinner text="Finding the best phones for you…" />}
          {!loading && error && <ErrorMsg message={error} />}
          {!loading && !error && submitted && (
            <div className="space-y-4">
              <p className="text-sm text-gray-500">
                {total != null ? (
                  <>Found <strong>{total}</strong> phones matching your criteria.</>
                ) : null}
              </p>
              {results.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                  No phones found. Try relaxing your filters.
                </div>
              ) : (
                <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {results.map((p, i) => (
                    <PhoneCard key={i} phone={p} />
                  ))}
                </div>
              )}
            </div>
          )}
          {!submitted && !loading && (
            <div className="text-center py-24 text-gray-400">
              <SlidersHorizontal size={48} className="mx-auto mb-3 opacity-30" />
              <p>Set your filters and click <strong>Get Recommendations</strong></p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
