"""
Scraper for BestBuyTunisie smartphone category.
Extracts: model, brand, RAM, storage, battery, price, screen, camera, etc.
Output: CSV dataset (bestbuytunisie_smartphones.csv)

WordPress/WooCommerce site – uses requests + BeautifulSoup (static HTML).
"""

import re
import csv
import time
import requests
from urllib.parse import urljoin
from typing import List, Dict, Optional

from bs4 import BeautifulSoup

BASE_URL = "https://bestbuytunisie.tn"
CATEGORY_URL = f"{BASE_URL}/vente/smartphones-smartphone-mobile-tunisie/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm_num(s: str) -> str:
    """Normalize number string: '6,67' -> '6.67'."""
    if not s:
        return ""
    return s.replace(",", ".").strip()


def get_page(url: str, retries: int = 3) -> Optional[BeautifulSoup]:
    """Fetch URL and return BeautifulSoup, or None on error."""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"  Error fetching {url}: {e}")
    return None


# ---------------------------------------------------------------------------
# Spec parsing from text
# ---------------------------------------------------------------------------

def parse_specs_from_text(text: str) -> dict:
    """Extract RAM, storage, battery, screen, camera, OS, network, processor from text."""
    if not text:
        return {}
    text = text.replace("\n", " ").replace("\r", " ")
    specs = {}

    # ---- RAM ----
    # "Mémoire: 4Go", "RAM : 6 Go", "RAM 8 Go", "8Go RAM", "8 Go de RAM"
    for pat in [
        r"M[eé]moire\s*(?:RAM)?\s*:?\s*(\d+)\s*Go",
        r"RAM\s*:?\s*(\d+)\s*Go",
        r"(\d+)\s*Go\s*(?:de\s+)?RAM",
        r"(\d+)\s*Go\s*/\s*\d+\s*Go",           # "4Go/128Go" -> first is RAM
        r"(\d+)\s*Go\s+\+\s+\d+\s*Go",          # "6Go + 128Go"
    ]:
        m = re.search(pat, text, re.I)
        if m:
            v = m.group(1)
            # Sanity: RAM typically 1-24 GB
            if v.isdigit() and 1 <= int(v) <= 24:
                specs["ram_gb"] = v
                break

    # ---- Storage ----
    for pat in [
        r"Stockage\s*:?\s*(\d+)\s*Go",
        r"(?:Capacit[eé]\s+)?[Ss]tockage\s*:?\s*(\d+)",
        r"(\d+)\s*Go\s+(?:de\s+)?stockage",
        r"/\s*(\d+)\s*Go",                       # "4Go/128Go" -> second is storage
        r"(\d+)\s*Go\s*-\s*(?:Noir|Blanc|Bleu|Gold|Silver|Vert|Rose|Gris|Violet|Cyan)",
    ]:
        m = re.search(pat, text, re.I)
        if m:
            v = m.group(1)
            if v.isdigit() and int(v) >= 16:
                specs["storage_gb"] = v
                break

    # ---- Battery ----
    for pat in [
        r"Capacit[eé]\s+de\s+[Bb]atterie\s*:?\s*(\d+)\s*mAh",
        r"Batterie\s*:?\s*(\d+)\s*mAh",
        r"(\d{4,5})\s*mAh",
    ]:
        m = re.search(pat, text, re.I)
        if m:
            specs["battery_mah"] = m.group(1)
            break

    # ---- Screen ----
    for pat in [
        r"[EÉe]cran\s*:?\s*([\d,\.]+)\s*[\"″]",
        r"([\d,\.]+)\s*[\"″]\s*(?:720|1080|1600|2400|HD|IPS|LCD|AMOLED|OLED|TFT|PLS)",
        r"([\d,\.]+)\s*(?:pouces|inch)",
    ]:
        m = re.search(pat, text, re.I)
        if m:
            v = _norm_num(m.group(1))
            try:
                if 3.0 <= float(v) <= 8.0:
                    specs["screen_inches"] = v
                    break
            except ValueError:
                pass

    # ---- Camera rear ----
    for pat in [
        r"[Aa]ppareil\s*[Pp]hoto\s*[Aa]rri[eè]re\s*:?\s*([\d\.]+)\s*MP",
        r"[Aa]rri[eè]re\s*:?\s*([\d\.]+)\s*MP",
        r"[Cc]am[eé]ra\s*[Aa]rri[eè]re\s*:?\s*([\d\.]+)\s*MP",
        r"([\d\.]+)\s*MP\s*\+",                   # "50 MP + 2 MP" -> first
        r"[Pp]rincipale\s*:?\s*([\d\.]+)\s*MP",
    ]:
        m = re.search(pat, text, re.I)
        if m:
            specs["camera_rear_mp"] = m.group(1).rstrip(".")
            break

    # ---- Camera front ----
    for pat in [
        r"[Aa]ppareil\s*[Pp]hoto\s*[Ff]rontale?\s*:?\s*([\d\.]+)\s*MP",
        r"[Ff]rontale?\s*:?\s*([\d\.]+)\s*MP",
        r"[Aa]vant\s*:?\s*([\d\.]+)\s*MP",
        r"[Ss]elfie\s*:?\s*([\d\.]+)\s*MP",
    ]:
        m = re.search(pat, text, re.I)
        if m:
            specs["camera_front_mp"] = m.group(1).rstrip(".")
            break

    # ---- Network ----
    if re.search(r"\b5G\b", text):
        specs["network"] = "5G"
    elif re.search(r"\b4G\b", text):
        specs["network"] = "4G"
    elif re.search(r"\b3G\b", text, re.I):
        specs["network"] = "3G"

    # ---- OS ----
    os_m = re.search(r"[Ss]yst[eè]me?\s+d['']exploitation\s*:?\s*(Android\s*\d+|iOS\s*\d*)", text, re.I)
    if os_m:
        specs["os"] = os_m.group(1).strip()
    if not specs.get("os"):
        os_m = re.search(r"Android\s*(\d+)", text, re.I)
        if os_m:
            specs["os"] = f"Android {os_m.group(1)}"
        elif re.search(r"\biOS\b", text):
            specs["os"] = "iOS"

    # ---- Processor / brand ----
    if re.search(r"Octa[- ]?[Cc]ore", text, re.I):
        specs["processor_type"] = "Octa Core"
    elif re.search(r"Quad[- ]?[Cc]ore", text, re.I):
        specs["processor_type"] = "Quad Core"
    if re.search(r"Snapdragon", text, re.I):
        specs["processor_type"] = "Snapdragon"
    elif re.search(r"MediaTek|Helio|Dimensity", text, re.I):
        specs["processor_type"] = "MediaTek"
    elif re.search(r"Unisoc", text, re.I):
        specs["processor_type"] = "Unisoc"
    elif re.search(r"Apple|A\d+\s+Bionic", text, re.I):
        specs["processor_type"] = "Apple"
    elif re.search(r"Exynos", text, re.I):
        specs["processor_type"] = "Exynos"

    # ---- Warranty ----
    war_m = re.search(r"Garantie\s*:?\s*(\d+\s*an)", text, re.I)
    if war_m:
        specs["warranty"] = war_m.group(1).strip()

    # ---- Color from description ----
    color_m = re.search(r"Couleur\s*:?\s*([A-Za-zéèêëàâùûîïô\s]+?)(?:\s*[-–]|\s*$|\.|,)", text, re.I)
    if color_m:
        c = color_m.group(1).strip()
        if 1 < len(c) <= 25 and not c.isdigit():
            specs["color"] = c

    return specs


