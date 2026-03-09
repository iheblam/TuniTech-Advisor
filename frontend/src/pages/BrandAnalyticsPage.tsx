import { useEffect, useState } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts';
import { TrendingUp, Award, Package, ExternalLink } from 'lucide-react';
import { getBrandAnalytics } from '../api/client';
import type { BrandAnalyticsResponse, BrandStat } from '../types';
import Spinner from '../components/Spinner';
import ErrorMsg from '../components/ErrorMsg';

// Warm palette matching the app theme
const COLORS = [
  '#ea580c','#fb923c','#fbbf24','#34d399',
  '#60a5fa','#c084fc','#f472b6','#a3e635',
  '#38bdf8','#fb7185','#818cf8','#4ade80',
];

const fmt = (n: number) => `${n.toLocaleString('fr-TN')} TND`;

// Custom label for the donut pie
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const renderCustomLabel = (props: Record<string, any>) => {
  const { cx, cy, midAngle, innerRadius, outerRadius, percent = 0 } = props;
  if (percent < 0.04) return null;
  const RADIAN = Math.PI / 180;
  const r = innerRadius + (outerRadius - innerRadius) * 0.55;
  const x = cx + r * Math.cos(-midAngle * RADIAN);
  const y = cy + r * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central"
      fontSize={11} fontWeight={600}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export default function BrandAnalyticsPage() {
  const [data, setData] = useState<BrandAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getBrandAnalytics()
      .then(setData)
      .catch(() => setError('Failed to load brand analytics. Is the API running?'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-20"><Spinner /></div>;
  if (error)   return <div className="max-w-xl mx-auto py-20"><ErrorMsg message={error} /></div>;
  if (!data)   return null;

  const { total_phones, brands } = data;
  const topBrand = brands[0];
  const avgMarket = Math.round(brands.reduce((s, b) => s + b.avg_price * b.count, 0) / total_phones);

  // Best-value picks (brands that have a best_value_phone)
  const valuePicks = brands.filter((b) => b.best_value_phone).slice(0, 6);

  return (
    <div className="min-h-screen bg-cozy-bg py-8 px-4">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold text-neutral-900 flex items-center gap-3">
            <TrendingUp className="text-primary-600" size={30} />
            Brand Analytics
          </h1>
          <p className="mt-1 text-neutral-500 text-sm">
            Market share and pricing analysis across {brands.length} brands — {total_phones.toLocaleString()} phones listed
          </p>
        </div>

        {/* KPI row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total Listings', value: total_phones.toLocaleString(), icon: <Package size={18}/>, color: 'bg-primary-50 text-primary-600' },
            { label: 'Market Leader', value: topBrand.brand, icon: <Award size={18}/>, color: 'bg-accent-50 text-accent-600' },
            { label: 'Leader Share', value: `${topBrand.share_pct}%`, icon: <TrendingUp size={18}/>, color: 'bg-green-50 text-green-600' },
            { label: 'Market Avg Price', value: fmt(avgMarket), icon: <TrendingUp size={18}/>, color: 'bg-blue-50 text-blue-600' },
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

        {/* Charts row */}
        <div className="grid lg:grid-cols-2 gap-6">

          {/* Donut – market share */}
          <div className="bg-cozy-card border border-cozy-border rounded-2xl p-5 shadow-sm">
            <h2 className="text-base font-bold text-neutral-800 mb-4">Market Share by Listings</h2>
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={brands}
                  dataKey="count"
                  nameKey="brand"
                  cx="50%" cy="50%"
                  innerRadius={75} outerRadius={130}
                  labelLine={false}
                  label={renderCustomLabel}
                >
                  {brands.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(v: unknown, name: unknown) => [`${v} phones`, String(name)]}
                  contentStyle={{ borderRadius: 10, border: '1px solid #e8ddd0', background: '#fffaf4', fontSize: 12 }}
                />
                <Legend iconType="circle" iconSize={10} wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Horizontal bar – avg price per brand */}
          <div className="bg-cozy-card border border-cozy-border rounded-2xl p-5 shadow-sm">
            <h2 className="text-base font-bold text-neutral-800 mb-4">Average Price by Brand (TND)</h2>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart
                data={[...brands].sort((a, b) => b.avg_price - a.avg_price)}
                layout="vertical"
                margin={{ left: 10, right: 20, top: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e8ddd0" />
                <XAxis type="number" tickFormatter={(v) => `${v}`} tick={{ fontSize: 11 }} />
                <YAxis dataKey="brand" type="category" width={72} tick={{ fontSize: 12, fill: '#44403c' }} />
                <Tooltip
                  formatter={(v: unknown) => [fmt(v as number), 'Avg Price']}
                  contentStyle={{ borderRadius: 10, border: '1px solid #e8ddd0', background: '#fffaf4', fontSize: 12 }}
                />
                <Bar dataKey="avg_price" radius={[0, 6, 6, 0]}>
                  {brands.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Price range table */}
        <div className="bg-cozy-card border border-cozy-border rounded-2xl p-5 shadow-sm overflow-x-auto">
          <h2 className="text-base font-bold text-neutral-800 mb-4">Brand Price Ranges</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-cozy-border text-left text-neutral-500 text-xs uppercase tracking-wide">
                <th className="pb-3 font-semibold">Brand</th>
                <th className="pb-3 font-semibold text-right">Listings</th>
                <th className="pb-3 font-semibold text-right">Share</th>
                <th className="pb-3 font-semibold text-right">Min</th>
                <th className="pb-3 font-semibold text-right">Avg</th>
                <th className="pb-3 font-semibold text-right">Max</th>
              </tr>
            </thead>
            <tbody>
              {brands.map((b: BrandStat, i) => (
                <tr key={b.brand} className="border-b border-cozy-border/50 hover:bg-neutral-50 transition-colors">
                  <td className="py-2.5 font-semibold text-neutral-800 flex items-center gap-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ background: COLORS[i % COLORS.length] }}
                    />
                    {b.brand}
                  </td>
                  <td className="py-2.5 text-right text-neutral-600">{b.count}</td>
                  <td className="py-2.5 text-right">
                    <span className="bg-primary-50 text-primary-700 text-xs font-semibold px-2 py-0.5 rounded-full">
                      {b.share_pct}%
                    </span>
                  </td>
                  <td className="py-2.5 text-right text-green-700 font-medium">{fmt(b.min_price)}</td>
                  <td className="py-2.5 text-right text-neutral-700 font-semibold">{fmt(b.avg_price)}</td>
                  <td className="py-2.5 text-right text-neutral-500">{fmt(b.max_price)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Best Value picks */}
        <div>
          <h2 className="text-base font-bold text-neutral-800 mb-4">Best Value Pick per Brand</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {valuePicks.map((b, i) => {
              const phone = b.best_value_phone!;
              return (
                <div
                  key={b.brand}
                  className="bg-cozy-card border border-cozy-border rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className="text-xs font-bold px-2.5 py-1 rounded-full text-white"
                      style={{ background: COLORS[i % COLORS.length] }}
                    >
                      {b.brand}
                    </span>
                    <span className="text-lg font-extrabold text-primary-600">{fmt(phone.price)}</span>
                  </div>
                  <p className="text-sm font-semibold text-neutral-800 leading-tight mb-2 line-clamp-2">{phone.name}</p>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {phone.ram && (
                      <span className="text-xs bg-neutral-100 text-neutral-600 px-2 py-0.5 rounded-full">{phone.ram} GB RAM</span>
                    )}
                    {phone.storage && (
                      <span className="text-xs bg-neutral-100 text-neutral-600 px-2 py-0.5 rounded-full">{phone.storage} GB</span>
                    )}
                    {phone.store && (
                      <span className="text-xs bg-accent-50 text-accent-700 px-2 py-0.5 rounded-full">{phone.store}</span>
                    )}
                  </div>
                  {phone.url && (
                    <a
                      href={phone.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium"
                    >
                      View listing <ExternalLink size={12} />
                    </a>
                  )}
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
}
