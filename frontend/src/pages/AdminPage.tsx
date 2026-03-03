import { useState, useEffect, useCallback } from 'react';
import {
  LayoutDashboard, FlaskConical, ExternalLink, LogOut,
  RefreshCw, Play, CheckCircle, XCircle, Cpu,
  Database, BarChart2, ChevronRight, Upload, Tag,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  adminGetSystem,
  adminGetActiveModel,
  adminGetRuns,
  adminLogModel,
  adminStartMLflowUI,
  adminGetMLflowStatus,
} from '../api/client';
import Spinner from '../components/Spinner';

/* ── Types ────────────────────────────────────────────────── */
interface SystemInfo {
  model_loaded: boolean;
  data_loaded: boolean;
  data_rows: number;
  mlflow_uri: string;
  mlflow_experiment: string;
}

interface ActiveModel {
  loaded: boolean;
  name: string;
  algorithm: string;
  k: number;
  features: string;
  samples: number;
  brands: number;
  approx_mae: number;
  price_min: number;
  price_max: number;
  price_mean: number;
  brand_price_tiers: Record<string, number>;
}

interface MLRun {
  run_id: string;
  run_name: string;
  status: string;
  start_time: number;
  end_time: number | null;
  metrics: Record<string, number>;
  params: Record<string, string>;
  tags: Record<string, string>;
}

type Tab = 'dashboard' | 'runs' | 'mlflow';

