#!/usr/bin/env python3
"""
Fill missing specs in BestBuyTunisie scraped data and apply feature engineering.

Steps:
  1. Load raw dataset/bestbuytunisie_smartphones.csv
  2. Cross-reference with existing filled datasets (tunisianet, mytek, spacenet, bestphone)
     to fill blanks using fuzzy model-name matching.
  3. Infer any remaining specs from the product title / description.
  4. Apply feature engineering (normalization, price bins, flags, etc.).
  5. Write dataset/bestbuytunisie_smartphones_filled.csv

Run from repo root:
    python scrapers/fill_bestbuytunisie_specs.py
"""

import re
import sys
from pathlib import Path
from difflib import SequenceMatcher

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"

RAW_CSV     = DATASET_DIR / "bestbuytunisie_smartphones.csv"
OUTPUT_CSV  = DATASET_DIR / "bestbuytunisie_smartphones_filled.csv"

REFERENCE_DATASETS = [
    ("Tunisianet",  "tunisianet_smartphones_filled.csv"),
    ("Mytek",       "mytek_smartphones_filled.csv"),
    ("SpaceNet",    "spacenet_smartphones_filled.csv"),
    ("BestPhone",   "bestphone_smartphones_filled.csv"),
    ("Unified",     "unified_smartphones_filled.csv"),
]

SPEC_COLS = [
    "battery_mah", "screen_inches", "camera_rear_mp", "camera_front_mp",
    "network", "os", "processor_type",
]


# ---------------------------------------------------------------------------
# Model-name normalisation helpers
# ---------------------------------------------------------------------------

def _normalize_model(name) -> str:
    """Reduce a model string to a compact lowercase key for matching."""
    if pd.isna(name):
        return ""
    s = str(name).lower().strip()

    # Drop common prefixes
    s = re.sub(r"^smartphone\s+", "", s)
    s = re.sub(r"^t[eé]l[eé]phone\s+portable\s+", "", s)

    # Drop RAM/storage specs  "4 go / 128 go", "4go/128go", "3go 64go" …
    s = re.sub(r"\d+\s*go\s*/?\s*\d*\s*(?:go)?", "", s, flags=re.I)

    # Drop numeric variants like "4g" (keep model numbers)
    s = re.sub(r"\b[45]g\b", "", s, flags=re.I)

    # Drop colors
    COLORS = (
        "noir|blanc|bleu|vert|rose|gold|silver|gris|violet|rouge|orange|cyan|"
        "black|white|green|blue|pink|grey|gray|purple|lavender|lime|natural|"
        "navy|teal|titanium|midnight|starlight|graphite|deep|ice|dark|menthe|"
        "neon|sleek|twilight|purple|satin|crystal|stellar|silver|cyan|bronze|"
        "red|yellow|coral|indigo"
    )
    s = re.sub(rf"\b({COLORS})\b", "", s)

    # Drop trailing dashes / special chars
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _extract_model_key(name) -> str:
    """Extract the core identifiable model key (brand + model number)."""
    n = _normalize_model(name)

    patterns = [
        (r"(iphone\s*\d+(?:\s*(?:pro\s*max|pro|plus|mini))?)", ""),
        (r"(galaxy\s+[zsa]\d+(?:\s*(?:ultra|fe|plus|\+))*)", "samsung"),
        (r"(redmi\s+note?\s*\d+(?:\s*(?:pro|plus))*)", "xiaomi"),
        (r"(redmi\s+a?\d+(?:\s*(?:pro|plus))*)", "xiaomi"),
        (r"(poco\s+[xmfc]\d+(?:\s*(?:pro|plus))*)", "xiaomi"),
        (r"(honor\s+\w+\d+\w*(?:\s*(?:plus|\+))*)", ""),
        (r"(infinix\s+\w+\s*\d+\w*)", ""),
        (r"(tecno\s+\w+\s*\d+\w*)", ""),
        (r"(realme\s+\d+\w*(?:\s*(?:pro|plus))*)", ""),
        (r"(vivo\s+[yvtx]\d+\w*(?:\s*(?:pro|plus))*)", ""),
        (r"(oppo\s+[a-z]+\d+\w*(?:\s*(?:pro|plus))*)", ""),
    ]
    for pat, brand_prefix in patterns:
        m = re.search(pat, n, re.I)
        if m:
            key = m.group(1).strip()
            return f"{brand_prefix} {key}".strip() if brand_prefix else key

    # Generic: first 6 words
    return " ".join(n.split()[:6])


