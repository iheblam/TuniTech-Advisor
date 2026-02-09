"""
Scraper for Tunisianet smartphone category.
Extracts: model, brand, RAM, storage, battery, price, screen, camera, etc.
Output: CSV dataset (tunisianet_smartphones.csv)
"""

import re
import csv
import time
import requests
from urllib.parse import urljoin
from typing import List, Dict, Optional

from bs4 import BeautifulSoup

BASE_URL = "https://www.tunisianet.com.tn"
CATEGORY_URL = f"{BASE_URL}/596-smartphone-tunisie"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def _norm_num(s: str) -> str:
    """Normalize number: '6,67' -> '6.67'."""
    if not s:
        return ""
    return s.replace(",", ".").strip()


def parse_specs_from_text(text: str) -> dict:
    """Extract RAM, storage, battery, screen, camera, color, OS from product description."""
    if not text:
        return {}
    text = text.replace("\n", " ").replace("\r", " ")
    specs = {}

    # ---- RAM (multiple patterns) ----
    ram_m = re.search(r"RAM\s*(\d+)\s*Go(?:\s+Extensible[^.]*?(\d+)\s*Go)?", text, re.I)
    if ram_m:
        specs["ram_gb"] = ram_m.group(2) if ram_m.group(2) else ram_m.group(1)
    if not specs.get("ram_gb"):
        ram_m = re.search(r"RAM\s*(\d+)\s*Go\s*\(\+\s*(\d+)", text, re.I)
        if ram_m:
            specs["ram_gb"] = ram_m.group(1)
        else:
            ram_m = re.search(r"MÉMOIRE\s*(\d+)\s*Go", text, re.I)
            if ram_m:
                specs["ram_gb"] = ram_m.group(1)
            else:
                ram_m = re.search(r"(\d+)\s*\+\s*(\d+)\s*Go\s*(?:/|RAM|Mémoire|étendus)", text, re.I)
                if ram_m:
                    specs["ram_gb"] = ram_m.group(1)
                else:
                    ram_m = re.search(r"RAM\s*:?\s*(\d+)\s*Go", text, re.I)
                    if ram_m:
                        specs["ram_gb"] = ram_m.group(1)
                    else:
                        ram_m = re.search(r"(\d+)\s*Go\s*\(\+\s*\d+\s*Go\s*étendus", text, re.I)
                        if ram_m:
                            specs["ram_gb"] = ram_m.group(1)

    # ---- Storage ----
    storage_m = re.search(r"(?:Mémoire|Stockage|STOCKAGE)\s*:?\s*(\d+)\s*Go", text, re.I)
    if storage_m:
        specs["storage_gb"] = storage_m.group(1)
    if not specs.get("storage_gb"):
        storage_m = re.search(r"Stockage\s*:?\s*(\d+)", text, re.I)
        if storage_m:
            specs["storage_gb"] = storage_m.group(1)
        else:
            storage_m = re.search(r"/(\d+)\s*Go\s*(?:\||\-|/|\s)", text)
            if storage_m:
                specs["storage_gb"] = storage_m.group(1)

    # ---- Battery ----
    bat_m = re.search(r"(?:Batterie|Capacité de Batterie|Capacité Batterie)\s*:?\s*(\d+)\s*mAh", text, re.I)
    if bat_m:
        specs["battery_mah"] = bat_m.group(1)
    if not specs.get("battery_mah"):
        bat_m = re.search(r"(\d+)\s*mAh", text)
        if bat_m:
            specs["battery_mah"] = bat_m.group(1)

    # ---- Screen (Écran 6.67", 6,67", 6.56" HD+) ----
    screen_m = re.search(r"[EÉ]cran\s*(?:LCD\s*)?(?:IPS\s*)?([\d,]+)\s*[\"']", text, re.I)
    if screen_m:
        specs["screen_inches"] = _norm_num(screen_m.group(1))
    if not specs.get("screen_inches"):
        screen_m = re.search(r"([\d,]+)\s*[\"']\s*(?:pouces|HD|IPS|LCD|TFT)", text, re.I)
        if screen_m:
            specs["screen_inches"] = _norm_num(screen_m.group(1))
        else:
            screen_m = re.search(r"Écran\s*([\d,]+)\s*[\"']", text, re.I)
            if screen_m:
                specs["screen_inches"] = _norm_num(screen_m.group(1))

    # ---- Camera rear ----
    cam_m = re.search(r"(?:Caméra\s*Arrière|Arrière|Appareil Photo Arri[eé]re|principale)\s*:?\s*(\d+)\s*MP", text, re.I)
    if cam_m:
        specs["camera_rear_mp"] = cam_m.group(1)
    if not specs.get("camera_rear_mp"):
        cam_m = re.search(r"Arrière\s*:?\s*(\d+)\s*MP", text, re.I)
        if cam_m:
            specs["camera_rear_mp"] = cam_m.group(1)
        else:
            cam_m = re.search(r"(\d+)\s*MP.*?(?:arrière|Arrière)", text, re.I)
            if cam_m:
                specs["camera_rear_mp"] = cam_m.group(1)
            else:
                cam_m = re.search(r"Photo.*?(\d+)\s*MP", text, re.I)
                if cam_m:
                    specs["camera_rear_mp"] = cam_m.group(1)

    # ---- Camera front ----
    cam_f = re.search(r"(?:Frontale|Avant|Caméra Avant|frontale)\s*:?\s*(\d+)\s*MP", text, re.I)
    if cam_f:
        specs["camera_front_mp"] = cam_f.group(1)
    if not specs.get("camera_front_mp"):
        cam_f = re.search(r"Frontale\s*:?\s*(\d+)", text, re.I)
        if cam_f:
            specs["camera_front_mp"] = cam_f.group(1)

    # ---- Network ----
    if re.search(r"\b5G\b", text):
        specs["network"] = "5G"
    elif re.search(r"\b4G\b", text):
        specs["network"] = "4G"
    elif re.search(r"Réseau\s*3G|3G\b", text, re.I):
        specs["network"] = "3G"

    # ---- OS ----
    os_m = re.search(r"(?:Système|Systéme).*?Android\s*(\d+)", text, re.I)
    if os_m:
        specs["os"] = f"Android {os_m.group(1)}"
    if not specs.get("os"):
        os_m = re.search(r"Android\s*(\d+)", text, re.I)
        if os_m:
            specs["os"] = os_m.group(0)
        elif re.search(r"\biOS\b", text):
            specs["os"] = "iOS"
        else:
            os_m = re.search(r"Funtouch OS\s*\(Android\s*(\d+)\)", text, re.I)
            if os_m:
                specs["os"] = f"Android {os_m.group(1)}"

    # ---- Processor ----
    if re.search(r"Octa[- ]?Core|Octa Core", text, re.I):
        specs["processor_type"] = "Octa Core"
    elif re.search(r"Quad[- ]?Core|Quad core", text, re.I):
        specs["processor_type"] = "Quad Core"
    elif re.search(r"Snapdragon", text, re.I):
        specs["processor_type"] = "Snapdragon"
    elif re.search(r"MediaTek", text, re.I):
        specs["processor_type"] = "MediaTek"
    elif re.search(r"Unisoc", text, re.I):
        specs["processor_type"] = "Unisoc"
    elif re.search(r"Apple", text, re.I):
        specs["processor_type"] = "Apple"

    # ---- Color (from description when not in title) ----
    color_m = re.search(r"Couleur\s*:?\s*([A-Za-zéèêëàâùûîïô\s]+?)(?:\s*-\s*Garantie|\s*$|\.|En stock)", text, re.I)
    if color_m:
        c = color_m.group(1).strip()
        if len(c) <= 25 and not c.isdigit():
            specs["color"] = c.strip()

    return specs


