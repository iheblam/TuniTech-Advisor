"""
Machine Learning Service – pure numpy/pandas KNN price predictor.

Avoids sklearn/scipy entirely so it works even on machines where
compiled extension DLLs are blocked by Application Control policies.

v2 improvements:
  - Brand mean-price encoding added as a feature (biggest price driver)
  - is_5g included as a binary feature
  - Two-stage prediction: brand-specific KNN first, global fallback
  - k increased to 15 for more stable estimates
  - Tighter confidence interval via weighted std on final neighbors
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List

from ..config import settings


class MLService:
    """Pure-numpy KNN price predictor trained on the unified dataset."""

    # Numerical CSV columns used to build the feature matrix
    # These are the RAW csv column names (before data_service rename)
    NUM_COLS = ['ram_gb', 'storage_gb', 'battery_mah',
                'screen_inches', 'camera_rear_mp', 'camera_front_mp']

    def __init__(self):
        self.model_loaded: bool = False
        self.model_info: Dict[str, Any] = {}

        # Full training arrays (all phones)
        self._train_X: Optional[np.ndarray] = None   # normalised, shape (n, 8)
        self._train_y: Optional[np.ndarray] = None   # prices
        self._train_brands: Optional[List[str]] = None  # lowercase brand per row

        # Per-brand training arrays for brand-scoped KNN
        self._brand_X: Dict[str, np.ndarray] = {}
        self._brand_y: Dict[str, np.ndarray] = {}

        # Normalisation params (8 features: 6 nums + brand_mean + is_5g)
        self._col_min: Optional[np.ndarray] = None
        self._col_rng: Optional[np.ndarray] = None

        # Brand → mean price lookup (normalised brand names)
        self._brand_mean: Dict[str, float] = {}
        self._global_mean: float = 0.0

        self._k = 15
        self._load_model()

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load_model(self):
        """Build the KNN index from the dataset CSV."""
        try:
            data_file = Path(settings.data_path) / settings.unified_data_file
            if not data_file.exists():
                print(f"Warning: dataset not found at {data_file}")
                return

            df = pd.read_csv(data_file)
            # Normalise brand casing
            if 'brand' in df.columns:
                df['brand'] = df['brand'].str.strip().str.lower().fillna('unknown')
            else:
                df['brand'] = 'unknown'

            # Derive is_5g from network column
            if 'network' in df.columns:
                df['is_5g'] = df['network'].str.upper().str.contains('5G', na=False).astype(float)
            else:
                df['is_5g'] = 0.0

            df = df.dropna(subset=['price'] + self.NUM_COLS).copy()
            if len(df) == 0:
                print("Warning: no rows with complete numerical specs + price.")
                return

            y = df['price'].values.astype(float)
            self._global_mean = float(y.mean())

            # Build brand mean-price lookup
            brand_means = df.groupby('brand')['price'].mean()
            self._brand_mean = brand_means.to_dict()

            # Encode brand as its mean price (very effective ordinal signal)
            df['brand_price'] = df['brand'].map(self._brand_mean).fillna(self._global_mean)

            # Feature matrix: 6 numeric specs + brand_price + is_5g  →  8 features
            feature_cols = self.NUM_COLS + ['brand_price', 'is_5g']
            X_raw = df[feature_cols].values.astype(float)

            # Min-max normalise per column
            col_min = X_raw.min(axis=0)
            col_max = X_raw.max(axis=0)
            rng = col_max - col_min
            rng[rng == 0] = 1.0
            X_norm = (X_raw - col_min) / rng

            self._train_X = X_norm
            self._train_y = y
            self._train_brands = df['brand'].tolist()
            self._col_min = col_min
            self._col_rng = rng

            # Per-brand index for two-stage lookup
            for brand in df['brand'].unique():
                mask = df['brand'] == brand
                self._brand_X[brand] = X_norm[mask]
                self._brand_y[brand] = y[mask]

            # MAE estimate via simple leave-10%-out approximation
            n = len(y)
            sample_idx = np.random.choice(n, size=min(200, n), replace=False)
            errors = []
            for i in sample_idx:
                dists = np.sqrt(((X_norm - X_norm[i]) ** 2).sum(axis=1))
                dists[i] = np.inf
                k = min(self._k, n - 1)
                nn_idx = np.argpartition(dists, k)[:k]
                w = 1.0 / (dists[nn_idx] + 1e-6)
                pred = float(np.sum(w * y[nn_idx]) / np.sum(w))
                errors.append(abs(pred - y[i]))
            approx_mae = float(np.mean(errors))

            self.model_loaded = True
            self.model_info = {
                "name":        f"KNN (k={self._k}, brand-aware, pure-numpy)",
                "algorithm":   "KNN",
                "k":           self._k,
                "features":    "ram, storage, battery, screen, cameras, brand, 5G",
                "dataset":     str(data_file.name),
                "samples":     int(len(df)),
                "brands":      int(len(self._brand_mean)),
                "approx_mae":  round(approx_mae, 1),
                "price_min":   float(y.min()),
                "price_max":   float(y.max()),
                "price_mean":  float(y.mean()),
            }
            print(f"[OK] KNN price model ready  ({len(df)} training phones, approx MAE ~= {approx_mae:.0f} TND)")

        except Exception as exc:
            print(f"Error building KNN model: {exc}")
            self.model_loaded = False

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_query(self, features: Dict[str, Any], brand: Optional[str]) -> np.ndarray:
        """Build a normalised 8-dim query vector."""
        col_api = ['ram', 'storage', 'battery', 'screen_size',
                   'main_camera', 'front_camera']
        q_raw = np.array([float(features.get(k, 0) or 0) for k in col_api], dtype=float)

        # Brand mean price (fallback to global mean if brand unknown)
        brand_key = brand.strip().lower() if brand else None
        brand_price = self._brand_mean.get(brand_key, self._global_mean) if brand_key else self._global_mean

        # is_5g
        is_5g_val = float(bool(features.get('is_5g', False)))

        q_full = np.append(q_raw, [brand_price, is_5g_val])
        return (q_full - self._col_min) / self._col_rng

    def _knn_predict(self, q_norm: np.ndarray,
                     X: np.ndarray, y: np.ndarray) -> Tuple[float, np.ndarray, np.ndarray]:
        """Return weighted prediction + neighbor prices + weights."""
        dists = np.sqrt(((X - q_norm) ** 2).sum(axis=1))
        k = min(self._k, len(dists))
        idx = np.argpartition(dists, k - 1)[:k]
        d_k = dists[idx]
        y_k = y[idx]
        eps = 1e-6
        w = 1.0 / (d_k + eps)
        predicted = float(np.sum(w * y_k) / np.sum(w))
        return predicted, y_k, w

    # ── Public interface ─────────────────────────────────────────────────────

    def is_model_loaded(self) -> bool:
        return self.model_loaded

    def predict_price(
        self,
        features: Dict[str, Any],
        brand: Optional[str] = None,
        return_confidence: bool = True,
    ) -> Tuple[float, Optional[Dict[str, float]]]:
        """
        Predict price with brand-aware weighted KNN.

        Two-stage strategy:
          1. If brand given and has ≥ 8 samples: predict within brand pool
          2. Global fallback with brand-encoded feature boosting brand signal
        Final prediction = weighted blend of both when applicable.
        """
        if not self.model_loaded:
            raise RuntimeError("KNN model is not loaded.")

        brand_key = brand.strip().lower() if brand else None
        q_norm = self._build_query(features, brand)

        # Stage 1: brand-scoped prediction
        brand_pred: Optional[float] = None
        brand_y_k: Optional[np.ndarray] = None
        brand_w: Optional[np.ndarray] = None
        if brand_key and brand_key in self._brand_X and len(self._brand_y[brand_key]) >= 5:
            brand_pred, brand_y_k, brand_w = self._knn_predict(
                q_norm, self._brand_X[brand_key], self._brand_y[brand_key]
            )

        # Stage 2: global prediction
        global_pred, global_y_k, global_w = self._knn_predict(
            q_norm, self._train_X, self._train_y
        )

        # Blend: 70% brand-specific + 30% global if brand available, else pure global
        if brand_pred is not None:
            predicted = 0.70 * brand_pred + 0.30 * global_pred
            # Merge neighbors for confidence estimate
            y_all = np.concatenate([brand_y_k, global_y_k])
            w_all = np.concatenate([brand_w * 0.70, global_w * 0.30])
        else:
            predicted = global_pred
            y_all = global_y_k
            w_all = global_w

        predicted = round(predicted, 2)

        confidence_interval: Optional[Dict[str, float]] = None
        if return_confidence:
            w_sum = w_all.sum()
            variance = float(np.sum(w_all * (y_all - predicted) ** 2) / w_sum)
            std = max(float(np.sqrt(variance)), predicted * 0.05)
            confidence_interval = {
                "lower": round(max(0.0, predicted - 1.64 * std), 2),  # 90% CI
                "upper": round(predicted + 1.64 * std, 2),
            }

        return predicted, confidence_interval

    def get_model_info(self) -> Dict[str, Any]:
        if not self.model_loaded:
            return {"loaded": False, "message": "No model is currently loaded"}
        return {"loaded": True, **self.model_info}

    def estimate_features_from_brand(
        self,
        brand: str,
        base_features: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Pass brand through; kept for API compatibility."""
        return base_features.copy()


# Singleton
ml_service = MLService()
