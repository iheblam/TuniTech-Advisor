import { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart2,
  Cpu,
  Search,
  GitCompare,
  CheckCircle2,
  XCircle,
  Store,
  Tag,
} from 'lucide-react';
import { getHealth, getDataStats, getBrands } from '../api/client';
import type { HealthResponse, DataStats } from '../types';
import Spinner from '../components/Spinner';

export default function HomePage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [stats, setStats] = useState<DataStats | null>(null);
  const [brandCount, setBrandCount] = useState<number | null>(null);
  const [brandList, setBrandList] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const STORES = [
    'Tunisianet',
    'Mytek',
    'SpaceNet',
    'BestBuyTunisie',
    'BestPhone',
  ];

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([getHealth(), getDataStats(), getBrands()]).then(([h, s, b]) => {
      if (h.status === 'fulfilled') setHealth(h.value);
      if (s.status === 'fulfilled') setStats(s.value);
      if (b.status === 'fulfilled') { setBrandCount(b.value.total); setBrandList(b.value.brands); }
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
            {/* Total phones – plain count-up */}
            <CountUpCard
              label="Total Phones"
              target={Number(stats.total_smartphones ?? 0)}
              suffix=" phones"
              hint="indexed across all stores"
            />
            {/* Stores – flip card */}
            <FlipCard
              label="Stores Covered"
              value={5}
              icon={<Store size={18} className="text-primary-500" />}
              backTitle="Where we scrape"
              items={STORES.map((s, i) => ({ label: s, color: STORE_COLORS[i] }))}
            />
            {/* Brands – flip card with pill cloud */}
            <FlipCard
              label="Brands Available"
              value={brandCount ?? 0}
              icon={<Tag size={18} className="text-primary-500" />}
              backTitle="All brands"
              items={brandList.map((b) => ({ label: b, color: 'bg-neutral-100 text-neutral-700' }))}
              pillCloud
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

const STORE_COLORS = [
  'bg-orange-100 text-orange-700',
  'bg-purple-100 text-purple-700',
  'bg-blue-100 text-blue-700',
  'bg-yellow-100 text-yellow-800',
  'bg-green-100 text-green-700',
];

// ── Count-up card ────────────────────────────────────────────────────────
function CountUpCard({ label, target, suffix, hint }: {
  label: string; target: number; suffix?: string; hint?: string;
}) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true;
        const duration = 1200;
        const steps = 40;
        const step = target / steps;
        let current = 0;
        const timer = setInterval(() => {
          current += step;
          if (current >= target) { setCount(target); clearInterval(timer); }
          else setCount(Math.round(current));
        }, duration / steps);
      }
    }, { threshold: 0.4 });
    io.observe(el);
    return () => io.disconnect();
  }, [target]);

  return (
    <div ref={ref} className="card text-center border-neutral-100 flex flex-col items-center justify-center gap-1">
      <p className="text-4xl font-extrabold text-primary-600 tabular-nums">
        {count.toLocaleString()}
        {suffix && <span className="text-base font-semibold text-neutral-400">{suffix}</span>}
      </p>
      <p className="text-sm font-semibold text-neutral-700">{label}</p>
      {hint && <p className="text-xs text-neutral-400">{hint}</p>}
    </div>
  );
}

// ── Flip card ──────────────────────────────────────────────────────────
function FlipCard({ label, value, icon, backTitle, items, pillCloud }: {
  label: string;
  value: number;
  icon: React.ReactNode;
  backTitle: string;
  items: { label: string; color: string }[];
  pillCloud?: boolean;
}) {
  const [flipped, setFlipped] = useState(false);
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true;
        const duration = 900;
        const steps = 30;
        const step = value / steps;
        let current = 0;
        const timer = setInterval(() => {
          current += step;
          if (current >= value) { setCount(value); clearInterval(timer); }
          else setCount(Math.round(current));
        }, duration / steps);
      }
    }, { threshold: 0.4 });
    io.observe(el);
    return () => io.disconnect();
  }, [value]);

  return (
    <div
      ref={ref}
      className="h-40 cursor-pointer"
      style={{ perspective: '1000px' }}
      onMouseEnter={() => setFlipped(true)}
      onMouseLeave={() => setFlipped(false)}
    >
      <div
        className="relative w-full h-full transition-transform duration-500"
        style={{ transformStyle: 'preserve-3d', transform: flipped ? 'rotateY(180deg)' : 'rotateY(0deg)' }}
      >
        {/* Front */}
        <div
          className="absolute inset-0 card border-neutral-100 flex flex-col items-center justify-center gap-1 select-none"
          style={{ backfaceVisibility: 'hidden' }}
        >
          <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center mb-1">{icon}</div>
          <p className="text-4xl font-extrabold text-primary-600 tabular-nums">{count}</p>
          <p className="text-sm font-semibold text-neutral-700">{label}</p>
          <p className="text-xs text-neutral-400">hover to reveal →</p>
        </div>

        {/* Back */}
        <div
          className="absolute inset-0 card border-primary-100 bg-primary-50 flex flex-col overflow-hidden select-none"
          style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
        >
          <p className="text-xs font-semibold text-primary-500 uppercase tracking-wider px-4 pt-3 pb-2 border-b border-primary-100">
            {backTitle}
          </p>
          <div className="flex-1 overflow-y-auto px-3 py-2">
            {pillCloud ? (
              <div className="flex flex-wrap gap-1.5">
                {items.map((item) => (
                  <span
                    key={item.label}
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${item.color}`}
                  >
                    {item.label}
                  </span>
                ))}
              </div>
            ) : (
              <ul className="space-y-1.5">
                {items.map((item) => (
                  <li key={item.label} className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full shrink-0 ${item.color.replace('text-', 'bg-').split(' ')[0]}`} />
                    <span className={`text-sm font-medium px-2 py-0.5 rounded-lg ${item.color}`}>{item.label}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