def parse_price(price_text: str) -> str:
    """Extract numeric price from '159,000 DT' -> 159.000 (normalized)."""
    if not price_text:
        return ""
    m = re.search(r"([\d\s,]+)\s*DT", price_text)
    if m:
        return m.group(1).replace(" ", "").replace(",", ".").strip()
    return price_text.replace(",", ".").strip()


def extract_price_from_card(card) -> str:
    """
    Robustly extract the SELLING price (not 'Prix de base', not discount like -50,000 DT).
    Prefer current-price / main price element, then scan card text for best match.
    """
    # 1) Prefer data attribute (PrestaShop often has data-product-price)
    el = card.select_one("[data-product-price], [itemprop='price'], .current-price .price, .product-price-and-shipping .price")
    if el:
        price = el.get("content") or el.get("data-product-price") or el.get_text(strip=True)
        if price and re.match(r"[\d.,]+", price):
            return parse_price(price if "DT" in str(price) else f"{price} DT")
    # 2) .current-price (sale price) before .regular-price
    for sel in (".current-price", ".price.current", ".product-price"):
        el = card.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if "de base" not in t.lower() and "-" not in t.split("DT")[0].strip()[:2]:
                p = parse_price(t)
                if p:
                    return p
    # 3) All "X,XXX DT" in card text; keep SELLING price, reject "Prix de base" and negative
    full_text = card.get_text(separator=" ", strip=True)
    candidates = list(re.finditer(r"([\d\s,]+)\s*DT", full_text))
    best_price = ""
    for m in candidates:
        # Skip discount line (e.g. "-50,000 DT")
        if m.start() > 0 and full_text[m.start() - 1] == "-":
            continue
        # Skip "Prix de base" price: skip only when THIS match is the base (text after "DT" is " Prix de base" with no digit right after "base")
        after = full_text[m.end() : m.end() + 35]
        if re.match(r"\s*Prix\s+de\s+base(?:\s*$|\s(?!\d))", after):
            continue
        price_str = m.group(1).replace(" ", "").replace(",", ".")
        if not price_str.replace(".", "").isdigit() or len(price_str.replace(".", "")) > 6:
            continue
        p = parse_price(m.group(0))
        # Prefer price followed by "Prix Ajouter" or "Prix " (selling price)
        if re.search(r"Prix\s+Ajouter|Prix\s+$|En stock", after):
            return p
        best_price = p
    return best_price or (parse_price(candidates[0].group(0)) if candidates else "")