# ---------------------------------------------------------------------------
# Spec database from reference datasets
# ---------------------------------------------------------------------------

def build_spec_db(dataframes) -> dict:
    """Build {model_key: {spec_col: value}} from a list of (name, DataFrame)."""
    db: dict = {}
    for src_name, df in dataframes:
        name_col = next((c for c in ("model", "name") if c in df.columns), None)
        if name_col is None:
            continue
        for _, row in df.iterrows():
            key = _extract_model_key(row.get(name_col, ""))
            if not key or len(key) < 4:
                continue
            specs = {
                c: str(row[c]).strip()
                for c in SPEC_COLS
                if c in df.columns and pd.notna(row[c]) and str(row[c]).strip()
            }
            if not specs:
                continue
            # Keep the richer entry
            if key not in db or len(specs) > len(db[key]):
                db[key] = specs
    return db


def lookup_specs(name: str, db: dict) -> dict:
    """Return spec dict for the best-matching model in db, or {}."""
    key = _extract_model_key(name)
    if not key:
        return {}

    # Exact
    if key in db:
        return db[key]

    # Fuzzy
    best_score, best_val = 0.0, {}
    for db_key, specs in db.items():
        score = SequenceMatcher(None, key, db_key).ratio()
        # Boost by word overlap
        kw = set(key.split())
        dw = set(db_key.split())
        if kw and dw:
            overlap = len(kw & dw) / max(len(kw), len(dw))
            score = max(score, overlap)
        if score > 0.78 and score > best_score:
            best_score, best_val = score, specs
    return best_val


# ---------------------------------------------------------------------------
# Infer specs from text / title when DB has no match
# ---------------------------------------------------------------------------

def _infer_from_title(row: pd.Series, df: pd.DataFrame) -> dict:
    """Pull specs that can be derived directly from the product title/description."""
    inferred = {}
    text_cols = [c for c in ("model", "description") if c in df.columns]
    combined = " ".join(str(row.get(c, "")) for c in text_cols)

    # Network
    if not _has(row, "network"):
        if re.search(r"\b5G\b", combined):
            inferred["network"] = "5G"
        elif re.search(r"\b4G\b", combined):
            inferred["network"] = "4G"

    # OS
    if not _has(row, "os"):
        m = re.search(r"Android\s*(\d+)", combined, re.I)
        if m:
            inferred["os"] = f"Android {m.group(1)}"
        elif re.search(r"\biOS\b", combined):
            inferred["os"] = "iOS"

    # Processor
    if not _has(row, "processor_type"):
        if re.search(r"Octa[- ]?[Cc]ore", combined, re.I):
            inferred["processor_type"] = "Octa Core"
        elif re.search(r"Quad[- ]?[Cc]ore", combined, re.I):
            inferred["processor_type"] = "Quad Core"
        if re.search(r"Snapdragon", combined, re.I):
            inferred["processor_type"] = "Snapdragon"
        elif re.search(r"MediaTek|Helio|Dimensity", combined, re.I):
            inferred["processor_type"] = "MediaTek"
        elif re.search(r"Unisoc", combined, re.I):
            inferred["processor_type"] = "Unisoc"
        elif re.search(r"Exynos", combined, re.I):
            inferred["processor_type"] = "Exynos"

    # Battery
    if not _has(row, "battery_mah"):
        m = re.search(r"(\d{4,5})\s*mAh", combined, re.I)
        if m:
            inferred["battery_mah"] = m.group(1)

    # Screen
    if not _has(row, "screen_inches"):
        for pat in [
            r"[EÉ]cran\s*:?\s*([\d,\.]+)\s*[\"″]",
            r"([\d,\.]+)\s*[\"″]\s*(?:HD|IPS|LCD|AMOLED|OLED|PLS)",
            r"([\d,\.]+)\s*pouces",
        ]:
            m = re.search(pat, combined, re.I)
            if m:
                v = m.group(1).replace(",", ".")
                try:
                    if 3.0 <= float(v) <= 8.0:
                        inferred["screen_inches"] = v
                        break
                except ValueError:
                    pass

    # Camera rear
    if not _has(row, "camera_rear_mp"):
        for pat in [
            r"[Aa]ppareil\s*[Pp]hoto\s*[Aa]rri[eè]re\s*:?\s*([\d\.]+)\s*MP",
            r"[Aa]rri[eè]re\s*:?\s*([\d\.]+)\s*MP",
            r"([\d\.]+)\s*MP\s*\+",
        ]:
            m = re.search(pat, combined, re.I)
            if m:
                inferred["camera_rear_mp"] = m.group(1).rstrip(".")
                break

    # Camera front
    if not _has(row, "camera_front_mp"):
        for pat in [
            r"[Ff]rontale?\s*:?\s*([\d\.]+)\s*MP",
            r"[Aa]vant\s*:?\s*([\d\.]+)\s*MP",
        ]:
            m = re.search(pat, combined, re.I)
            if m:
                inferred["camera_front_mp"] = m.group(1).rstrip(".")
                break

    return inferred


