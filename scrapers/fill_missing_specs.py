"""
Fill missing smartphone specs by fetching from GSMArena.
Reads tunisianet_smartphones.csv, looks up each model (by brand + normalized name)
on GSMArena, parses specs, and fills only empty fields. Saves back to CSV.
"""

import os
import re
import csv
import time
import requests
from urllib.parse import urljoin, quote_plus
from typing import Dict, List, Optional, Set, Any

from bs4 import BeautifulSoup

GSM_BASE = "https://www.gsmarena.com"
GSM_SEARCH = f"{GSM_BASE}/res.php3"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

SPEC_COLUMNS = [
    "ram_gb", "storage_gb", "battery_mah", "screen_inches",
    "camera_rear_mp", "camera_front_mp", "network", "os",
]


def normalize_model_for_search(model: str, brand: str) -> str:
    """Reduce model string to a short search query (brand + model name without color/variant)."""
    if not model:
        return brand or ""
    # Remove common prefixes
    s = re.sub(r"^(Smartphone|Téléphone Portable|SMARTPHONE)\s+", "", model, flags=re.I)
    # Remove trailing color/variant: " | Vert", " - Noir", " / Bleu", " 4G / 3 Go / 64 Go / Bleu"
    s = re.sub(r"\s*[\|\/\-]\s*[A-Za-zéèêëàâùûîïô\s]+\s*$", "", s)
    s = re.sub(r"\s*/\s*\d+\s*Go\s*/\s*\d+\s*Go\s*(/\s*[A-Za-z]+)?\s*$", "", s, flags=re.I)
    s = re.sub(r"\s*\d+\s*\+\s*\d+Go\s*/\s*\d+\s*Go\s*.*$", "", s, flags=re.I)
    s = re.sub(r"\s*A631W\s*.*$", "", s, flags=re.I)  # variant codes
    s = s.strip()
    # Limit length; prefer brand + first part of model
    if brand and not s.lower().startswith(brand.lower()[:4]):
        query = f"{brand} {s}"
    else:
        query = s
    # Take first ~6 words for search
    words = query.split()[:7]
    return " ".join(words).strip() or brand or ""


def canonical_key(row: Dict[str, Any]) -> str:
    """Unique key for deduplication: same phone model = same key."""
    brand = (row.get("brand") or "").strip()
    model = (row.get("model") or "").strip()
    q = normalize_model_for_search(model, brand)
    return (q or model).lower()


def get_page(url: str) -> Optional[BeautifulSoup]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  Fetch error: {e}")
        return None


def find_first_phone_url(soup: BeautifulSoup) -> Optional[str]:
    """From GSMArena search results page, return first phone spec page URL."""
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if re.match(r"^[a-z0-9_\-]+-\d+\.php$", href) and "reviews" not in href and "pictures" not in href:
            return urljoin(GSM_BASE, href)
    return None


def parse_spec_table(soup: BeautifulSoup) -> Dict[str, str]:
    """Parse GSMArena spec page tables into a flat dict of our column names."""
    out = {}
    in_main_camera = False
    # GSMArena: td.ttl (label) and td.nfo (value)
    for table in soup.select("table"):
        rows = table.select("tr")
        for tr in rows:
            ttl_td = tr.select_one("td.ttl") or (tr.select("td")[0] if tr.select("td") else None)
            nfo_td = tr.select_one("td.nfo") or (tr.select("td")[1] if len(tr.select("td")) > 1 else None)
            if not ttl_td or not nfo_td:
                continue
            ttl = (ttl_td.get_text(strip=True) or "").lower()
            nfo = (nfo_td.get_text(strip=True) or "").lower()
            if not nfo:
                continue
            if "main camera" in ttl:
                in_main_camera = True
            elif "selfie" in ttl or "battery" in ttl or "memory" in ttl:
                in_main_camera = False
            # Internal -> RAM + Storage
            if "internal" in ttl:
                ram = re.search(r"(\d+)\s*GB\s*RAM", nfo, re.I)
                if ram:
                    out["ram_gb"] = ram.group(1)
                storage_m = re.search(r"(\d+)\s*GB", nfo, re.I)
                if storage_m:
                    out["storage_gb"] = storage_m.group(1)
            # Size (display)
            if "size" in ttl and "inch" in nfo:
                m = re.search(r"([\d.]+)\s*inches?", nfo, re.I)
                if m:
                    out["screen_inches"] = m.group(1)
            # Battery Type
            if "type" in ttl and "mah" in nfo:
                m = re.search(r"(\d+)\s*mah", nfo, re.I)
                if m:
                    out["battery_mah"] = m.group(1)
            # Main Camera: first MP value after "Main Camera" section
            if in_main_camera and re.search(r"\d+\s*MP", nfo, re.I) and "camera_rear_mp" not in out:
                m = re.search(r"(\d+)\s*MP", nfo, re.I)
                if m:
                    out["camera_rear_mp"] = m.group(1)
            if "selfie" in ttl:
                in_main_camera = False
                m = re.search(r"(\d+)\s*MP", nfo, re.I)
                if m:
                    out["camera_front_mp"] = m.group(1)
            # Technology (network)
            if "technology" in ttl:
                if "5g" in nfo:
                    out["network"] = "5G"
                elif "4g" in nfo or "lte" in nfo:
                    out["network"] = "4G"
                elif "3g" in nfo or "hspa" in nfo:
                    out["network"] = "3G"
            # OS
            if "os" in ttl:
                if "android" in nfo:
                    ver = re.search(r"android\s*(\d+)", nfo, re.I)
                    out["os"] = f"Android {ver.group(1)}" if ver else "Android"
                elif "ios" in nfo:
                    out["os"] = "iOS"
    return out