# ---------------------------------------------------------------------------
# Price parsing
# ---------------------------------------------------------------------------

def parse_price(text: str) -> str:
    """Extract current price from WooCommerce price text (handles sale prices, DT format)."""
    if not text:
        return ""
    # WooCommerce sale: "Le prix initial était : 289,000 DT.Le prix actuel est : 249,000 DT."
    sale_m = re.search(r"prix\s+actuel\s+est\s*:\s*([\d\s,]+)\s*DT", text, re.I)
    if sale_m:
        return sale_m.group(1).replace(" ", "").replace(",", ".").strip()
    # Regular: "379,000 DT" or "379.000 DT"
    m = re.search(r"([\d\s,\.]+)\s*DT", text)
    if m:
        raw = m.group(1).replace(" ", "")
        # Tunisian format: comma is decimal separator e.g. "379,000" means 379.000
        # If there's a comma, replace with dot
        return raw.replace(",", ".").strip()
    return ""


def parse_old_price(text: str) -> str:
    """Extract original/old price when sale is present."""
    if not text:
        return ""
    old_m = re.search(r"prix\s+initial\s+[eé]tait\s*:\s*([\d\s,]+)\s*DT", text, re.I)
    if old_m:
        return old_m.group(1).replace(" ", "").replace(",", ".").strip()
    return ""


