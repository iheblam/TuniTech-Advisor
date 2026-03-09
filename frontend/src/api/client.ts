import axios from 'axios';
import type {
  PricePredictionRequest,
  PricePredictionResponse,
  RecommendationRequest,
  RecommendationResponse,
  HealthResponse,
  DataStats,
  SearchResult,
  TokenResponse,
  AdminInfo,
  UserProfile,
  RegisterPayload,
  ProfileUpdatePayload,
  ChangePasswordPayload,
  BrandAnalyticsResponse,
  MarketOverviewResponse,
} from '../types';

// In development / docker-compose: VITE_API_BASE_URL is not set,
// so we use '/api/v1' which is proxied by Vite dev server or nginx.
// In cloud (Render, Fly, etc.): set VITE_API_BASE_URL to the full backend URL
// e.g. https://tunitech-api.onrender.com/api/v1
const BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const http = axios.create({ baseURL: BASE });

// ─── Auth ─────────────────────────────────────────────────────
export const loginAdmin = async (username: string, password: string): Promise<TokenResponse> => {
  const form = new URLSearchParams();
  form.append('username', username);
  form.append('password', password);
  const r = await http.post<TokenResponse>('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return r.data;
};

export const loginUser = (username: string, password: string): Promise<TokenResponse> =>
  http.post<TokenResponse>('/auth/user-login', { username, password }).then((r) => r.data);

export const registerUser = (payload: RegisterPayload): Promise<TokenResponse> =>
  http.post<TokenResponse>('/auth/register', payload).then((r) => r.data);

export const getMe = (token: string): Promise<AdminInfo> =>
  http.get<AdminInfo>('/auth/me', { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data);

export const getProfile = (token: string): Promise<UserProfile> =>
  http.get<UserProfile>('/auth/me/profile', { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data);

export const updateProfile = (token: string, data: ProfileUpdatePayload): Promise<UserProfile> =>
  http.put<UserProfile>('/auth/me/profile', data, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data);

export const changePassword = (token: string, data: ChangePasswordPayload): Promise<{ message: string }> =>
  http.post<{ message: string }>('/auth/me/change-password', data, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.data);

// ─── Admin helpers ─────────────────────────────────────────────
const authHeaders = (token: string) => ({ headers: { Authorization: `Bearer ${token}` } });

export const adminGetSystem = (token: string) =>
  http.get('/admin/system', authHeaders(token)).then((r) => r.data);

export const adminGetActiveModel = (token: string) =>
  http.get('/admin/model/active', authHeaders(token)).then((r) => r.data);

export const adminGetRuns = (token: string) =>
  http.get('/admin/runs', authHeaders(token)).then((r) => r.data);

export const adminLogModel = (token: string) =>
  http.post('/admin/model/log', null, authHeaders(token)).then((r) => r.data);

export const adminStartMLflowUI = (token: string) =>
  http.post('/admin/mlflow-ui/start', null, authHeaders(token)).then((r) => r.data);

export const adminGetMLflowStatus = (token: string) =>
  http.get<{ running: boolean; url: string | null }>('/admin/mlflow-ui/status', authHeaders(token)).then((r) => r.data);

// ─── Health ──────────────────────────────────────────────────
export const getHealth = () =>
  http.get<HealthResponse>('/health/').then((r) => r.data);

export const getDataStats = () =>
  http.get<DataStats>('/health/data-stats').then((r) => r.data);

export const getBrands = () =>
  http.get<{ total: number; brands: string[] }>('/health/brands').then((r) => r.data);

export const getModelInfo = () =>
  http.get<Record<string, unknown>>('/health/model-info').then((r) => r.data);

// ─── Predictions ─────────────────────────────────────────────
export const predictPrice = (req: PricePredictionRequest) =>
  http.post<PricePredictionResponse>('/predict/price', req).then((r) => r.data);

// ─── Recommendations ─────────────────────────────────────────
export const getRecommendations = (req: RecommendationRequest) =>
  http.post<RecommendationResponse>('/recommendations/', req).then((r) => r.data);

export const searchSmartphones = (
  query: string,
  min_price?: number,
  max_price?: number,
  limit = 50,
  store?: string
) =>
  http
    .get<SearchResult>('/recommendations/search', {
      params: { query, min_price, max_price, limit, store },
    })
    .then((r) => r.data);

export const compareSmartphones = (ids: number[]) =>
  http
    .get<{ total: number; smartphones: unknown[] }>('/recommendations/compare', {
      params: { ids: ids.join(',') },
    })
    .then((r) => r.data);

// ─── Phone image (localStorage-persisted cache) ──────────────────────────────
const IMG_CACHE_KEY = 'tuniTech_imgCache_v2';  // bumped: v1 had empty-array entries for failed lookups

// Load the entire cache from localStorage into memory once at startup
const _imgCache: Record<string, string[]> = (() => {
  try {
    return JSON.parse(localStorage.getItem(IMG_CACHE_KEY) ?? '{}');
  } catch {
    return {};
  }
})();

const _saveImgCache = () => {
  try {
    localStorage.setItem(IMG_CACHE_KEY, JSON.stringify(_imgCache));
  } catch {
    // localStorage full — clear old entries and retry
    localStorage.removeItem(IMG_CACHE_KEY);
  }
};

// ─── Analytics ───────────────────────────────────────────────
export const getBrandAnalytics = (): Promise<BrandAnalyticsResponse> =>
  http.get<BrandAnalyticsResponse>('/analytics/brands').then((r) => r.data);

export const getMarketOverview = (): Promise<MarketOverviewResponse> =>
  http.get<MarketOverviewResponse>('/analytics/market').then((r) => r.data);

export const getAiInsight = (): Promise<{ insight: string }> =>
  http.get<{ insight: string }>('/analytics/ai-insight').then((r) => r.data);

// ─── Scheduler ───────────────────────────────────────────────
export interface SchedulerStoreResult {
  status: 'ok' | 'error';
  count: number;
  error?: string;
}

export interface SchedulerStatus {
  running: boolean;
  last_run: string | null;
  next_run: string | null;
  started_at: string | null;
  elapsed_sec: number | null;
  current_store: string | null;
  interval_hours: number;
  include_mytek: boolean;
  last_results: Record<string, SchedulerStoreResult>;
  live_results: Record<string, SchedulerStoreResult>;
  logs: string[];
}

export const getSchedulerStatus = (): Promise<SchedulerStatus> =>
  http.get<SchedulerStatus>('/scheduler/status').then((r) => r.data);

export const triggerSchedulerNow = (token: string): Promise<{ status: string; message?: string }> =>
  http
    .post<{ status: string; message?: string }>('/scheduler/run-now', null, {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then((r) => r.data);

export const setSchedulerInterval = (token: string, hours: number): Promise<{ message: string }> =>
  http
    .post<{ message: string }>('/scheduler/set-interval', { hours }, {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then((r) => r.data);

export const getPhoneImage = (
  name: string,
  brand: string,
  url?: string
): Promise<{ image_urls: string[]; source: string }> => {
  const key = `${brand}|${name}`;
  if (key in _imgCache) {
    return Promise.resolve({ image_urls: _imgCache[key], source: 'cache' });
  }
  return http
    .get<{ image_urls: string[]; source: string }>('/recommendations/phone-image', {
      params: { name, brand, url },
    })
    .then((r) => {
      const urls = r.data.image_urls ?? [];
      if (urls.length > 0) {
        // Only cache successful results so phones with no image are retried later
        _imgCache[key] = urls;
        _saveImgCache();
      }
      return r.data;
    });
};

// ─── Community ────────────────────────────────────────────────

export const getReviews = (phoneName: string) =>
  http.get(`/community/reviews/${encodeURIComponent(phoneName)}`).then((r) => r.data as {
    phone_name: string;
    stats: { count: number; avg_rating: number | null };
    reviews: Array<{ id: string; username: string; rating: number; comment: string; date: string }>;
  });

export const addReview = (token: string, phoneName: string, rating: number, comment: string) =>
  http.post(
    `/community/reviews/${encodeURIComponent(phoneName)}`,
    { rating, comment },
    { headers: { Authorization: `Bearer ${token}` } }
  ).then((r) => r.data);

export const deleteReview = (token: string, phoneName: string, reviewId: string) =>
  http.delete(
    `/community/reviews/${encodeURIComponent(phoneName)}`,
    {
      headers: { Authorization: `Bearer ${token}` },
      params: { review_id: reviewId },
    }
  ).then((r) => r.data);

/** Fire-and-forget view/search event tracking */
export const trackEvent = (phoneName: string, eventType: 'view' | 'search' = 'view') => {
  http.post(`/community/track/${encodeURIComponent(phoneName)}`, { event_type: eventType }).catch(() => {});
};

export const getTrending = (limit = 12): Promise<{
  trending: Array<{ phone_name: string; views: number; searches: number; score: number; last_seen: string }>;
}> =>
  http.get(`/community/trending?limit=${limit}`).then((r) => r.data);

export const getPriceHistory = (phoneName: string, store?: string): Promise<{
  phone_name: string; store: string;
  history: Array<{ date: string; price: number; store?: string }>;
}> =>
  http.get(
    `/community/price-history/${encodeURIComponent(phoneName)}${store ? `?store=${encodeURIComponent(store)}` : ''}`
  ).then((r) => r.data);

