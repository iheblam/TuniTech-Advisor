import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart2,
  Cpu,
  Search,
  GitCompare,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { getHealth, getDataStats, getBrands } from '../api/client';
import type { HealthResponse, DataStats } from '../types';
import Spinner from '../components/Spinner';

export default function HomePage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [stats, setStats] = useState<DataStats | null>(null);
  const [brandCount, setBrandCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([getHealth(), getDataStats(), getBrands()]).then(([h, s, b]) => {
      if (h.status === 'fulfilled') setHealth(h.value);
      if (s.status === 'fulfilled') setStats(s.value);
      if (b.status === 'fulfilled') setBrandCount(b.value.total);
      setLoading(false);
    });
  }, []);

  const features = [
    {
      icon: <BarChart2 size={28} className="text-primary-600" />,
      title: 'Smart Recommendations',
      desc: 'Find your perfect smartphone filtered by budget, RAM, camera, battery and more.',
      to: '/recommend',
      color: 'bg-primary-50 border-primary-100',
    },
    {
      icon: <Cpu size={28} className="text-accent-600" />,
      title: 'AI Price Predictor',
      desc: 'Enter specs and let our ML model estimate a fair market price in TND.',
      to: '/predict',
      color: 'bg-accent-50 border-accent-100',
    },
    {
      icon: <Search size={28} className="text-primary-500" />,
      title: 'Search Smartphones',
      desc: 'Search any device by name or brand across all Tunisian stores.',
      to: '/search',
      color: 'bg-primary-50 border-primary-100',
    },
    {
      icon: <GitCompare size={28} className="text-accent-500" />,
      title: 'Side-by-Side Compare',
      desc: 'Compare up to 4 smartphones spec-by-spec to make the best decision.',
      to: '/compare',
      color: 'bg-accent-50 border-accent-100',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-14">
      {/* Hero */}
      <section className="text-center space-y-5">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-neutral-900 leading-tight">
          Find Your Perfect{' '}
          <span className="text-primary-600">Smartphone</span> in Tunisia
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          TuniTech Advisor aggregates smartphones from Tunisianet, Mytek, SpaceNet, BestBuyTunisie & BestPhone,
          then uses AI to recommend, predict prices, and compare devices for you.
        </p>
        <div className="flex flex-wrap justify-center gap-3 pt-2">
          <Link to="/recommend" className="btn-primary">
            Get Recommendations
          </Link>
          <Link to="/search" className="btn-secondary">
            Search Devices
          </Link>
        </div>
      </section>

      {/* Status strip */}
      <section className="card flex flex-wrap gap-6 items-center justify-center text-sm">
        {loading ? (
          <Spinner text="Checking API…" />
        ) : (
          <>
            <StatusPill ok={health?.status === 'healthy'} label="API" />
            <StatusPill ok={!!health?.model_loaded} label="ML Model" />
            <StatusPill ok={!!health?.data_loaded} label="Dataset" />
            {stats?.total_smartphones != null && (
              <span className="text-gray-600">
                📦 <strong>{Number(stats.total_smartphones).toLocaleString()}</strong> phones indexed
              </span>
            )}
            {health?.version && (
              <span className="text-gray-400">v{health.version}</span>
            )}
          </>
        )}
      </section>

      {/* Feature cards */}
      <section>
        <h2 className="text-2xl font-bold text-neutral-800 mb-6 text-center">What can you do?</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {features.map((f) => (
            <Link
              key={f.to}
              to={f.to}
              className={`rounded-2xl border p-5 flex flex-col gap-3 hover:shadow-md hover:-translate-y-0.5 transition-all group ${f.color}`}
            >
              <div>{f.icon}</div>
              <h3 className="font-semibold text-neutral-900 group-hover:text-primary-700">
                {f.title}
              </h3>
              <p className="text-sm text-neutral-500 leading-relaxed">{f.desc}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Stats */}
      {stats && !loading && (
        <section>
          <h2 className="text-2xl font-bold text-neutral-800 mb-6 text-center">Dataset at a glance</h2>
          <div className="grid sm:grid-cols-3 gap-5">
            <StatCard
              label="Total Phones"
              value={Number(stats.total_smartphones ?? 0).toLocaleString()}
            />
            <StatCard
              label="Stores Covered"
              value="5"
            />
            <StatCard
              label="Brands Available"
              value={brandCount != null ? String(brandCount) : '–'}
            />
          </div>
        </section>
      )}
    </div>
  );
}

function StatusPill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className={`flex items-center gap-1.5 font-medium ${ok ? 'text-primary-600' : 'text-red-500'}`}>
      {ok ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
      {label}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="card text-center border-neutral-100">
      <p className="text-3xl font-extrabold text-primary-600">{value}</p>
      <p className="text-sm text-neutral-500 mt-1">{label}</p>
    </div>
  );
}