def get_page(url: str) -> Optional[BeautifulSoup]:
    """Fetch URL and return BeautifulSoup or None."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_product_cards(soup: BeautifulSoup):
    """Yield product card elements (PrestaShop product-miniature or article)."""
    # PrestaShop: .product-miniature or article.js-product-miniature
    blocks = soup.select(".product-miniature, article.js-product-miniature, .item-product, article.item")
    if blocks:
        for block in blocks:
            yield block
        return
    # Fallback: divs that contain both product link and price (DT)
    for div in soup.select("div.thumbnail-container, div.product, div.item"):
        if div.select_one("a[href*='.html']") and re.search(r"[\d,.]+\s*DT", div.get_text()):
            yield div
    # Last resort: unique parents of product links that have price
    seen = set()
    for a in soup.select("a[href*='smartphone'][href*='.html']"):
        parent = a.find_parent("article") or a.find_parent("div", class_=lambda c: c and ("product" in c or "item" in c))
        if parent and id(parent) not in seen and "DT" in parent.get_text():
            seen.add(id(parent))
            yield parent


def extract_product(card) -> dict:
    """Extract fields from one product card."""
    row = {
        "model": "",
        "brand": "",
        "reference": "",
        "price_dt": "",
        "ram_gb": "",
        "storage_gb": "",
        "battery_mah": "",
        "screen_inches": "",
        "camera_rear_mp": "",
        "camera_front_mp": "",
        "network": "",
        "os": "",
        "processor_type": "",
        "color": "",
        "warranty": "",
        "description": "",
        "url": "",
        "in_stock": "",
    }

    # Title / model
    title_el = card.select_one(".product-title a, h2 a, .product-title, h2")
    if title_el:
        row["model"] = title_el.get_text(strip=True)
        link = title_el.get("href") or card.select_one("a.product-thumbnail, a[href*='.html']")
        if link:
            row["url"] = link.get("href", "")

    # Reference code [LESIA-YOUNG1-VR]
    ref_el = card.select_one(".product-reference, .reference")
    if ref_el:
        row["reference"] = ref_el.get_text(strip=True).strip("[]")
    else:
        ref_m = re.search(r"\[([A-Z0-9\-]+)\]", card.get_text())
        if ref_m:
            row["reference"] = ref_m.group(1)

    # Price (robust: avoid "Prix de base" and discount lines)
    row["price_dt"] = extract_price_from_card(card)

    # Short description (for specs)
    desc_el = card.select_one(".product-description-short, .product-desc, .short-desc, .description a")
    desc_text = ""
    if desc_el:
        desc_text = desc_el.get_text(strip=True)
    if not desc_text:
        # Use card text and take a chunk that looks like description (between title and price)
        full = card.get_text(separator=" ", strip=True)
        desc_text = full

    row["description"] = desc_text[:500] if desc_text else ""

    # Parse specs from FULL card text to minimize missing values (not just short description)
    full_card_text = card.get_text(separator=" ", strip=True)
    specs = parse_specs_from_text(full_card_text)
    # Also try model title for "X Go / Y Go" (RAM / Storage)
    if row["model"]:
        title_ram = re.search(r"(\d+)\s*Go\s*/\s*(\d+)\s*Go", row["model"])
        if title_ram and not specs.get("storage_gb"):
            specs["storage_gb"] = title_ram.group(2)
        if title_ram and not specs.get("ram_gb"):
            specs["ram_gb"] = title_ram.group(1)
    for k, v in specs.items():
        if k in row and v:
            row[k] = v

    # Brand (from manufacturer block or first word of model after "Smartphone"/"Téléphone")
    brand_el = card.select_one(".manufacturer a, .product-manufacturer a, .brand a")
    if brand_el:
        row["brand"] = brand_el.get_text(strip=True) or ""
    if not row["brand"]:
        img = card.select_one("img[alt][src*='img/m/']")
        if img and img.get("alt"):
            row["brand"] = img.get("alt", "").strip()
    if not row["brand"] and row["model"]:
        parts = re.sub(r"^(Smartphone|Téléphone Portable)\s+", "", row["model"], flags=re.I).strip().split()
        if parts:
            row["brand"] = parts[0]

    # Color from title: "| Vert", "- Noir", "/ Bleu"
    color_m = re.search(r"[\|\/\-]\s*([A-Za-zéèêëàâùûîïô\s]+)\s*$", row["model"])
    if color_m:
        row["color"] = color_m.group(1).strip()
    if not row["color"] and specs.get("color"):
        row["color"] = specs["color"]

    # Warranty
    if re.search(r"Garantie\s*(\d+\s*an)", desc_text, re.I):
        row["warranty"] = re.search(r"Garantie\s*(\d+\s*an)", desc_text, re.I).group(1)
    if re.search(r"(\d+)\s*an", desc_text) and not row["warranty"]:
        row["warranty"] = re.search(r"(\d+)\s*an", desc_text).group(0)

    # Stock
    if card.select_one(".availability span.available, .in-stock, .stock-available"):
        row["in_stock"] = "Oui"
    elif "En stock" in card.get_text():
        row["in_stock"] = "Oui"
    else:
        row["in_stock"] = ""

    # Ensure URL is absolute
    if row["url"] and not row["url"].startswith("http"):
        row["url"] = urljoin(BASE_URL, row["url"])

    return row


def get_total_pages(soup: BeautifulSoup) -> int:
    """Infer total pages from pagination or product count."""
    # "Il y a 369 produits" -> 369, 24 per page -> 16 pages
    text = soup.get_text()
    m = re.search(r"(\d+)\s*produits?", text, re.I)
    if m:
        total = int(m.group(1))
        return max(1, (total + 23) // 24)
    # Pagination links
    last_page = 1
    for a in soup.select(".page-list a, .pagination a"):
        t = a.get_text(strip=True)
        if t.isdigit():
            last_page = max(last_page, int(t))
    return last_page


def scrape_all_pages(max_pages: Optional[int] = None) -> List[Dict]:
    """Scrape category and all pagination; return list of product dicts."""
    all_products = []
    soup = get_page(CATEGORY_URL)
    if not soup:
        return all_products

    total_pages = get_total_pages(soup)
    if max_pages is not None:
        total_pages = min(total_pages, max_pages)

    print(f"Scraping up to {total_pages} page(s)...")

    # Use same URL format as site: ?page=N&order=product.price.asc (price ascending)
    for page in range(1, total_pages + 1):
        if page == 1:
            url = f"{CATEGORY_URL}?order=product.price.asc"
        else:
            url = f"{CATEGORY_URL}?page={page}&order=product.price.asc"
        soup = get_page(url)
        if not soup:
            continue

        cards = list(get_product_cards(soup))
        if not cards:
            # Try alternative: look for product links in main content
            main = soup.select_one("#products, .products, main, .product-list")
            if main:
                for a in main.select("a[href*='smartphone'][href*='.html']"):
                    parent = a.find_parent("article") or a.find_parent("div", class_=re.compile(r"product|item"))
                    if parent and parent not in [p.get("_parent") for p in all_products]:
                        cards = [parent]
                        break
        for card in cards:
            try:
                prod = extract_product(card)
                if prod.get("model") or prod.get("price_dt"):
                    all_products.append(prod)
            except Exception as e:
                print(f"Skip product on page {page}: {e}")

        print(f"  Page {page}/{total_pages} -> {len(cards)} products (total: {len(all_products)})")
        time.sleep(0.8)

    return all_products


def deduplicate_by_url(products: List[Dict]) -> List[Dict]:
    """Keep one row per product URL (first occurrence)."""
    seen = set()
    out = []
    for p in products:
        url = (p.get("url") or "").strip()
        if url and url not in seen:
            seen.add(url)
            out.append(p)
        elif not url and (p.get("model") or p.get("reference")):
            out.append(p)
    return out


def save_csv(products: List[Dict], path: str = "tunisianet_smartphones.csv") -> None:
    """Write products to CSV with all keys as columns."""
    products = deduplicate_by_url(products)
    if not products:
        print("No products to save.")
        return
    fieldnames = [
        "model", "brand", "reference", "price_dt", "ram_gb", "storage_gb",
        "battery_mah", "screen_inches", "camera_rear_mp", "camera_front_mp",
        "network", "os", "processor_type", "color", "warranty", "in_stock",
        "description", "url",
    ]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(products)
    print(f"Saved {len(products)} products to {path}")


def main():
    import sys
    max_pages = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        max_pages = int(sys.argv[1])
        print(f"Limiting to first {max_pages} page(s).")
    print("Tunisianet smartphone scraper")
    print("URL:", CATEGORY_URL)
    products = scrape_all_pages(max_pages=max_pages)
    # Always save to a NEW file so Excel doesn't overwrite or lock the same file
    out_path = "tunisianet_smartphones_export.csv"
    save_csv(products, path=out_path)
    print("Done. Open", out_path, "in Excel (this file is never overwritten by the script).")


if __name__ == "__main__":
    main()