# ---------------------------------------------------------------------------
# Product card extraction
# ---------------------------------------------------------------------------

def get_product_cards(soup: BeautifulSoup):
    """Yield WooCommerce product card elements from category listing page."""
    # WooCommerce standard selectors
    selectors = [
        "ul.products li.product",
        "ul.products li",
        ".products li.product",
        ".products article",
        "li.product",
        ".woocommerce-loop-product",
    ]
    for sel in selectors:
        blocks = soup.select(sel)
        if blocks:
            valid = [b for b in blocks if (
                b.select_one("a[href*='bestbuytunisie']") or
                b.select_one("a[href*='-tunisie/']") or
                re.search(r"[\d,\.]+\s*DT", b.get_text())
            )]
            if valid:
                for block in valid:
                    yield block
                return

    # Fallback: find divs/articles containing product links and prices
    seen = set()
    for a in soup.select("a[href*='-tunisie/']"):
        href = a.get("href", "")
        if "categorie" in href or "vente/" in href:
            continue
        parent = (
            a.find_parent("li") or
            a.find_parent("article") or
            a.find_parent("div", class_=lambda c: c and ("product" in c or "item" in c))
        )
        if parent and id(parent) not in seen:
            text = parent.get_text()
            if re.search(r"[\d,\.]+\s*DT", text) or "stock" in text.lower():
                seen.add(id(parent))
                yield parent


