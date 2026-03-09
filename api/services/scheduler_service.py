"""
Scraper Refresh Scheduler Service
──────────────────────────────────
Automatically re-scrapes all Tunisian stores on a configurable interval
(default 168 h = 1 week), merges the results into unified_smartphones.csv,
fills missing specs, and hot-reloads the in-memory data/ML services.

Architecture
────────────
• APScheduler BackgroundScheduler keeps one job ("scrape_refresh") alive
  inside the FastAPI process – no extra workers or message brokers needed.
• Status is persisted to logs/scheduler_status.json so it survives a
  browser refresh and is visible the next time the admin page loads.
• Mytek uses Selenium/Chrome; it is intentionally SKIPPED in the
  automated scheduler by default (too fragile in headless CI).
  Set SCHEDULER_INCLUDE_MYTEK=true in .env to opt-in.
"""

import importlib
import logging
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .database import get_db

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent.parent.parent   # project root
DATASET_DIR   = ROOT / "dataset"
SCRAPERS_DIR  = ROOT / "scrapers"
LOG_DIR       = ROOT / "logs"

LOG_DIR.mkdir(exist_ok=True)

# Add scrapers/ to sys.path so we can import them as modules
if str(SCRAPERS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRAPERS_DIR))

logger = logging.getLogger("scheduler")

# ── Unified column schema (must match data_service expectations) ───────────────
UNIFIED_COLS = [
    "name", "brand", "ram_gb", "storage_gb", "battery_mah",
    "screen_inches", "camera_rear_mp", "camera_front_mp",
    "network", "os", "processor_type", "price", "url", "source",
]

# ── Store definitions ─────────────────────────────────────────────────────────
#   (module_name, display_name, store csv filename)
STORES_REQUESTS = [
    ("scrape_tunisianet_smartphones",     "Tunisianet",     "tunisianet_smartphones.csv"),
    ("scrape_spacenet_smartphones",       "SpaceNet",       "spacenet_smartphones.csv"),
    ("scrape_bestbuytunisie_smartphones", "BestBuyTunisie", "bestbuytunisie_smartphones.csv"),
    ("scrape_bestphone_smartphones",      "BestPhone",      "bestphone_smartphones.csv"),
]
STORES_SELENIUM = [
    ("scrape_mytek_smartphones",          "Mytek",          "mytek_smartphones.csv"),
]

# Max seconds to wait for a single store scrape before giving up
STORE_TIMEOUT_SEC = 240  # 4 minutes per store

# Store csv → display name mapping (used during merge)
STORE_SOURCE_MAP = {
    "tunisianet_smartphones.csv":     "Tunisianet",
    "spacenet_smartphones.csv":       "Spacenet",
    "mytek_smartphones.csv":          "Mytek",
    "bestbuytunisie_smartphones.csv": "BestBuyTunisie",
    "bestphone_smartphones.csv":      "Bestphone",
}


# ═══════════════════════════════════════════════════════════════════════════════

