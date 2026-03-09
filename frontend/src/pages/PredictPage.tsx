import { useState, useEffect } from 'react';
import { Cpu, TrendingUp } from 'lucide-react';
import { predictPrice, getBrands } from '../api/client';
import type { PricePredictionRequest, PricePredictionResponse } from '../types';
import Spinner from '../components/Spinner';
import ErrorMsg from '../components/ErrorMsg';

const DEFAULT: PricePredictionRequest = {
  brand: '',
  features: {
    ram: 8,
    storage: 128,
    battery: 5000,
    screen_size: 6.5,
    main_camera: 64,
    front_camera: 16,
    processor_cores: 8,
    is_5g: false,
    has_nfc: false,
  },
};

export default function PredictPage() {
  const [form, setForm] = useState<PricePredictionRequest>(DEFAULT);
  const [brands, setBrands] = useState<string[]>([]);
  const [result, setResult] = useState<PricePredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getBrands()
      .then((d) => setBrands(d.brands))
      .catch(() => {});
  }, []);

  const setFeature = (key: keyof typeof form.features, value: number | boolean) => {
    setForm((prev) => ({ ...prev, features: { ...prev.features, [key]: value } }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const payload: PricePredictionRequest = {
        features: form.features,
        ...(form.brand ? { brand: form.brand } : {}),
      };
      const data = await predictPrice(payload);
      setResult(data);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? 'Prediction failed. Is the API running and model loaded?');
    } finally {
      setLoading(false);
    }
  };

  const f = form.features;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">AI Price Predictor</h1>
        <p className="text-gray-500 mt-1">
          Enter smartphone specifications and our ML model will estimate the fair market price in TND.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 items-start">
        {/* Form */}
        <form onSubmit={handleSubmit} className="card space-y-5">
          <div className="flex items-center gap-2 font-semibold text-gray-800">
            <Cpu size={18} className="text-indigo-500" />
            Specifications
          </div>

          {/* Brand */}
          <div>
            <label className="label">Brand (optional)</label>
            <select
              className="input"
              value={form.brand ?? ''}
              onChange={(e) => setForm({ ...form, brand: e.target.value || undefined })}
            >
              <option value="">Unknown / Generic</option>
              {brands.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <NumberField
              label="RAM (GB)"
              value={f.ram}
              min={1} max={64}
              onChange={(v) => setFeature('ram', v)}
            />
            <NumberField
              label="Storage (GB)"
              value={f.storage}
              min={16} max={1024}
              onChange={(v) => setFeature('storage', v)}
            />
            <NumberField
              label="Battery (mAh)"
              value={f.battery}
              min={1000} max={10000}
              onChange={(v) => setFeature('battery', v)}
            />
            <NumberField
              label="Screen Size (inches)"
              value={f.screen_size}
              min={3} max={10} step={0.1}
              onChange={(v) => setFeature('screen_size', v)}
            />
            <NumberField
              label="Main Camera (MP)"
              value={f.main_camera}
              min={2} max={200}
              onChange={(v) => setFeature('main_camera', v)}
            />
            <NumberField
              label="Front Camera (MP)"
              value={f.front_camera}
              min={2} max={100}
              onChange={(v) => setFeature('front_camera', v)}
            />
            <NumberField
              label="CPU Cores"
              value={f.processor_cores}
              min={2} max={16}
              onChange={(v) => setFeature('processor_cores', v)}
            />
          </div>

          <div className="flex gap-6">
            <Toggle
              label="5G"
              checked={f.is_5g}
              onChange={(v) => setFeature('is_5g', v)}
            />
            <Toggle
              label="NFC"
              checked={f.has_nfc}
              onChange={(v) => setFeature('has_nfc', v)}
            />
          </div>

          <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2">
            <TrendingUp size={16} />
            Predict Price
          </button>
        </form>

        {/* Result */}
        <div className="space-y-4">
          {loading && <Spinner text="Running ML prediction…" />}
          {!loading && error && <ErrorMsg message={error} />}
          {!loading && !error && result && (
            <div className="card space-y-5">
              <p className="font-semibold text-gray-700 flex items-center gap-2">
                <TrendingUp size={18} className="text-green-500" />
                Prediction Result
              </p>

              <div className="text-center space-y-1">
                <p className="text-5xl font-extrabold text-primary-700">
                  {result.predicted_price.toLocaleString('fr-TN', { maximumFractionDigits: 0 })}
                </p>
                <p className="text-lg text-gray-500 font-medium">TND</p>
              </div>

              {result.confidence_interval && (
                <div className="bg-blue-50 rounded-xl p-4 text-sm text-blue-700 text-center">
                  95% Confidence Interval:&nbsp;
                  <strong>
                    {result.confidence_interval.lower.toFixed(0)} –{' '}
                    {result.confidence_interval.upper.toFixed(0)} TND
                  </strong>
                </div>
              )}

              {result.model_info && (
                <div className="text-sm text-gray-500 space-y-1 border-t pt-4">
                  <p className="font-medium text-gray-700 mb-1">Model Info</p>
                  {Object.entries(result.model_info).map(([k, v]) => (
                    <div key={k} className="flex justify-between">
                      <span className="capitalize">{k.replace(/_/g, ' ')}</span>
                      <span className="font-medium text-gray-700">{String(v)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {!loading && !result && !error && (
            <div className="card text-center py-16 text-gray-400">
              <Cpu size={48} className="mx-auto mb-3 opacity-30" />
              <p>Fill in the specs and click <strong>Predict Price</strong></p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Helper sub-components ─────────────────────────────────────

function NumberField({
  label, value, min, max, step = 1, onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (v: number) => void;
}) {
  return (
    <div>
      <label className="label">{label}</label>
      <input
        type="number"
        className="input"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}

function Toggle({
  label, checked, onChange,
}: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="flex items-center gap-2 cursor-pointer select-none">
      <div
        className={`relative w-10 h-5 rounded-full transition-colors ${
          checked ? 'bg-primary-600' : 'bg-gray-300'
        }`}
        onClick={() => onChange(!checked)}
      >
        <div
          className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
            checked ? 'translate-x-5' : ''
          }`}
        />
      </div>
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </label>
  );
}