def extract_product_from_card(card) -> dict:
    """Extract fields from one listing-page product card."""
    row = {
        "model": "", "brand": "", "sku": "", "price_dt": "", "old_price_dt": "",
        "ram_gb": "", "storage_gb": "", "battery_mah": "", "screen_inches": "",
        "camera_rear_mp": "", "camera_front_mp": "", "network": "", "os": "",
        "processor_type": "", "color": "", "warranty": "", "in_stock": "",
        "description": "", "url": "",
    }

    # ---- Title & URL ----
    title_el = card.select_one(
        ".woocommerce-loop-product__title, .product-title, h2.entry-title a, h2 a, h3 a"
    )
    if title_el:
        row["model"] = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        if not href:
            a = card.select_one("a[href*='-tunisie/']")
            if a:
                href = a.get("href", "")
        row["url"] = href if href.startswith("http") else urljoin(BASE_URL, href)
    else:
        a = card.select_one("a[href*='-tunisie/']")
        if a:
            row["url"] = a.get("href", "")
            if a.get_text(strip=True):
                row["model"] = a.get_text(strip=True)

    # ---- Price ----
    price_el = card.select_one(
        "ins .woocommerce-Price-amount, "
        ".price ins bdi, "
        "ins bdi, "
        ".woocommerce-Price-amount bdi, "
        ".woocommerce-Price-amount, "
        ".price"
    )
    if price_el:
        price_text = price_el.get_text(separator=" ", strip=True)
        row["price_dt"] = parse_price(price_text)
    if not row["price_dt"]:
        # Try full card text
        full = card.get_text(separator=" ", strip=True)
        row["price_dt"] = parse_price(full)
        row["old_price_dt"] = parse_old_price(full)

    # Old price
    old_el = card.select_one("del .woocommerce-Price-amount, del bdi, .price del bdi")
    if old_el:
        row["old_price_dt"] = parse_price(old_el.get_text(strip=True))

    # ---- Stock ----
    card_text = card.get_text(separator=" ", strip=True)
    if re.search(r"\bEN STOCK\b", card_text, re.I):
        row["in_stock"] = "Oui"
    elif re.search(r"\bEN ARRIVAGE\b", card_text, re.I):
        row["in_stock"] = "En arrivage"
    elif re.search(r"\bSUR COMMANDE\b", card_text, re.I):
        row["in_stock"] = "Sur commande"
    elif re.search(r"[Rr]upture|[Ii]ndisponible|[Éé]puis", card_text):
        row["in_stock"] = "Non"

    # ---- Extract specs from title (RAM/Storage embedded in name) ----
    title = row["model"]
    # Patterns: "4Go 128Go", "4 Go 128 Go", "3Go/64Go", "4Go/128Go"
    ram_storage = re.search(
        r"(\d+)\s*Go\s*/?\s*(\d+)\s*Go",
        title, re.I
    )
    if ram_storage:
        row["ram_gb"] = ram_storage.group(1)
        row["storage_gb"] = ram_storage.group(2)
    else:
        # "2Go 64Go" without separator
        pieces = re.findall(r"(\d+)\s*Go", title, re.I)
        if len(pieces) >= 2:
            if int(pieces[0]) <= 24:
                row["ram_gb"] = pieces[0]
            if int(pieces[1]) >= 16:
                row["storage_gb"] = pieces[1]

    # ---- Network from title ----
    if re.search(r"\b5G\b", title):
        row["network"] = "5G"
    elif re.search(r"\b4G\b", title):
        row["network"] = "4G"

    # ---- Color from title (after "–" or "-") ----
    color_m = re.search(r"[–\-]\s*([A-Za-zéèêëàâùûîïôÉÈÊËÀÂÙÛÎÏÔ][A-Za-zéèêëàâùûîïôÉÈÊËÀÂÙÛÎÏÔ\s]+?)\s*(?:[–\-]|$)", title)
    if color_m:
        c = color_m.group(1).strip()
        if len(c) <= 30 and not re.match(r"^\d", c):
            row["color"] = c

    # ---- SKU / reference from title (after last "–") ----
    sku_m = re.search(r"–\s*([A-Z0-9][A-Z0-9\-\+/]{3,})\s*$", title)
    if sku_m:
        row["sku"] = sku_m.group(1).strip()

    # ---- Brand detection ----
    brands = [
        "Samsung", "Apple", "Xiaomi", "Huawei", "OPPO", "Vivo", "Realme",
        "Honor", "Infinix", "Tecno", "Itel", "TCL", "Nokia", "Motorola",
        "OnePlus", "ZTE", "Alcatel", "Sony", "Google", "Nothing", "Poco",
        "Redmi", "Lesia", "Condor",
    ]
    model_up = row["model"].upper()
    for brand in brands:
        if brand.upper() in model_up:
            row["brand"] = brand
            break

    return row


# ---------------------------------------------------------------------------
# Individual product page fetching
# ---------------------------------------------------------------------------

