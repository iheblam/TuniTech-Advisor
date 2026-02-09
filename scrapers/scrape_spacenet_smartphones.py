"""
Scraper for SpaceNet.tn smartphone category.
Extracts: model, brand, RAM, storage, battery, price, screen, camera, etc.
Output: CSV dataset (spacenet_smartphones.csv)
"""

import re
import csv
import time
import requests
from urllib.parse import urljoin
from typing import List, Dict, Optional

from bs4 import BeautifulSoup

BASE_URL = "https://spacenet.tn"
CATEGORY_URL = f"{BASE_URL}/130-smartphone-tunisie"
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
    ram_m = re.search(r"RAM\s*:?\s*(\d+)\s*Go", text, re.I)
    if ram_m:
        specs["ram_gb"] = ram_m.group(1)
    if not specs.get("ram_gb"):
        ram_m = re.search(r"Mémoire\s*Ram\s*:?\s*(\d+)\s*Go", text, re.I)
        if ram_m:
            specs["ram_gb"] = ram_m.group(1)
    if not specs.get("ram_gb"):
        ram_m = re.search(r"(\d+)\s*Go\s*RAM", text, re.I)
        if ram_m:
            specs["ram_gb"] = ram_m.group(1)
    if not specs.get("ram_gb"):
        # Title pattern: "4Go 64Go" (RAM then Storage)
        ram_m = re.search(r"(\d+)Go\s+(\d+)Go", text)
        if ram_m:
            specs["ram_gb"] = ram_m.group(1)

    # ---- Storage ----
    storage_m = re.search(r"Stockage\s*:?\s*(\d+)\s*Go", text, re.I)
    if storage_m:
        specs["storage_gb"] = storage_m.group(1)
    if not specs.get("storage_gb"):
        storage_m = re.search(r"Mémoire\s*(?:interne)?\s*:?\s*(\d+)\s*Go", text, re.I)
        if storage_m:
            specs["storage_gb"] = storage_m.group(1)
    if not specs.get("storage_gb"):
        # Title pattern: "4Go 64Go" (RAM then Storage)
        storage_m = re.search(r"(\d+)Go\s+(\d+)Go", text)
        if storage_m:
            specs["storage_gb"] = storage_m.group(2)
    if not specs.get("storage_gb"):
        storage_m = re.search(r"(\d+)\s*Go\s*(?:stockage|interne|ROM)", text, re.I)
        if storage_m:
            specs["storage_gb"] = storage_m.group(1)

    # ---- Battery ----
    bat_m = re.search(r"(?:Batterie|Capacité)\s*(?:de la batterie)?\s*:?\s*(\d+)\s*mAh", text, re.I)
    if bat_m:
        specs["battery_mah"] = bat_m.group(1)
    if not specs.get("battery_mah"):
        bat_m = re.search(r"(\d{4,5})\s*mAh", text)
        if bat_m:
            specs["battery_mah"] = bat_m.group(1)

    # ---- Screen ----
    screen_m = re.search(r"[EÉ]cran\s*(?:LCD\s*)?(?:IPS\s*)?([\d,\.]+)\s*[\"'\s]*(?:pouces|Pouces)?", text, re.I)
    if screen_m:
        specs["screen_inches"] = _norm_num(screen_m.group(1))
    if not specs.get("screen_inches"):
        screen_m = re.search(r"Taille\s*(?:de l'écran)?\s*:?\s*([\d,\.]+)\s*(?:pouces|Pouces|\")", text, re.I)
        if screen_m:
            specs["screen_inches"] = _norm_num(screen_m.group(1))
    if not specs.get("screen_inches"):
        screen_m = re.search(r"([\d,\.]+)\s*[\"']\s*(?:pouces|HD|IPS|LCD|TFT|Amoled|FHD)", text, re.I)
        if screen_m:
            specs["screen_inches"] = _norm_num(screen_m.group(1))

    # ---- Camera rear ----
    cam_m = re.search(r"(?:Caméra\s*Arrière|Appareil Photo|principale)\s*:?\s*(\d+)\s*(?:MP|Mégapixels)", text, re.I)
    if cam_m:
        specs["camera_rear_mp"] = cam_m.group(1)
    if not specs.get("camera_rear_mp"):
        cam_m = re.search(r"(\d+)\s*(?:MP|Mégapixels).*?(?:arrière|principale)", text, re.I)
        if cam_m:
            specs["camera_rear_mp"] = cam_m.group(1)
    if not specs.get("camera_rear_mp"):
        cam_m = re.search(r"(\d+)\s*MP", text)
        if cam_m:
            specs["camera_rear_mp"] = cam_m.group(1)

    # ---- Camera front ----
    cam_f = re.search(r"(?:Frontale|Avant|Selfie)\s*:?\s*(\d+)\s*(?:MP|Mégapixels)", text, re.I)
    if cam_f:
        specs["camera_front_mp"] = cam_f.group(1)
    if not specs.get("camera_front_mp"):
        cam_f = re.search(r"(\d+)\s*(?:MP|Mégapixels).*?(?:frontale|avant|selfie)", text, re.I)
        if cam_f:
            specs["camera_front_mp"] = cam_f.group(1)

    # ---- Network ----
    if re.search(r"\b5G\b", text):
        specs["network"] = "5G"
    elif re.search(r"\b4G\b|LTE", text):
        specs["network"] = "4G"
    elif re.search(r"\b3G\b", text):
        specs["network"] = "3G"

    # ---- OS ----
    os_m = re.search(r"Android\s*(\d+)", text, re.I)
    if os_m:
        specs["os"] = f"Android {os_m.group(1)}"
    if not specs.get("os"):
        if re.search(r"ColorOS\s*(\d+)", text, re.I):
            m = re.search(r"ColorOS\s*([\d\.]+)", text, re.I)
            specs["os"] = f"ColorOS {m.group(1)}" if m else "ColorOS"
        elif re.search(r"MagicOS\s*([\d\.]+)", text, re.I):
            m = re.search(r"MagicOS\s*([\d\.]+)", text, re.I)
            specs["os"] = f"MagicOS {m.group(1)}" if m else "MagicOS"
        elif re.search(r"MIUI\s*(\d+)", text, re.I):
            m = re.search(r"MIUI\s*(\d+)", text, re.I)
            specs["os"] = f"MIUI {m.group(1)}" if m else "MIUI"
        elif re.search(r"One\s*UI\s*([\d\.]+)", text, re.I):
            m = re.search(r"One\s*UI\s*([\d\.]+)", text, re.I)
            specs["os"] = f"One UI {m.group(1)}" if m else "One UI"
        elif re.search(r"\biOS\b", text):
            specs["os"] = "iOS"

    # ---- Processor ----
    if re.search(r"Octa[- ]?Core|Octa\s*Core", text, re.I):
        specs["processor_type"] = "Octa Core"
    elif re.search(r"Quad[- ]?Core|Quad\s*Core", text, re.I):
        specs["processor_type"] = "Quad Core"
    elif re.search(r"Snapdragon", text, re.I):
        specs["processor_type"] = "Snapdragon"
    elif re.search(r"MediaTek|Helio", text, re.I):
        specs["processor_type"] = "MediaTek"
    elif re.search(r"Unisoc", text, re.I):
        specs["processor_type"] = "Unisoc"
    elif re.search(r"Exynos", text, re.I):
        specs["processor_type"] = "Exynos"
    elif re.search(r"Apple\s*A\d+", text, re.I):
        specs["processor_type"] = "Apple"

    # ---- Color ----
    color_m = re.search(r"Couleur\s*:?\s*([A-Za-zéèêëàâùûîïôÉÈ\s]+?)(?:\s*-|\s*$|\.|,|En stock)", text, re.I)
    if color_m:
        c = color_m.group(1).strip()
        if len(c) <= 25 and not c.isdigit():
            specs["color"] = c

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
    Robustly extract the SELLING price (not crossed-out price).
    SpaceNet shows promo prices before regular prices.
    """
    # Look for main price element
    el = card.select_one(".product-price, .price, [itemprop='price']")
    if el:
        price = el.get("content") or el.get_text(strip=True)
        if price and re.match(r"[\d.,]+", str(price)):
            return parse_price(price if "DT" in str(price) else f"{price} DT")
    
    # Get all prices from card text and take the selling price (usually first non-crossed)
    full_text = card.get_text(separator=" ", strip=True)
    # SpaceNet format: "399,000 DT229,000 DT" (old price then new price without space)
    # Or just "159,000 DT"
    prices = list(re.finditer(r"([\d,]+)\s*DT", full_text))
    
    if len(prices) >= 2:
        # If there are two prices, the second is usually the sale price
        return parse_price(prices[1].group(0))
    elif len(prices) == 1:
        return parse_price(prices[0].group(0))
    
    return ""


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
    """Yield product card elements from SpaceNet page."""
    # SpaceNet uses PrestaShop-like structure
    blocks = soup.select(".product-miniature, article.js-product-miniature, .item-product, article.item")
    if blocks:
        for block in blocks:
            yield block
        return
    
    # Fallback: look for product containers with links and prices
    for div in soup.select("div.thumbnail-container, div.product, div.item"):
        if div.select_one("a[href*='.html']") and re.search(r"[\d,.]+\s*DT", div.get_text()):
            yield div
    
    # Last resort: find unique parents of product links
    seen = set()
    for a in soup.select("a[href*='smartphone'][href*='.html']"):
        parent = a.find_parent("article") or a.find_parent("div", class_=lambda c: c and ("product" in str(c) or "item" in str(c)))
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
    title_el = card.select_one(".product-title a, h2 a, h3 a, .product-title, h2, h3")
    if title_el:
        row["model"] = title_el.get_text(strip=True)
        link = title_el.get("href")
        if not link:
            link_el = card.select_one("a.product-thumbnail, a[href*='.html']")
            if link_el:
                link = link_el.get("href", "")
        row["url"] = link or ""

    # Reference code
    ref_el = card.select_one(".product-reference, .reference")
    if ref_el:
        row["reference"] = ref_el.get_text(strip=True).strip("[]")
    else:
        # Look for "Réf :" pattern
        ref_m = re.search(r"Réf\s*:?\s*([A-Z0-9\-/]+)", card.get_text())
        if ref_m:
            row["reference"] = ref_m.group(1)

    # Price
    row["price_dt"] = extract_price_from_card(card)

    # Description text from card
    desc_el = card.select_one(".product-description-short, .product-desc, .short-desc")
    desc_text = ""
    if desc_el:
        desc_text = desc_el.get_text(strip=True)
    if not desc_text:
        desc_text = card.get_text(separator=" ", strip=True)
    row["description"] = desc_text[:500] if desc_text else ""

    # Parse specs from model title and card text
    full_card_text = card.get_text(separator=" ", strip=True)
    specs = parse_specs_from_text(full_card_text)
    
    # Also parse from model title (e.g., "Smartphone Samsung Galaxy A16 4Go 128Go Bleu")
    if row["model"]:
        title_specs = parse_specs_from_text(row["model"])
        for k, v in title_specs.items():
            if k not in specs or not specs[k]:
                specs[k] = v
        
        # Direct pattern: "XGo YGo" in title
        title_ram = re.search(r"(\d+)Go\s+(\d+)Go", row["model"])
        if title_ram:
            if not specs.get("ram_gb"):
                specs["ram_gb"] = title_ram.group(1)
            if not specs.get("storage_gb"):
                specs["storage_gb"] = title_ram.group(2)
    
    for k, v in specs.items():
        if k in row and v:
            row[k] = v

    # Brand (from manufacturer image or first word of model)
    brand_el = card.select_one(".manufacturer a, .product-manufacturer a, .brand a")
    if brand_el:
        row["brand"] = brand_el.get_text(strip=True)
    if not row["brand"]:
        img = card.select_one("img[alt][src*='img/m/']")
        if img and img.get("alt"):
            row["brand"] = img.get("alt", "").strip()
    if not row["brand"] and row["model"]:
        # Extract brand from model name
        model_clean = re.sub(r"^(Smartphone|Téléphone Portable)\s+", "", row["model"], flags=re.I).strip()
        parts = model_clean.split()
        if parts:
            row["brand"] = parts[0]

    # Color from title: last word or after separator
    if not row["color"]:
        color_m = re.search(r"[\s\|\/\-]+([A-Za-zéèêëàâùûîïôÉÈ]+)\s*$", row["model"])
        if color_m:
            potential_color = color_m.group(1).strip()
            # List of common colors
            colors = ["Noir", "Blanc", "Bleu", "Vert", "Rose", "Rouge", "Gold", "Silver", 
                      "Gris", "Violet", "Orange", "Cyan", "Lime", "Caramel", "Lavande"]
            if potential_color in colors or potential_color.lower() in [c.lower() for c in colors]:
                row["color"] = potential_color

    # Warranty
    warranty_m = re.search(r"Garantie\s*:?\s*(\d+\s*(?:an|mois))", desc_text, re.I)
    if warranty_m:
        row["warranty"] = warranty_m.group(1)
    elif re.search(r"(\d+)\s*an", desc_text, re.I):
        m = re.search(r"(\d+)\s*an", desc_text, re.I)
        row["warranty"] = m.group(0)

    # Stock
    if card.select_one(".availability span.available, .in-stock, .stock-available"):
        row["in_stock"] = "Oui"
    elif "En stock" in card.get_text():
        row["in_stock"] = "Oui"
    elif "Sur commande" in card.get_text():
        row["in_stock"] = "Sur commande"
    else:
        row["in_stock"] = ""

    # Ensure URL is absolute
    if row["url"] and not row["url"].startswith("http"):
        row["url"] = urljoin(BASE_URL, row["url"])

    return row


def get_product_details(url: str) -> dict:
    """Fetch product page and extract additional details."""
    details = {}
    soup = get_page(url)
    if not soup:
        return details
    
    # Look for product features/specs table
    features = soup.select(".product-features li, .data-sheet tr, .product-information li")
    for feat in features:
        text = feat.get_text(separator=" ", strip=True)
        specs = parse_specs_from_text(text)
        for k, v in specs.items():
            if v and k not in details:
                details[k] = v
    
    # Look for description
    desc_el = soup.select_one(".product-description, #description, .tab-content")
    if desc_el:
        desc_text = desc_el.get_text(separator=" ", strip=True)
        specs = parse_specs_from_text(desc_text)
        for k, v in specs.items():
            if v and k not in details:
                details[k] = v
    
    return details


def get_total_pages(soup: BeautifulSoup) -> int:
    """Infer total pages from pagination or product count."""
    # Look for "Afficher 1-20 dans 320 produits"
    text = soup.get_text()
    m = re.search(r"(\d+)\s*produits?", text, re.I)
    if m:
        total = int(m.group(1))
        return max(1, (total + 19) // 20)  # SpaceNet shows 20 products per page
    
    # Check pagination links
    last_page = 1
    for a in soup.select(".page-list a, .pagination a, a[href*='page=']"):
        href = a.get("href", "")
        m = re.search(r"page=(\d+)", href)
        if m:
            last_page = max(last_page, int(m.group(1)))
        t = a.get_text(strip=True)
        if t.isdigit():
            last_page = max(last_page, int(t))
    
    return last_page


def scrape_all_pages(max_pages: Optional[int] = None, fetch_details: bool = False) -> List[Dict]:
    """Scrape category and all pagination; return list of product dicts."""
    all_products = []
    soup = get_page(CATEGORY_URL)
    if not soup:
        return all_products

    total_pages = get_total_pages(soup)
    if max_pages is not None:
        total_pages = min(total_pages, max_pages)

    print(f"Scraping up to {total_pages} page(s)...")

    for page in range(1, total_pages + 1):
        if page == 1:
            url = CATEGORY_URL
        else:
            url = f"{CATEGORY_URL}?page={page}"
        
        soup = get_page(url)
        if not soup:
            continue

        cards = list(get_product_cards(soup))
        page_products = []
        
        for card in cards:
            try:
                prod = extract_product(card)
                if prod.get("model") or prod.get("price_dt"):
                    # Optionally fetch detailed page for more specs
                    if fetch_details and prod.get("url"):
                        details = get_product_details(prod["url"])
                        for k, v in details.items():
                            if k in prod and not prod[k] and v:
                                prod[k] = v
                        time.sleep(0.3)  # Be gentle with the server
                    
                    page_products.append(prod)
            except Exception as e:
                print(f"Skip product on page {page}: {e}")

        all_products.extend(page_products)
        print(f"  Page {page}/{total_pages} -> {len(page_products)} products (total: {len(all_products)})")
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


def save_csv(products: List[Dict], path: str = "spacenet_smartphones.csv") -> None:
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
    fetch_details = False
    
    for arg in sys.argv[1:]:
        if arg.isdigit():
            max_pages = int(arg)
            print(f"Limiting to first {max_pages} page(s).")
        elif arg == "--details":
            fetch_details = True
            print("Will fetch individual product pages for more details.")
    
    print("SpaceNet.tn smartphone scraper")
    print("URL:", CATEGORY_URL)
    products = scrape_all_pages(max_pages=max_pages, fetch_details=fetch_details)
    
    # Save to dataset folder
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(os.path.dirname(script_dir), "dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    out_path = os.path.join(dataset_dir, "spacenet_smartphones.csv")
    
    save_csv(products, path=out_path)
    print("Done. Open", out_path, "in Excel.")


if __name__ == "__main__":
    main()
