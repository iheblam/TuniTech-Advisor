// ─── API Types ────────────────────────────────────────────────

export interface SmartphoneFeatures {
  ram: number;
  storage: number;
  battery: number;
  screen_size: number;
  main_camera: number;
  front_camera: number;
  processor_cores: number;
  is_5g: boolean;
  has_nfc: boolean;
}

export interface PricePredictionRequest {
  features: SmartphoneFeatures;
  brand?: string;
}

export interface PricePredictionResponse {
  predicted_price: number;
  confidence_interval?: { lower: number; upper: number };
  model_info: Record<string, unknown>;
}

export interface RecommendationRequest {
  budget_min: number;
  budget_max: number;
  min_ram?: number;
  min_storage?: number;
  min_battery?: number;
  min_camera?: number;
  brand?: string;
  requires_5g?: boolean;
  limit?: number;
}

export interface SmartphoneDetail {
  name: string;
  brand: string;
  price: number;
  store: string;
  url?: string;
  ram?: number;
  storage?: number;
  battery?: number;
  screen_size?: number;
  main_camera?: number;
  front_camera?: number;
  processor?: string;
  is_5g?: boolean;
  has_nfc?: boolean;
  availability?: string;
  match_score?: number;
}

export interface RecommendationResponse {
  total_found: number;
  recommendations: SmartphoneDetail[];
  filters_applied: Record<string, unknown>;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  model_loaded: boolean;
  data_loaded: boolean;
}

export interface DataStats {
  total_smartphones?: number;
  brands?: number | string[];
  price?: { min: number; max: number; mean: number; median: number };
  [key: string]: unknown;
}

export interface SearchResult {
  query: string;
  total_found: number;
  results: SmartphoneDetail[];
}

// ─── Auth ────────────────────────────────────────────────────
export interface TokenResponse {
  access_token: string;
  token_type: string;
  username: string;
  role: string;
}

export interface AdminInfo {
  username: string;
  role: string;
}

export type Occupation = 'student' | 'employee' | 'freelancer' | 'self_employed' | 'other';
export type JoinReason = 'searching_phone' | 'comparing_prices' | 'reading_reviews' | 'browsing';

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  age?: number;
  occupation?: Occupation;
  avatar?: string;          // URL (online preset) or base64 data-URL
  favourite_brand?: string;
  current_phone?: string;
  join_reason?: JoinReason;
  created_at: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  age?: number;
  occupation?: Occupation;
  avatar?: string;
  favourite_brand?: string;
  current_phone?: string;
  join_reason?: JoinReason;
}

export interface ProfileUpdatePayload {
  email?: string;
  age?: number;
  occupation?: Occupation;
  avatar?: string;
  favourite_brand?: string;
  current_phone?: string;
  join_reason?: JoinReason;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

// ─── Analytics Types ──────────────────────────────────────────

export interface BestValuePhone {
  name: string;
  price: number;
  ram?: number;
  storage?: number;
  store: string;
  url?: string;
}

export interface BrandStat {
  brand: string;
  count: number;
  share_pct: number;
  avg_price: number;
  min_price: number;
  max_price: number;
  best_value_phone: BestValuePhone | null;
}

export interface BrandAnalyticsResponse {
  total_phones: number;
  brands: BrandStat[];
}

export interface SegmentStat { label: string; count: number; }
export interface OsStat      { os: string;    count: number; }
export interface NetworkStat { type: string;  count: number; }
export interface StoreStat   { store: string; count: number; avg_price: number; }

export interface MarketOverviewResponse {
  total_phones: number;
  five_g_pct: number;
  price_summary: { min: number; max: number; mean: number; median: number };
  price_segments: SegmentStat[];
  os_distribution: OsStat[];
  network_stats: NetworkStat[];
  store_stats: StoreStat[];
  spec_averages: Record<string, number>;
}