def fetch_product_detail(url: str) -> dict:
    """Fetch individual product page and extract full specs."""
    extras = {}
    soup = get_page(url)
    if not soup:
        return extras

    # ---- Short description (bullet list) ----
    desc_el = soup.select_one(
        ".woocommerce-product-details__short-description, "
        ".product-short-description, "
        ".short-description, "
        ".entry-summary .description, "
        "[class*='short-desc']"
    )
    desc_text = ""
    if desc_el:
        desc_text = desc_el.get_text(separator=" ", strip=True)

    # Fallback: look for the bullet-point description block (contains "Ecran :", "Mémoire :", etc.)
    if not desc_text or len(desc_text) < 50:
        for el in soup.select(".entry-content p, .product_description p, .woocommerce-Tabs-panel p"):
            t = el.get_text(separator=" ", strip=True)
            if re.search(r"[Ee]cran|M[eé]moire|Stockage|Batterie|Android", t):
                desc_text = t
                break

    extras["description"] = desc_text[:800] if desc_text else ""

    # Parse specs from description text
    if desc_text:
        parsed = parse_specs_from_text(desc_text)
        extras.update(parsed)

    # ---- WooCommerce attribute table ----
    for row in soup.select(
        ".woocommerce-product-attributes tr, "
        "table.woocommerce-product-attributes tr, "
        ".product-attributes tr"
    ):
        th = row.select_one("th, td:first-child")
        td = row.select_one("td:last-child, td:nth-child(2)")
        if not (th and td):
            continue
        label = th.get_text(strip=True).lower()
        value = td.get_text(strip=True)

        if "fabricant" in label or "marque" in label:
            extras["brand"] = value
        elif "m[eé]moire" in label or "ram" in label:
            m = re.search(r"(\d+)", value)
            if m and not extras.get("ram_gb"):
                extras["ram_gb"] = m.group(1)
        elif "stockage" in label:
            m = re.search(r"(\d+)", value)
            if m and not extras.get("storage_gb"):
                extras["storage_gb"] = m.group(1)
        elif "garantie" in label:
            if not extras.get("warranty"):
                extras["warranty"] = value
        elif "processeur" in label:
            if not extras.get("processor_type"):
                extras["processor_type"] = value

    # ---- SKU ----
    sku_el = soup.select_one(".sku, [itemprop='sku'], .sku_wrapper .sku")
    if sku_el:
        extras["sku"] = sku_el.get_text(strip=True)

    # ---- Stock from detail page ----
    stock_text = soup.get_text(separator=" ")
    if not extras.get("in_stock"):
        if re.search(r"\bEN STOCK\b", stock_text, re.I):
            extras["in_stock"] = "Oui"
        elif re.search(r"\bEN ARRIVAGE\b", stock_text, re.I):
            extras["in_stock"] = "En arrivage"
        elif re.search(r"\bSUR COMMANDE\b", stock_text, re.I):
            extras["in_stock"] = "Sur commande"

    return extras


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