def _has(row: pd.Series, col: str) -> bool:
    v = row.get(col, "")
    return bool(v and str(v).strip() and str(v).strip().lower() not in ("nan", "none", ""))


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def apply_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns and normalise values."""

    # -- Coerce numeric columns --
    for col in ("ram_gb", "storage_gb", "battery_mah", "screen_inches",
                "camera_rear_mp", "camera_front_mp"):
        if col not in df.columns:
            df[col] = ""
        df[col] = (
            df[col].astype(str)
            .str.replace(",", ".", regex=False)
            .str.extract(r"([\d\.]+)")[0]
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # -- Price as numeric --
    if "price_dt" in df.columns:
        df["price_num"] = pd.to_numeric(
            df["price_dt"].astype(str).str.replace(",", ".", regex=False)
            .str.extract(r"([\d\.]+)")[0],
            errors="coerce",
        )

    # -- Price tier --
    def _price_tier(p):
        if pd.isna(p):
            return "Unknown"
        if p < 400:
            return "Entrée de gamme"
        if p < 800:
            return "Milieu de gamme"
        if p < 1500:
            return "Haut de gamme"
        return "Premium"

    if "price_num" in df.columns:
        df["price_tier"] = df["price_num"].apply(_price_tier)

    # -- OS family --
    def _os_family(os):
        if pd.isna(os) or not str(os).strip():
            return ""
        s = str(os).lower()
        if "android" in s:
            return "Android"
        if "ios" in s or "iphone" in s:
            return "iOS"
        return str(os)

    if "os" in df.columns:
        df["os_family"] = df["os"].apply(_os_family)

    # -- 5G flag --
    if "network" in df.columns:
        df["is_5g"] = df["network"].astype(str).str.contains("5G", case=False, na=False)

    # -- RAM tier --
    def _ram_tier(r):
        if pd.isna(r):
            return ""
        r = float(r)
        if r <= 3:
            return "Low"
        if r <= 6:
            return "Mid"
        return "High"

    if "ram_gb" in df.columns:
        df["ram_tier"] = df["ram_gb"].apply(_ram_tier)

    # -- Storage tier --
    def _storage_tier(s):
        if pd.isna(s):
            return ""
        s = float(s)
        if s <= 64:
            return "Low"
        if s <= 128:
            return "Mid"
        return "High"

    if "storage_gb" in df.columns:
        df["storage_tier"] = df["storage_gb"].apply(_storage_tier)

    # -- Battery tier --
    def _bat_tier(b):
        if pd.isna(b):
            return ""
        b = float(b)
        if b < 3500:
            return "Small"
        if b < 5000:
            return "Standard"
        return "Large"

    if "battery_mah" in df.columns:
        df["battery_tier"] = df["battery_mah"].apply(_bat_tier)

    # -- Normalize brand (title-case) --
    if "brand" in df.columns:
        df["brand"] = df["brand"].astype(str).str.strip().str.title()
        df.loc[df["brand"].str.lower() == "nan", "brand"] = ""

    # -- Normalize color (title-case) --
    if "color" in df.columns:
        df["color"] = df["color"].astype(str).str.strip().str.title()
        df.loc[df["color"].str.lower() == "nan", "color"] = ""

    # -- Normalize OS string --
    if "os" in df.columns:
        df["os"] = df["os"].astype(str).str.strip()
        df.loc[df["os"].str.lower().isin(["nan", "none", ""]), "os"] = ""

    # -- Source column --
    df["source"] = "BestBuyTunisie"

    # -- Drop helper column --
    df.drop(columns=["price_num"], errors="ignore", inplace=True)

    return df


# ---------------------------------------------------------------------------
# Coverage report
# ---------------------------------------------------------------------------

def print_coverage(df: pd.DataFrame) -> None:
    cols = SPEC_COLS + ["brand", "color", "warranty", "in_stock"]
    print("\nColumn coverage:")
    for col in cols:
        if col not in df.columns:
            continue
        non_empty = df[col].astype(str).str.strip().replace("nan", "").replace("", pd.NA).notna().sum()
        pct = non_empty / len(df) * 100 if len(df) else 0
        bar = "█" * int(pct / 5)
        print(f"  {col:<22}: {non_empty:>4}/{len(df)}  ({pct:5.1f}%)  {bar}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("BestBuyTunisie – spec filler & feature engineering")
    print("=" * 60)

    # 1. Load raw data
    if not RAW_CSV.exists():
        print(f"\nERROR: Raw CSV not found at {RAW_CSV}")
        print("       Run scrapers/scrape_bestbuytunisie_smartphones.py first.")
        sys.exit(1)

    df = pd.read_csv(RAW_CSV, dtype=str)
    df = df.fillna("")
    print(f"\nLoaded {len(df)} raw products from {RAW_CSV.name}")

    # 2. Load reference datasets
    print("\nLoading reference datasets for cross-filling…")
    ref_dfs = []
    for label, fname in REFERENCE_DATASETS:
        path = DATASET_DIR / fname
        if path.exists():
            try:
                ref_df = pd.read_csv(path, dtype=str).fillna("")
                ref_dfs.append((label, ref_df))
                print(f"  {label:<14}: {len(ref_df)} rows  ✓")
            except Exception as e:
                print(f"  {label:<14}: SKIP ({e})")
        else:
            print(f"  {label:<14}: not found – skip")

    # 3. Build spec database
    spec_db = build_spec_db(ref_dfs)
    print(f"\nSpec database: {len(spec_db)} unique model keys")

    # 4. Cross-fill missing specs
    filled_from_db = 0
    filled_from_text = 0

    for idx, row in df.iterrows():
        model_name = str(row.get("model", "") or "")

        # a) try DB lookup
        db_specs = lookup_specs(model_name, spec_db)
        for col in SPEC_COLS:
            if not _has(row, col) and db_specs.get(col):
                df.at[idx, col] = db_specs[col]
                filled_from_db += 1

        # b) infer from title / description
        text_specs = _infer_from_title(df.loc[idx], df)
        for col, val in text_specs.items():
            if not _has(df.loc[idx], col) and val:
                df.at[idx, col] = val
                filled_from_text += 1

    print(f"\nFilled {filled_from_db} values from reference datasets")
    print(f"Filled {filled_from_text} values inferred from title/description")

    # 5. Feature engineering
    print("\nApplying feature engineering…")
    df = apply_feature_engineering(df)

    # 6. Coverage report
    print_coverage(df)

    # 7. Save
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(df)} products to {OUTPUT_CSV}")
    print("Done.")


if __name__ == "__main__":
    main()