def fetch_specs_for_query(query: str) -> Dict[str, str]:
    """Search GSMArena for query and return parsed specs from first result."""
    if not query or len(query) < 3:
        return {}
    url = f"{GSM_SEARCH}?sSearch={quote_plus(query)}"
    soup = get_page(url)
    if not soup:
        return {}
    spec_url = find_first_phone_url(soup)
    if not spec_url:
        return {}
    time.sleep(1.2)
    spec_soup = get_page(spec_url)
    if not spec_soup:
        return {}
    return parse_spec_table(spec_soup)


def load_csv(path: str) -> tuple:
    """Returns (rows, fieldnames)."""
    rows = []
    fieldnames = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for row in reader:
            rows.append(dict(row))
    return rows, fieldnames


def save_csv(rows: List[Dict[str, Any]], path: str, fieldnames: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    import sys
    csv_path = "tunisianet_smartphones.csv"
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]

    # Always write to a NEW file so Excel doesn't overwrite or lock the same file
    base, ext = os.path.splitext(csv_path)
    out_path = f"{base}_filled{ext}"

    print(f"Loading {csv_path}...")
    rows, fieldnames = load_csv(csv_path)
    if not rows:
        print("No rows.")
        return

    # Which canonical models need a lookup (have at least one missing spec)
    models_to_lookup: Set[str] = set()
    key_to_query: Dict[str, str] = {}
    for row in rows:
        key = canonical_key(row)
        if not key:
            continue
        missing = [c for c in SPEC_COLUMNS if not (row.get(c) or "").strip()]
        if missing:
            models_to_lookup.add(key)
            # Store a representative query (brand + model) for this key
            if key not in key_to_query:
                key_to_query[key] = normalize_model_for_search(
                    row.get("model") or "", row.get("brand") or ""
                )

    print(f"Found {len(models_to_lookup)} unique models with missing specs to look up.")

    limit = None
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        limit = int(sys.argv[2])
        print(f"Limit: first {limit} models only.")

    # Fetch specs for each model (deduplicated)
    lookup: Dict[str, Dict[str, str]] = {}
    to_fetch = sorted(models_to_lookup)
    if limit:
        to_fetch = to_fetch[:limit]
    for i, key in enumerate(to_fetch, 1):
        query = key_to_query.get(key) or key
        print(f"  [{i}/{len(to_fetch)}] {query[:55]}...")
        specs = fetch_specs_for_query(query)
        if specs:
            lookup[key] = specs
        else:
            lookup[key] = {}

    # Fill missing values in rows
    filled = 0
    for row in rows:
        key = canonical_key(row)
        if key not in lookup:
            continue
        spec = lookup[key]
        for col in SPEC_COLUMNS:
            if not (row.get(col) or "").strip() and spec.get(col):
                row[col] = spec[col]
                filled += 1

    save_csv(rows, out_path, fieldnames)
    print(f"Filled {filled} missing values. Saved to {out_path} (new file; original unchanged).")


if __name__ == "__main__":
    main()