def get_total_pages(soup: BeautifulSoup, category_url: str) -> int:
    """Determine total pages from pagination or product count."""
    # WooCommerce: "Affichage de 1–35 sur 261 résultats"
    count_m = re.search(r"sur\s+(\d+)\s+r[eé]sultat", soup.get_text(), re.I)
    if count_m:
        total = int(count_m.group(1))
        # Check how many per page from listing
        cards = list(get_product_cards(soup))
        per_page = max(len(cards), 12)
        return max(1, (total + per_page - 1) // per_page)

    # Pagination links: /page/N/
    last_page = 1
    for a in soup.select(".page-numbers a, .pagination a, a.page-numbers"):
        href = a.get("href", "")
        t = a.get_text(strip=True)
        if t.isdigit():
            last_page = max(last_page, int(t))
        else:
            m = re.search(r"/page/(\d+)/", href)
            if m:
                last_page = max(last_page, int(m.group(1)))
    # Also check next-page links
    for a in soup.select("a.next, a[rel='next']"):
        href = a.get("href", "")
        m = re.search(r"/page/(\d+)/", href)
        if m:
            last_page = max(last_page, int(m.group(1)))
    return last_page


# ---------------------------------------------------------------------------
# Main scraping loop
# ---------------------------------------------------------------------------

def scrape_all_pages(
    max_pages: Optional[int] = None,
    fetch_details: bool = True,
) -> List[Dict]:
    """Scrape all category pages; optionally fetch individual product pages for rich specs."""
    all_products = []

    print("Fetching category page 1...")
    soup = get_page(CATEGORY_URL)
    if not soup:
        print("ERROR: Could not fetch category page.")
        return all_products

    total_pages = get_total_pages(soup, CATEGORY_URL)
    if max_pages is not None:
        total_pages = min(total_pages, max_pages)

    print(f"Found {total_pages} page(s) to scrape.")

    for page in range(1, total_pages + 1):
        if page == 1:
            url = CATEGORY_URL
            page_soup = soup
        else:
            url = f"{CATEGORY_URL}page/{page}/"
            print(f"Fetching page {page}...")
            page_soup = get_page(url)
            if not page_soup:
                print(f"  Skipped page {page} (fetch error).")
                continue

        cards = list(get_product_cards(page_soup))
        for card in cards:
            try:
                prod = extract_product_from_card(card)
                if prod.get("model") or prod.get("price_dt"):
                    all_products.append(prod)
            except Exception as e:
                print(f"  Skip card on page {page}: {e}")

        print(f"  Page {page}/{total_pages} → {len(cards)} cards  (total so far: {len(all_products)})")
        time.sleep(1.0)

    # Deduplicate by URL before detail fetching
    all_products = deduplicate_by_url(all_products)
    print(f"\nAfter dedup: {len(all_products)} unique products.")

    if fetch_details:
        _fetch_detail_pages(all_products)

    return all_products


def _fetch_detail_pages(products: List[Dict]) -> None:
    """For each product with missing specs, fetch its detail page to fill them in."""
    needs_fetch = [
        p for p in products
        if p.get("url") and (
            not p.get("battery_mah") or
            not p.get("screen_inches") or
            not p.get("camera_rear_mp") or
            not p.get("os")
        )
    ]
    print(f"Fetching detail pages for {len(needs_fetch)} products with missing specs...")

    for i, prod in enumerate(needs_fetch, 1):
        extras = fetch_product_detail(prod["url"])
        for key, val in extras.items():
            if key in prod and val and not prod[key]:
                prod[key] = val
        # Always take longer description from detail page
        if extras.get("description") and len(extras["description"]) > len(prod.get("description", "")):
            prod["description"] = extras["description"]

        if i % 25 == 0:
            print(f"  ... fetched {i}/{len(needs_fetch)} detail pages")
        time.sleep(0.5)

    print(f"  Detail fetch complete.")


# ---------------------------------------------------------------------------
# Deduplication & CSV save
# ---------------------------------------------------------------------------

def deduplicate_by_url(products: List[Dict]) -> List[Dict]:
    """Keep first occurrence per URL."""
    seen: set = set()
    out = []
    for p in products:
        url = (p.get("url") or "").strip()
        if url and url not in seen:
            seen.add(url)
            out.append(p)
        elif not url and (p.get("model") or p.get("sku")):
            out.append(p)
    return out


FIELDNAMES = [
    "model", "brand", "sku", "price_dt", "old_price_dt",
    "ram_gb", "storage_gb", "battery_mah", "screen_inches",
    "camera_rear_mp", "camera_front_mp", "network", "os",
    "processor_type", "color", "warranty", "in_stock",
    "description", "url",
]


def save_csv(products: List[Dict], path: str = "bestbuytunisie_smartphones.csv") -> None:
    """Write products to CSV."""
    if not products:
        print("No products to save.")
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        w.writeheader()
        w.writerows(products)
    print(f"Saved {len(products)} products to {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    import sys

    max_pages = None
    fetch_details = True  # default: fetch detail pages for full specs

    for arg in sys.argv[1:]:
        if arg.isdigit():
            max_pages = int(arg)
            print(f"Limiting to first {max_pages} page(s).")
        elif arg == "--no-details":
            fetch_details = False
            print("Skipping individual product detail pages.")

    print("=" * 55)
    print("BestBuyTunisie smartphone scraper")
    print("URL:", CATEGORY_URL)
    print("=" * 55)

    products = scrape_all_pages(max_pages=max_pages, fetch_details=fetch_details)

    out_path = "bestbuytunisie_smartphones.csv"
    save_csv(products, path=out_path)
    print(f"\nDone – {len(products)} products written to {out_path}")


if __name__ == "__main__":
    main()
