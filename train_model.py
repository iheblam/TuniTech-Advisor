"""
Quick training script - mirrors the notebook pipeline.
Trains KNN, Random Forest and XGBoost, then saves the best model
to models/best_model.pkl and logs everything to MLflow.
"""

import os
import sys
import time
import pickle
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# ─── Paths ───────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, "dataset", "unified_smartphones_filled.csv")
MODELS_DIR = os.path.join(ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# ─── sklearn ───────────────────────────────────────────────────
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("⚠️  XGBoost not installed – skipping XGBoost model")

import mlflow
import mlflow.sklearn

# ─── MLflow ───────────────────────────────────────────────────
MLFLOW_URI = f"file:///{ROOT.replace(os.sep, '/')}/mlruns"
EXPERIMENT  = "smartphone-price-prediction"          # matches api/config.py

mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment(EXPERIMENT)
print(f"✅ MLflow ready  → {MLFLOW_URI}  experiment={EXPERIMENT}")

# ─── Load data ────────────────────────────────────────────────
print("\n📦 Loading dataset…")
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=['price']).copy()
print(f"   {df.shape[0]} smartphones × {df.shape[1]} features")
print(f"   Price range: {df['price'].min():.0f} – {df['price'].max():.0f} TND")

# ─── Feature engineering ──────────────────────────────────────
numerical_cols = ['ram_gb', 'storage_gb', 'battery_mah', 'screen_inches',
                  'camera_rear_mp', 'camera_front_mp']
scaler_temp = MinMaxScaler()
df_norm = pd.DataFrame(
    scaler_temp.fit_transform(df[numerical_cols]),
    columns=numerical_cols,
    index=df.index
)

df['specs_sum_normalized'] = df_norm.mean(axis=1)
df['value_score']          = df['specs_sum_normalized'] / (df['price'] / 1000)
df['total_specs_score']    = (
    df_norm['ram_gb']          * 0.25 +
    df_norm['storage_gb']      * 0.25 +
    df_norm['battery_mah']     * 0.15 +
    df_norm['camera_rear_mp']  * 0.20 +
    df_norm['camera_front_mp'] * 0.10 +
    df_norm['screen_inches']   * 0.05
)
df['price_tier'] = pd.cut(
    df['price'],
    bins=[0, 700, 2000, float('inf')],
    labels=['Budget', 'Mid-Range', 'Premium']
)

# Save scaler so the API can reproduce the same normalisation at inference time
scaler_meta = {
    "scaler": scaler_temp,
    "numerical_cols": numerical_cols,
    "price_min": float(df['price'].min()),
    "price_max": float(df['price'].max()),
}
with open(os.path.join(MODELS_DIR, "feature_scaler.pkl"), "wb") as f:
    pickle.dump(scaler_meta, f)
print("✅ Feature scaler saved → models/feature_scaler.pkl")

# ─── Feature selection ────────────────────────────────────────
SEL_NUM = ['value_score', 'total_specs_score']
SEL_CAT = ['brand', 'network', 'os', 'processor_type', 'price_tier']

X = df[SEL_NUM + SEL_CAT].copy()
y = df['price'].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n📊 Train: {len(X_train)}  Test: {len(X_test)}")

# Save splits
with open(os.path.join(MODELS_DIR, "data_splits.pkl"), "wb") as f:
    pickle.dump({"X_train": X_train, "X_test": X_test,
                 "y_train": y_train, "y_test": y_test}, f)

# ─── Preprocessing pipeline ───────────────────────────────────
preprocessor = ColumnTransformer([
    ('num', Pipeline([
        ('imputer', KNNImputer(n_neighbors=5)),
        ('scaler', StandardScaler())
    ]), SEL_NUM),
    ('cat', Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(drop='first', sparse_output=False,
                                  handle_unknown='ignore'))
    ]), SEL_CAT)
])

# ─── Training helper ──────────────────────────────────────────
def train(model, name, params, run_name):
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tag("model_type", name)
        for k, v in params.items():
            mlflow.log_param(k, v)

        pipe = Pipeline([('preprocessor', preprocessor), ('regressor', model)])
        t0 = time.time()
        pipe.fit(X_train, y_train)
        elapsed = time.time() - t0

        y_pred = pipe.predict(X_test)
        mae  = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2   = r2_score(y_test, y_pred)

        mlflow.log_metric("mae",           mae)
        mlflow.log_metric("rmse",          rmse)
        mlflow.log_metric("r2_score",      r2)
        mlflow.log_metric("training_time", elapsed)
        mlflow.log_param("algorithm",      name)
        mlflow.sklearn.log_model(pipe, "model")

        print(f"   {run_name:20s}  MAE={mae:7.1f} TND  R²={r2:.4f}  t={elapsed:.2f}s")
        return pipe, {"mae": mae, "rmse": rmse, "r2": r2}

# ─── Train models ─────────────────────────────────────────────
print("\n🚀 Training models…")
results = {}

# KNN variants
for n in [3, 5, 7, 10]:
    m, metrics = train(
        KNeighborsRegressor(n_neighbors=n, weights='distance'),
        "KNN", {"n_neighbors": n, "weights": "distance"}, f"KNN_n{n}"
    )
    results[f"KNN_n{n}"] = (m, metrics)

# Random Forest
rf_m, rf_metrics = train(
    RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1),
    "Random Forest", {"n_estimators": 100, "max_depth": 20}, "Random_Forest"
)
results["Random_Forest"] = (rf_m, rf_metrics)

# XGBoost (if available)
if HAS_XGB:
    xgb_m, xgb_metrics = train(
        XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1,
                     random_state=42, n_jobs=-1, verbosity=0),
        "XGBoost", {"n_estimators": 100, "max_depth": 6, "learning_rate": 0.1},
        "XGBoost"
    )
    results["XGBoost"] = (xgb_m, xgb_metrics)

# ─── Pick best ────────────────────────────────────────────────
best_name = min(results, key=lambda k: results[k][1]["mae"])
best_pipeline, best_metrics = results[best_name]

print(f"\n🏆 Best model: {best_name}")
print(f"   MAE  = {best_metrics['mae']:.2f} TND")
print(f"   RMSE = {best_metrics['rmse']:.2f} TND")
print(f"   R²   = {best_metrics['r2']:.4f}")

# ─── Save best model ──────────────────────────────────────────
model_path = os.path.join(MODELS_DIR, "best_model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(best_pipeline, f)

info = {
    "model_name":       best_name,
    "mae":              best_metrics["mae"],
    "rmse":             best_metrics["rmse"],
    "r2":               best_metrics["r2"],
    "features":         SEL_NUM + SEL_CAT,
    "training_samples": len(X_train),
    "test_samples":     len(X_test),
}
with open(os.path.join(MODELS_DIR, "best_model_info.pkl"), "wb") as f:
    pickle.dump(info, f)

print(f"\n✅ Saved → models/best_model.pkl")
print(f"✅ Saved → models/best_model_info.pkl")
print("\n✨ Training complete!")