class SchedulerService:
    """Singleton that owns the APScheduler job and the pipeline logic."""

    _instance: Optional["SchedulerService"] = None

    def __new__(cls) -> "SchedulerService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized   = True
        self._lock          = threading.Lock()
        self._running       = False
        self._status        = self._load_status()
        self._scheduler     = BackgroundScheduler(timezone="UTC", daemon=True)
        self._init_scheduler()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load_status(self) -> Dict[str, Any]:
        try:
            doc = get_db().scheduler_status.find_one({"_id": "status"})
            if doc:
                # Never restore a stale "running" state
                doc["running"]       = False
                doc["started_at"]    = None
                doc["current_store"] = None
                doc.pop("_id", None)
                return doc
        except Exception:
            pass
        return {
            "last_run":        None,
            "next_run":        None,
            "last_results":    {},
            "live_results":    {},
            "started_at":      None,
            "current_store":   None,
            "interval_hours":  168,
            "include_mytek":   False,
            "logs":            [],
        }

    def _save_status(self) -> None:
        try:
            get_db().scheduler_status.replace_one(
                {"_id": "status"},
                {"_id": "status", **self._status},
                upsert=True,
            )
        except Exception as exc:
            logger.warning("Could not save scheduler status to MongoDB: %s", exc)

    # ── Logging ───────────────────────────────────────────────────────────────

    def _log(self, msg: str, level: str = "INFO") -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts} UTC] [{level}] {msg}"
        if level == "ERROR":
            logger.error(msg)
        else:
            logger.info(msg)
        logs: List[str] = self._status.setdefault("logs", [])
        logs.insert(0, entry)
        self._status["logs"] = logs[:150]    # keep last 150 entries
        self._save_status()

    # ── Scheduler initialisation ──────────────────────────────────────────────

    def _init_scheduler(self) -> None:
        hours = self._status.get("interval_hours", 168)
        self._scheduler.add_job(
            self.run_pipeline,
            trigger=IntervalTrigger(hours=hours),
            id="scrape_refresh",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        self._scheduler.start()
        self._update_next_run()
        self._log(f"Scheduler initialised — interval={hours} h")

    def _update_next_run(self) -> None:
        job = self._scheduler.get_job("scrape_refresh")
        if job and job.next_run_time:
            self._status["next_run"] = job.next_run_time.isoformat()
            self._save_status()

    # ══════════════════════════════════════════════════════════════════════════
    # PIPELINE
    # ══════════════════════════════════════════════════════════════════════════

    def run_pipeline(self) -> Dict[str, Any]:
        """Full scrape → merge → fill → hot-reload pipeline (thread-safe)."""
        with self._lock:
            if self._running:
                return {"error": "Pipeline already running"}
            self._running = True

        results: Dict[str, Any] = {}
        start = datetime.now(timezone.utc)
        self._status["started_at"]  = start.isoformat()
        self._status["live_results"] = {}
        self._status["current_store"] = None
        self._save_status()
        self._log("=" * 50)
        self._log("Scrape refresh pipeline STARTED")

        try:
            # ── 1. Scrape stores (each with a hard timeout) ───────────────
            stores_to_run = list(STORES_REQUESTS)
            if self._status.get("include_mytek"):
                stores_to_run += STORES_SELENIUM

            for module_name, store_name, csv_file in stores_to_run:
                self._status["current_store"] = store_name
                self._save_status()
                res = self._run_store_with_timeout(
                    module_name, store_name, DATASET_DIR / csv_file
                )
                results[store_name] = res
                # Save partial result immediately so UI can show it
                self._status["live_results"][store_name] = res
                self._save_status()

            self._status["current_store"] = "merging"
            self._save_status()

            # ── 2. Merge all store CSVs (preserve old data for failed stores) ──
            self._log("Merging store CSVs into unified dataset...")
            unified = self._merge_stores(results)
            if unified is None or unified.empty:
                raise RuntimeError("Merge step produced an empty DataFrame")
            (DATASET_DIR / "unified_smartphones.csv").parent.mkdir(exist_ok=True)
            # Always snapshot the current files before overwriting (safety net)
            for _fname in ("unified_smartphones.csv", "unified_smartphones_filled.csv"):
                _src = DATASET_DIR / _fname
                if _src.exists():
                    import shutil as _sh
                    _sh.copy(_src, DATASET_DIR / (_fname.replace(".csv", "_backup.csv")))
            unified.to_csv(DATASET_DIR / "unified_smartphones.csv", index=False)
            self._log(f"Merged {len(unified)} phones → unified_smartphones.csv")

            # ── Price history snapshot ─────────────────────────────────────
            try:
                from api.services.community_service import snapshot_prices
                records = unified[["name", "price", "source"]].rename(
                    columns={"source": "source"}
                ).to_dict("records")
                snapped = snapshot_prices(records)
                self._log(f"Price history: {snapped} snapshots recorded")
            except Exception as exc:
                self._log(f"Price history snapshot FAILED: {exc}", level="WARN")

            self._status["current_store"] = "filling"
            self._save_status()

            # ── 3. Fill missing specs ──────────────────────────────────────
            self._log("Filling missing specs...")
            filled = self._fill_specs(unified.copy())
            filled.to_csv(DATASET_DIR / "unified_smartphones_filled.csv", index=False)
            self._log(f"Specs filled → {len(filled)} phones saved")

            self._status["current_store"] = "reloading"
            self._save_status()

            # ── 4. Hot-reload in-memory services ──────────────────────────
            self._reload_services()

        except Exception as exc:
            self._log(f"Pipeline ERROR: {exc}", level="ERROR")
            results["__pipeline_error__"] = str(exc)
        finally:
            self._running = False
            elapsed = (datetime.now(timezone.utc) - start).total_seconds()
            self._status["last_run"]      = start.isoformat()
            self._status["last_results"]  = results
            self._status["live_results"]  = {}
            self._status["current_store"] = None
            self._status["started_at"]    = None
            self._update_next_run()
            self._log(f"Pipeline FINISHED in {elapsed:.0f} s")
            self._log("=" * 50)

        return results

    # ── Store scraper ─────────────────────────────────────────────────────────

    def _run_store(
        self, module_name: str, store_name: str, output_path: Path
    ) -> Dict[str, Any]:
        """Blocking scrape call — must be run inside a thread with timeout."""
        mod = importlib.import_module(module_name)
        products = mod.scrape_all_pages()
        if not products:
            raise ValueError("Scraper returned 0 products")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mod.save_csv(products, str(output_path))
        return products

    def _run_store_with_timeout(
        self, module_name: str, store_name: str, output_path: Path
    ) -> Dict[str, Any]:
        """Run _run_store in a thread; kill it after STORE_TIMEOUT_SEC."""
        self._log(f"  → Scraping {store_name} (timeout={STORE_TIMEOUT_SEC}s)...")
        store_start = datetime.now(timezone.utc)
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(self._run_store, module_name, store_name, output_path)
                products = future.result(timeout=STORE_TIMEOUT_SEC)
            elapsed = (datetime.now(timezone.utc) - store_start).total_seconds()
            self._log(f"    {store_name}: {len(products)} products ✓ ({elapsed:.0f}s)")
            return {"status": "ok", "count": len(products), "duration_sec": round(elapsed)}
        except FuturesTimeoutError:
            elapsed = (datetime.now(timezone.utc) - store_start).total_seconds()
            msg = f"Timed out after {elapsed:.0f}s"
            self._log(f"    {store_name} TIMEOUT: {msg}", level="ERROR")
            return {"status": "timeout", "count": 0, "error": msg, "duration_sec": round(elapsed)}
        except Exception as exc:
            elapsed = (datetime.now(timezone.utc) - store_start).total_seconds()
            self._log(f"    {store_name} FAILED: {exc}", level="ERROR")
            return {"status": "error", "count": 0, "error": str(exc), "duration_sec": round(elapsed)}

    # ── Merge ─────────────────────────────────────────────────────────────────

    def _normalise_store_df(self, df: pd.DataFrame, source_name: str) -> pd.DataFrame:
        """Rename columns, coerce types, drop empties, ensure all unified cols."""
        df = df.rename(columns={"model": "name", "price_dt": "price"})
        df["source"] = source_name
        num_cols = ["ram_gb", "storage_gb", "battery_mah",
                    "screen_inches", "camera_rear_mp", "camera_front_mp", "price"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["name", "price"])
        df = df[df["name"].str.strip() != ""]
        for col in UNIFIED_COLS:
            if col not in df.columns:
                df[col] = None
        return df[UNIFIED_COLS]

    def _merge_stores(self, scrape_results: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Additive merge strategy — never loses data:
        1. Load existing unified_smartphones.csv as the baseline.
        2. For every store that was scraped successfully this run,
           replace that store's old rows with the fresh ones.
        3. For stores that failed / timed out, keep old rows.
        Result is always >= the previous row count (minus duplicates).
        """
        # ── Load existing baseline ────────────────────────────────────────────
        existing_path = DATASET_DIR / "unified_smartphones.csv"
        baseline: Optional[pd.DataFrame] = None
        if existing_path.exists():
            try:
                baseline = pd.read_csv(existing_path)
                self._log(f"    Baseline loaded: {len(baseline)} existing phones")
            except Exception as exc:
                self._log(f"    Could not load baseline: {exc}", level="ERROR")

        # ── Collect freshly scraped frames ────────────────────────────────────
        fresh_sources: set = set()   # track which sources we have fresh data for
        fresh_frames: List[pd.DataFrame] = []

        for csv_name, source_name in STORE_SOURCE_MAP.items():
            store_result = scrape_results.get(source_name, {})
            if store_result.get("status") != "ok":
                self._log(f"    Skipping fresh load for {source_name} (scrape failed/timed out — keeping old rows)")
                continue
            path = DATASET_DIR / csv_name
            if not path.exists():
                self._log(f"    {source_name}: CSV not found after scrape — keeping old rows")
                continue
            try:
                df = pd.read_csv(path, dtype=str)
                df = self._normalise_store_df(df, source_name)
                if df.empty:
                    self._log(f"    {source_name}: normalised to 0 rows — keeping old rows")
                    continue
                fresh_frames.append(df)
                fresh_sources.add(source_name)
                self._log(f"    {source_name}: {len(df)} fresh rows ✓")
            except Exception as exc:
                self._log(f"    Could not read {csv_name}: {exc} — keeping old rows", level="ERROR")

        # ── Build final dataset ───────────────────────────────────────────────
        frames: List[pd.DataFrame] = []

        # Keep old rows for sources we did NOT successfully re-scrape
        if baseline is not None and not baseline.empty:
            old_kept = baseline[~baseline["source"].isin(fresh_sources)].copy()
            if not old_kept.empty:
                self._log(f"    Kept {len(old_kept)} old rows for un-scraped sources")
                # Ensure schema matches
                for col in UNIFIED_COLS:
                    if col not in old_kept.columns:
                        old_kept[col] = None
                frames.append(old_kept[UNIFIED_COLS])

        # Add all fresh rows
        frames.extend(fresh_frames)

        if not frames:
            # Nothing at all — fall back to pure baseline if available
            if baseline is not None and not baseline.empty:
                self._log("    WARNING: all scrapes failed — returning full baseline unchanged")
                return baseline
            return None

        merged = pd.concat(frames, ignore_index=True)

        # Deduplicate: keep the row with the lowest price for same (name, source)
        # (in case a product appears twice from the same CSV)
        merged = (
            merged
            .sort_values("price", ascending=True)
            .drop_duplicates(subset=["name", "source"], keep="first")
            .reset_index(drop=True)
        )

        prev = len(baseline) if baseline is not None else 0
        self._log(f"    Final dataset: {len(merged)} phones (was {prev} → {'↑' if len(merged) >= prev else '↓'}{abs(len(merged)-prev)})")
        return merged

    # ── Spec filling ──────────────────────────────────────────────────────────

    def _fill_specs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reuse fill_missing_smart logic without calling its main()."""
        try:
            filler = importlib.import_module("fill_missing_smart")

            # Strategy 1 – known phone specs DB
            for idx, row in df.iterrows():
                specs = filler.find_matching_specs(row.get("name", ""))
                if specs:
                    for col, val in specs.items():
                        if col in df.columns:
                            current = row.get(col)
                            if pd.isna(current) or str(current).strip() == "":
                                df.at[idx, col] = val

            # Strategy 2 – brand averages
            df = filler.fill_from_brand_stats(df)

            # Strategy 3 – global median / mode
            for col in ["battery_mah", "screen_inches", "camera_rear_mp",
                        "camera_front_mp", "ram_gb", "storage_gb"]:
                if col in df.columns:
                    median = df[col].median()
                    if not pd.isna(median):
                        df[col] = df[col].fillna(median)

            for col in ["network", "os"]:
                if col in df.columns and df[col].notna().any():
                    mode = df[col].mode()
                    if len(mode):
                        df[col] = df[col].fillna(mode[0]).replace("", mode[0])

        except Exception as exc:
            self._log(f"Fill specs FAILED (raw data used): {exc}", level="ERROR")

        return df

    # ── Hot-reload ────────────────────────────────────────────────────────────

    def _reload_services(self) -> None:
        self._log("  Hot-reloading in-memory services...")
        try:
            from api.services.data_service import data_service
            data_service._load_data()
            self._log(f"    data_service: {len(data_service.data)} rows loaded ✓")
        except Exception as exc:
            self._log(f"    data_service reload ERROR: {exc}", level="ERROR")

        try:
            from api.services.ml_service import ml_service
            ml_service._load_model()
            self._log(f"    ml_service reloaded ✓")
        except Exception as exc:
            self._log(f"    ml_service reload ERROR: {exc}", level="ERROR")

    # ── Public API ────────────────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        status = {**self._status, "running": self._running}
        # Add elapsed seconds so frontend can show a live timer
        if self._running and self._status.get("started_at"):
            try:
                started = datetime.fromisoformat(self._status["started_at"])
                status["elapsed_sec"] = round(
                    (datetime.now(timezone.utc) - started).total_seconds()
                )
            except Exception:
                status["elapsed_sec"] = None
        else:
            status["elapsed_sec"] = None
        return status

    def trigger_now(self) -> Dict[str, str]:
        """Start pipeline in background thread; returns immediately."""
        if self._running:
            return {"status": "already_running"}
        thread = threading.Thread(target=self.run_pipeline, daemon=True, name="scrape-pipeline")
        thread.start()
        return {"status": "started"}

    def set_interval(self, hours: int) -> None:
        self._status["interval_hours"] = hours
        self._scheduler.reschedule_job(
            "scrape_refresh",
            trigger=IntervalTrigger(hours=hours),
        )
        self._update_next_run()
        self._save_status()
        self._log(f"Interval updated → {hours} h")

    def set_include_mytek(self, value: bool) -> None:
        self._status["include_mytek"] = value
        self._save_status()
        self._log(f"include_mytek → {value}")

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)


# Singleton instance used throughout the app
scheduler_service = SchedulerService()