/* ── Sub-components ─────────────────────────────────────────── */
function StatCard({ icon, label, value, sub, ok }: {
  icon: React.ReactNode; label: string; value: string; sub?: string; ok?: boolean;
}) {
  return (
    <div className="card flex items-start gap-4">
      <div className={`p-2.5 rounded-xl ${ok === undefined ? 'bg-primary-100 text-primary-700' : ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
        {icon}
      </div>
      <div>
        <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">{label}</p>
        <p className="text-lg font-bold text-gray-900 leading-tight">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

function Badge({ status }: { status: string }) {
  const map: Record<string, string> = {
    FINISHED: 'bg-green-100 text-green-700',
    RUNNING:  'bg-blue-100 text-blue-700',
    FAILED:   'bg-red-100 text-red-600',
    KILLED:   'bg-yellow-100 text-yellow-700',
  };
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${map[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  );
}

/* ── Main page ──────────────────────────────────────────────── */
export default function AdminPage() {
  const { user, logout, token } = useAuth();
  const [tab, setTab] = useState<Tab>('dashboard');

  const [system,      setSystem]      = useState<SystemInfo | null>(null);
  const [activeModel, setActiveModel] = useState<ActiveModel | null>(null);
  const [runs,        setRuns]        = useState<MLRun[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [loggingRun,  setLoggingRun]  = useState(false);
  const [logMsg,      setLogMsg]      = useState('');
  const [mlflowMsg,   setMlflowMsg]   = useState('');
  const [mlflowLive,  setMlflowLive]  = useState(false);

  const fetchAll = useCallback(async () => {
    if (!token) return;
    setLoadingData(true);
    try {
      const [sys, model, runsData] = await Promise.all([
        adminGetSystem(token),
        adminGetActiveModel(token),
        adminGetRuns(token),
      ]);
      setSystem(sys);
      setActiveModel(model);
      setRuns(runsData.runs ?? []);
    } catch (e) {
      console.error('Admin fetch error', e);
    } finally {
      setLoadingData(false);
    }
  }, [token]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // Ping MLflow UI via backend (avoids browser ERR_CONNECTION_REFUSED noise)
  useEffect(() => {
    if (!token) return;
    adminGetMLflowStatus(token)
      .then((r) => setMlflowLive(r.running))
      .catch(() => setMlflowLive(false));
  }, [token, mlflowMsg]);

  const handleLogModel = async () => {
    if (!token) return;
    setLoggingRun(true);
    setLogMsg('');
    try {
      const r = await adminLogModel(token);
      setLogMsg(`✓ Logged as run ${r.run_id.slice(0, 8)} in "${r.experiment}"`);
      await fetchAll();
    } catch {
      setLogMsg('✗ Failed to log run');
    } finally {
      setLoggingRun(false);
    }
  };

  const handleStartMLflow = async () => {
    if (!token) return;
    try {
      const r = await adminStartMLflowUI(token);
      setMlflowMsg(r.message);
    } catch {
      setMlflowMsg('Failed to start MLflow UI');
    }
  };

  const fmtTime = (ms: number | null) =>
    ms ? new Date(ms).toLocaleString() : '—';

  const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Dashboard',   icon: <LayoutDashboard size={16} /> },
    { id: 'runs',      label: 'MLflow Runs', icon: <FlaskConical size={16} /> },
    { id: 'mlflow',    label: 'MLflow UI',   icon: <ExternalLink size={16} /> },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900">Admin Panel</h1>
          <p className="text-gray-500 mt-1">
            Logged in as <span className="font-semibold text-primary-600">{user?.username}</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchAll}
            className="btn-secondary flex items-center gap-2 text-sm"
            disabled={loadingData}
          >
            <RefreshCw size={15} className={loadingData ? 'animate-spin' : ''} />
            Refresh
          </button>
          <button
            onClick={logout}
            className="flex items-center gap-2 text-sm px-4 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut size={15} />
            Logout
          </button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b border-gray-200">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg border-b-2 transition-colors -mb-px ${
              tab === t.id
                ? 'border-primary-600 text-primary-700 bg-primary-50'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {loadingData && tab !== 'mlflow' && (
        <div className="py-10"><Spinner text="Loading admin data…" /></div>
      )}

      {/* ── DASHBOARD TAB ─────────────────────────────────── */}
      {!loadingData && tab === 'dashboard' && (
        <div className="space-y-8">
          {/* System stat cards */}
          <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <StatCard
              icon={<Cpu size={20} />}
              label="Model"
              value={system?.model_loaded ? 'Loaded' : 'Not Loaded'}
              sub={activeModel?.name}
              ok={system?.model_loaded}
            />
            <StatCard
              icon={<Database size={20} />}
              label="Dataset"
              value={system?.data_loaded ? `${system.data_rows.toLocaleString()} phones` : 'Not Loaded'}
              sub={system?.data_loaded ? 'unified_smartphones_filled.csv' : undefined}
              ok={system?.data_loaded}
            />
            <StatCard
              icon={<BarChart2 size={20} />}
              label="Approx MAE"
              value={activeModel ? `${activeModel.approx_mae} TND` : '—'}
              sub="Leave-one-out estimate"
            />
            <StatCard
              icon={<FlaskConical size={20} />}
              label="MLflow Runs"
              value={String(runs.length)}
              sub={system?.mlflow_experiment}
            />
          </div>

          {/* Active model detail */}
          {activeModel && (
            <div className="grid lg:grid-cols-2 gap-6">
              <div className="card space-y-4">
                <h2 className="font-bold text-gray-900 flex items-center gap-2">
                  <Cpu size={16} className="text-primary-500" />
                  Active Model
                </h2>
                <table className="w-full text-sm">
                  <tbody>
                    {[
                      ['Name',       activeModel.name],
                      ['Algorithm',  activeModel.algorithm],
                      ['K',          String(activeModel.k)],
                      ['Features',   activeModel.features],
                      ['Samples',    activeModel.samples?.toLocaleString()],
                      ['Brands',     String(activeModel.brands)],
                      ['MAE',        `${activeModel.approx_mae} TND`],
                      ['Price range',`${activeModel.price_min} – ${activeModel.price_max} TND`],
                      ['Price mean', `${activeModel.price_mean?.toFixed(0)} TND`],
                    ].map(([k, v]) => (
                      <tr key={k} className="border-b last:border-0">
                        <td className="py-1.5 pr-4 text-gray-400 font-medium w-32">{k}</td>
                        <td className="py-1.5 text-gray-800">{v}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Log to MLflow */}
                <div className="pt-2 border-t">
                  <button
                    onClick={handleLogModel}
                    disabled={loggingRun}
                    className="btn-primary flex items-center gap-2 text-sm"
                  >
                    {loggingRun
                      ? <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                      : <Upload size={15} />
                    }
                    Log to MLflow
                  </button>
                  {logMsg && (
                    <p className={`text-xs mt-2 ${logMsg.startsWith('✓') ? 'text-green-600' : 'text-red-500'}`}>
                      {logMsg}
                    </p>
                  )}
                </div>
              </div>

              {/* Brand price tiers */}
              <div className="card space-y-3 overflow-hidden">
                <h2 className="font-bold text-gray-900 flex items-center gap-2">
                  <Tag size={16} className="text-primary-500" />
                  Brand Price Tiers (avg TND)
                </h2>
                <div className="overflow-y-auto max-h-72">
                  {Object.entries(activeModel.brand_price_tiers ?? {}).map(([brand, avg]) => {
                    const max = Math.max(...Object.values(activeModel.brand_price_tiers));
                    const pct = Math.round((avg / max) * 100);
                    return (
                      <div key={brand} className="flex items-center gap-3 py-1.5 border-b last:border-0">
                        <span className="text-xs font-medium text-gray-600 w-20 capitalize">{brand}</span>
                        <div className="flex-1 bg-gray-100 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-primary-500"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500 w-16 text-right">{avg.toLocaleString()} TND</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── RUNS TAB ──────────────────────────────────────── */}
      {!loadingData && tab === 'runs' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-gray-900">{runs.length} MLflow Run{runs.length !== 1 ? 's' : ''}</h2>
            <button
              onClick={handleLogModel}
              disabled={loggingRun}
              className="btn-primary flex items-center gap-2 text-sm"
            >
              {loggingRun
                ? <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                : <Upload size={15} />}
              Log Active Model
            </button>
          </div>

          {logMsg && (
            <p className={`text-sm ${logMsg.startsWith('✓') ? 'text-green-600' : 'text-red-500'}`}>{logMsg}</p>
          )}

          {runs.length === 0 ? (
            <div className="card text-center py-16 text-gray-400">
              <FlaskConical size={48} className="mx-auto mb-3 opacity-30" />
              <p className="font-medium">No runs yet.</p>
              <p className="text-sm mt-1">Hit "Log Active Model" to create the first one.</p>
            </div>
          ) : (
            <div className="overflow-x-auto card p-0">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left px-4 py-3 text-gray-500 font-medium">Run</th>
                    <th className="text-left px-4 py-3 text-gray-500 font-medium">Status</th>
                    <th className="text-left px-4 py-3 text-gray-500 font-medium">Started</th>
                    <th className="text-left px-4 py-3 text-gray-500 font-medium">MAE</th>
                    <th className="text-left px-4 py-3 text-gray-500 font-medium">Params</th>
                    <th className="text-left px-4 py-3 text-gray-500 font-medium">Tags</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((r) => (
                    <tr key={r.run_id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="font-medium text-gray-900">{r.run_name}</div>
                        <div className="text-xs text-gray-400 font-mono">{r.run_id.slice(0, 12)}…</div>
                      </td>
                      <td className="px-4 py-3"><Badge status={r.status} /></td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{fmtTime(r.start_time)}</td>
                      <td className="px-4 py-3">
                        {r.metrics.approx_mae != null
                          ? <span className="font-semibold text-primary-700">{r.metrics.approx_mae} TND</span>
                          : <span className="text-gray-300">—</span>}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {Object.entries(r.params).slice(0, 3).map(([k, v]) => (
                            <span key={k} className="text-xs bg-gray-100 text-gray-600 rounded px-1.5 py-0.5">
                              {k}={v}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {Object.entries(r.tags).slice(0, 2).map(([k, v]) => (
                            <span key={k} className="text-xs bg-indigo-100 text-indigo-700 rounded px-1.5 py-0.5">
                              {k}: {v}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── MLFLOW UI TAB ─────────────────────────────────── */}
      {tab === 'mlflow' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <h2 className="font-bold text-gray-900">MLflow UI</h2>
              <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${mlflowLive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                {mlflowLive ? <CheckCircle size={12} /> : <XCircle size={12} />}
                {mlflowLive ? 'Running on :5000' : 'Not Running'}
              </span>
            </div>
            <div className="flex gap-2 flex-wrap">
              {!mlflowLive && (
                <button
                  onClick={handleStartMLflow}
                  className="btn-primary flex items-center gap-2 text-sm"
                >
                  <Play size={14} /> Start MLflow UI
                </button>
              )}
              <a
                href="http://localhost:5000"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary flex items-center gap-2 text-sm"
              >
                <ExternalLink size={14} /> Open in New Tab
              </a>
            </div>
          </div>

          {mlflowMsg && (
            <p className="text-sm text-green-600 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
              {mlflowMsg} — refresh in a few seconds then click below.
            </p>
          )}

          {mlflowLive ? (
            <div className="card text-center py-20 space-y-5">
              <FlaskConical size={56} className="mx-auto text-blue-500 opacity-60" />
              <div>
                <p className="font-semibold text-gray-800 text-lg">MLflow UI is running on port 5000</p>
                <p className="text-sm text-gray-500 mt-1">
                  MLflow blocks embedding in iframes. Open it directly in a new tab.
                </p>
              </div>
              <a
                href="http://localhost:5000"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center gap-2"
              >
                <ExternalLink size={16} /> Open MLflow Dashboard
              </a>
            </div>
          ) : (
            <div className="card text-center py-20 text-gray-400 space-y-4">
              <FlaskConical size={56} className="mx-auto opacity-20" />
              <div>
                <p className="font-semibold text-gray-600">MLflow UI is not running</p>
                <p className="text-sm mt-1">Click <strong>Start MLflow UI</strong> above, wait ~3 seconds, then click <strong>Refresh</strong>.</p>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-left inline-block mx-auto">
                <p className="text-xs text-gray-400 mb-1">Or start manually:</p>
                <code className="text-xs text-gray-700 font-mono">
                  mlflow ui --backend-store-uri ./mlruns --port 5000
                </code>
              </div>
              <div className="flex justify-center">
                <button
                  onClick={() => {
                    if (!token) return;
                    adminGetMLflowStatus(token)
                      .then((r) => setMlflowLive(r.running))
                      .catch(() => setMlflowLive(false));
                  }}
                  className="btn-secondary flex items-center gap-2 text-sm"
                >
                  <RefreshCw size={14} /> Check Again
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
