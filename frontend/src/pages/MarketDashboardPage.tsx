import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { Wifi, ShoppingBag, DollarSign, Cpu, Sparkles, Store } from 'lucide-react';
import { getMarketOverview, getAiInsight } from '../api/client';
import type { MarketOverviewResponse } from '../types';
import Spinner from '../components/Spinner';
import ErrorMsg from '../components/ErrorMsg';

const OS_COLORS  = ['#ea580c','#fb923c','#fbbf24','#34d399','#60a5fa','#c084fc'];
const NET_COLORS = ['#60a5fa','#ea580c','#a8a29e'];
const STORE_COLOR = '#ea580c';

const fmt = (n: number) => `${Math.round(n).toLocaleString('fr-TN')} TND`;

// ── AI Insight card ───────────────────────────────────────────────────────────

function AiInsightCard() {
  const [insight, setInsight] = useState('');
  const [loading, setLoading]  = useState(true);

  useEffect(() => {
    getAiInsight()
      .then((d) => setInsight(d.insight))
      .catch(() => setInsight('AI insight temporarily unavailable.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl p-6 shadow-lg text-white">
      {/* decorative blur blob */}
      <div className="absolute -top-6 -right-6 w-32 h-32 bg-white/10 rounded-full blur-2xl pointer-events-none" />
      <div className="relative flex items-start gap-4">
        <div className="w-11 h-11 rounded-xl bg-white/20 flex items-center justify-center shrink-0 mt-0.5">
          <Sparkles size={22} />
        </div>
        <div className="flex-1">
          <p className="text-sm font-semibold text-white/70 mb-1">AI Market Insight · Powered by Groq</p>
          {loading ? (
            <div className="space-y-2 animate-pulse">
              <div className="h-4 bg-white/20 rounded-full w-full" />
              <div className="h-4 bg-white/20 rounded-full w-4/5" />
              <div className="h-4 bg-white/20 rounded-full w-3/5" />
            </div>
          ) : (
            <p className="text-base leading-relaxed font-medium">{insight}</p>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function MarketDashboardPage() {
  const [data, setData]     = useState<MarketOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState('');

  useEffect(() => {
    getMarketOverview()
      .then(setData)
      .catch(() => setError('Failed to load market data. Is the API running?'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-20"><Spinner /></div>;
  if (error)   return <div className="max-w-xl mx-auto py-20"><ErrorMsg message={error} /></div>;
  if (!data)   return null;

  const { total_phones, five_g_pct, price_summary, price_segments,
          os_distribution, network_stats, store_stats, spec_averages } = data;

  const specEntries = Object.entries(spec_averages);

  return (
    <div className="min-h-screen bg-cozy-bg py-8 px-4">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold text-neutral-900 flex items-center gap-3">
            <ShoppingBag className="text-primary-600" size={30} />
            Market Dashboard
          </h1>
          <p className="mt-1 text-neutral-500 text-sm">
            Overview of the Tunisian smartphone retail market across 5 stores
          </p>
        </div>

        {/* AI Insight */}
        <AiInsightCard />

        {/* KPI row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total Phones',  value: total_phones.toLocaleString(), icon: <ShoppingBag size={18}/>, color: 'bg-primary-50 text-primary-600' },
            { label: 'Average Price', value: fmt(price_summary.mean),       icon: <DollarSign size={18}/>,  color: 'bg-accent-50 text-accent-600' },
            { label: 'Median Price',  value: fmt(price_summary.median),     icon: <DollarSign size={18}/>,  color: 'bg-green-50 text-green-600' },
            { label: '5G Adoption',   value: `${five_g_pct}%`,              icon: <Wifi size={18}/>,        color: 'bg-blue-50 text-blue-600' },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-cozy-card border border-cozy-border rounded-2xl p-4 flex items-center gap-3 shadow-sm">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${kpi.color}`}>
                {kpi.icon}
              </div>
              <div>
                <p className="text-xs text-neutral-500 font-medium">{kpi.label}</p>
                <p className="text-lg font-bold text-neutral-800 leading-tight">{kpi.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Spec averages chips */}
        {specEntries.length > 0 && (
          <div className="bg-cozy-card border border-cozy-border rounded-2xl p-5 shadow-sm">
            <h2 className="text-sm font-bold text-neutral-700 mb-3 flex items-center gap-2">
              <Cpu size={16} className="text-primary-500" /> Average Specs Across All Phones
            </h2>
            <div className="flex flex-wrap gap-3">
              {specEntries.map(([label, val]) => (
                <div key={label} className="flex items-center gap-2 bg-neutral-100 rounded-xl px-4 py-2">
                  <span className="text-xs text-neutral-500 font-medium">{label}</span>
                  <span className="text-sm font-bold text-neutral-800">{val}</span>
                </div>
              ))}
              <div className="flex items-center gap-2 bg-neutral-100 rounded-xl px-4 py-2">
                <span className="text-xs text-neutral-500 font-medium">Price Range</span>
                <span className="text-sm font-bold text-neutral-800">
                  {fmt(price_summary.min)} – {fmt(price_summary.max)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Price segments + OS distribution */}
        <div className="grid lg:grid-cols-5 gap-6">

          {/* Price segments bar chart */}
          <div className="lg:col-span-3 bg-cozy-card border border-cozy-border rounded-2xl p-5 shadow-sm">
            <h2 className="text-base font-bold text-neutral-800 mb-4">Phones by Price Segment</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={price_segments} margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e8ddd0" />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#78716c' }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(v: unknown) => [`${v} phones`, 'Count']}
                  contentStyle={{ borderRadius: 10, border: '1px solid #e8ddd0', background: '#fffaf4', fontSize: 12 }}
                />
                <Bar dataKey="count" fill={STORE_COLOR} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* OS distribution pie */}
          <div className="lg:col-span-2 bg-cozy-card border border-cozy-border rounded-2xl p-5 shadow-sm">
            <h2 className="text-base font-bold text-neutral-800 mb-4">OS Distribution</h2>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={os_distribution}
                  dataKey="count"
                  nameKey="os"
                  cx="50%" cy="45%"
                  outerRadius={90}
                  label={(props: { name?: string; percent?: number }) =>
                    (props.percent ?? 0) > 0.05 ? `${((props.percent ?? 0) * 100).toFixed(0)}%` : ''
                  }
                  labelLine={false}
                >
                  {os_distribution.map((_, i) => (
                    <Cell key={i} fill={OS_COLORS[i % OS_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(v: unknown, name: unknown) => [`${v} phones`, String(name)]}
                  contentStyle={{ borderRadius: 10, border: '1px solid #e8ddd0', background: '#fffaf4', fontSize: 12 }}
                />
                <Legend iconType="circle" iconSize={9} wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Store comparison */}
        <div className="bg-cozy-card border border-cozy-border rounded-2xl p-5 shadow-sm">
          <h2 className="text-base font-bold text-neutral-800 mb-1 flex items-center gap-2">
            <Store size={18} className="text-primary-500" /> Store Comparison
          </h2>
          <p className="text-xs text-neutral-500 mb-4">Listings count and average price per retailer</p>
          <div className="grid sm:grid-cols-2 gap-6">
            <div>
              <p className="text-xs font-semibold text-neutral-500 mb-2">Listings per Store</p>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={store_stats} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e8ddd0" />
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis dataKey="store" type="category" width={110} tick={{ fontSize: 12, fill: '#44403c' }} />
                  <Tooltip
                    formatter={(v: unknown) => [`${v} phones`, 'Count']}
                    contentStyle={{ borderRadius: 10, border: '1px solid #e8ddd0', background: '#fffaf4', fontSize: 12 }}
                  />
                  <Bar dataKey="count" fill="#ea580c" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div>
              <p className="text-xs font-semibold text-neutral-500 mb-2">Average Price per Store (TND)</p>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={[...store_stats].sort((a,b) => b.avg_price - a.avg_price)} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e8ddd0" />
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis dataKey="store" type="category" width={110} tick={{ fontSize: 12, fill: '#44403c' }} />
                  <Tooltip
                    formatter={(v: unknown) => [fmt(v as number), 'Avg Price']}
                    contentStyle={{ borderRadius: 10, border: '1px solid #e8ddd0', background: '#fffaf4', fontSize: 12 }}
                  />
                  <Bar dataKey="avg_price" fill="#fbbf24" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Network stats */}
        <div className="bg-cozy-card border border-cozy-border rounded-2xl p-5 shadow-sm">
          <h2 className="text-base font-bold text-neutral-800 mb-4 flex items-center gap-2">
            <Wifi size={18} className="text-blue-500" /> Network Generation Breakdown
          </h2>
          <div className="flex flex-wrap gap-4">
            {network_stats.map((n, i) => {
              const pct = Math.round(n.count / total_phones * 100);
              return (
                <div key={n.type} className="flex-1 min-w-[140px] bg-neutral-50 border border-cozy-border rounded-2xl p-4 text-center">
                  <div
                    className="text-3xl font-extrabold mb-1"
                    style={{ color: NET_COLORS[i % NET_COLORS.length] }}
                  >
                    {pct}%
                  </div>
                  <div className="text-sm font-bold text-neutral-700">{n.type}</div>
                  <div className="text-xs text-neutral-500 mt-0.5">{n.count.toLocaleString()} phones</div>
                  {/* progress bar */}
                  <div className="mt-2 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${pct}%`, background: NET_COLORS[i % NET_COLORS.length] }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
}
