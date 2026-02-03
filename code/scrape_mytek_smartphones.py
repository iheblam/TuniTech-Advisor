"""
Scraper for Mytek.tn smartphone category.
Extracts: model, brand, RAM, storage, battery, price, screen, camera, etc.
Output: CSV dataset (mytek_smartphones.csv)

Uses Selenium for JavaScript rendering.
"""

import re
import csv
import time
from urllib.parse import urljoin
from typing import List, Dict, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.mytek.tn"
CATEGORY_URL = f"{BASE_URL}/smartphone.html"


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
    ram_m = re.search(r"(?:Mémoire\s*)?RAM\s*:?\s*(\d+)\s*Go", text, re.I)
    if ram_m:
        specs["ram_gb"] = ram_m.group(1)
    if not specs.get("ram_gb"):
        ram_m = re.search(r"Mémoire\s*:?\s*(\d+)\s*Go", text, re.I)
        if ram_m:
            specs["ram_gb"] = ram_m.group(1)
    if not specs.get("ram_gb"):
        ram_m = re.search(r"(\d+)\s*Go\s*\+\s*\d+\s*Go", text, re.I)
        if ram_m:
            specs["ram_gb"] = ram_m.group(1)
    if not specs.get("ram_gb"):
        ram_m = re.search(r"(\d+)\s*\+\s*\d+\s*Go", text, re.I)
        if ram_m:
            specs["ram_gb"] = ram_m.group(1)

    # ---- Storage ----
    storage_m = re.search(r"(?:Capacité\s*)?Stockage\s*:?\s*(\d+)\s*Go", text, re.I)
    if storage_m:
        specs["storage_gb"] = storage_m.group(1)
    if not specs.get("storage_gb"):
        storage_m = re.search(r"Stockage\s*:?\s*(\d+)", text, re.I)
        if storage_m:
            specs["storage_gb"] = storage_m.group(1)
    if not specs.get("storage_gb"):
        storage_m = re.search(r"/(\d+)Go", text)
        if storage_m:
            specs["storage_gb"] = storage_m.group(1)
    if not specs.get("storage_gb"):
        storage_m = re.search(r"(\d+)\s*Go\s*-\s*(?:Noir|Blanc|Bleu|Gold|Silver|Vert|Rose)", text, re.I)
        if storage_m:
            specs["storage_gb"] = storage_m.group(1)

    # ---- Battery ----
    bat_m = re.search(r"(?:Batterie|Capacité de la batterie|Capacité Batterie)\s*:?\s*(\d+)\s*mAh", text, re.I)
    if bat_m:
        specs["battery_mah"] = bat_m.group(1)
    if not specs.get("battery_mah"):
        bat_m = re.search(r"(\d{4,5})\s*mAh", text)
        if bat_m:
            specs["battery_mah"] = bat_m.group(1)

    # ---- Screen ----
    screen_m = re.search(r"[EÉ]cran\s*([\d,\.]+)\s*[\"']?\s*(?:pouces|HD|IPS|LCD|TFT)?", text, re.I)
    if screen_m:
        specs["screen_inches"] = _norm_num(screen_m.group(1))
    if not specs.get("screen_inches"):
        screen_m = re.search(r"([\d,\.]+)\s*[\"']\s*(?:pouces|HD|IPS|LCD)", text, re.I)
        if screen_m:
            specs["screen_inches"] = _norm_num(screen_m.group(1))
    if not specs.get("screen_inches"):
        screen_m = re.search(r"([\d,\.]+)\s*pouces", text, re.I)
        if screen_m:
            specs["screen_inches"] = _norm_num(screen_m.group(1))

    # ---- Camera rear ----
    cam_m = re.search(r"(?:Appareil\s*[Pp]hoto\s*)?(?:Arri[eè]re)\s*:?\s*(\d+)\s*(?:MP|Mégapixels?)", text, re.I)
    if cam_m:
        specs["camera_rear_mp"] = cam_m.group(1)
    if not specs.get("camera_rear_mp"):
        cam_m = re.search(r"(\d+)\s*(?:MP|Mégapixels?).*?(?:arri[eè]re|principal)", text, re.I)
        if cam_m:
            specs["camera_rear_mp"] = cam_m.group(1)
    if not specs.get("camera_rear_mp"):
        cam_m = re.search(r"photo\s*Arri[eè]re\s*:?\s*(\d+)", text, re.I)
        if cam_m:
            specs["camera_rear_mp"] = cam_m.group(1)

    # ---- Camera front ----
    cam_f = re.search(r"(?:Appareil\s*[Pp]hoto\s*)?(?:Avant|Frontale?)\s*:?\s*(\d+)\s*(?:MP|Mégapixels?)", text, re.I)
    if cam_f:
        specs["camera_front_mp"] = cam_f.group(1)
    if not specs.get("camera_front_mp"):
        cam_f = re.search(r"Avant\s*:?\s*(\d+)", text, re.I)
        if cam_f:
            specs["camera_front_mp"] = cam_f.group(1)

    # ---- Network ----
    if re.search(r"\b5G\b", text):
        specs["network"] = "5G"
    elif re.search(r"\b4G\b", text):
        specs["network"] = "4G"
    elif re.search(r"\b3G\b", text, re.I):
        specs["network"] = "3G"

    # ---- OS ----
    os_m = re.search(r"(?:Système\s*d['']exploitation|OS)\s*:?\s*(Android\s*\d+|iOS\s*\d*)", text, re.I)
    if os_m:
        specs["os"] = os_m.group(1).strip()
    if not specs.get("os"):
        os_m = re.search(r"Android\s*(\d+)", text, re.I)
        if os_m:
            specs["os"] = f"Android {os_m.group(1)}"
        elif re.search(r"\biOS\b", text):
            specs["os"] = "iOS"

    # ---- Processor ----
    if re.search(r"Octa[- ]?[Cc]ore", text, re.I):
        specs["processor_type"] = "Octa Core"
    elif re.search(r"Quad[- ]?[Cc]ore", text, re.I):
        specs["processor_type"] = "Quad Core"
    elif re.search(r"Snapdragon", text, re.I):
        specs["processor_type"] = "Snapdragon"
    elif re.search(r"MediaTek|Helio", text, re.I):
        specs["processor_type"] = "MediaTek"
    elif re.search(r"Unisoc", text, re.I):
        specs["processor_type"] = "Unisoc"
    elif re.search(r"Apple|A\d+\s+Bionic", text, re.I):
        specs["processor_type"] = "Apple"
    elif re.search(r"Exynos", text, re.I):
        specs["processor_type"] = "Exynos"

    return specs


def parse_price(price_text: str) -> str:
    """Extract numeric price from '159,000 DT' -> 159.000 (normalized)."""
    if not price_text:
        return ""
    # Find the pattern like "179,000 DT" or "1 299,000 DT"
    m = re.search(r"([\d\s,]+)\s*DT", price_text)
    if m:
        return m.group(1).replace(" ", "").replace(",", ".").strip()
    return price_text.replace(",", ".").strip()


def create_driver():
    """Create a headless Chrome driver."""
    print("  Setting up Chrome options...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        print("  Installing/locating ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        print("  Starting Chrome browser...")
        driver = webdriver.Chrome(service=service, options=options)
        print("  Chrome driver ready!")
        return driver
    except Exception as e:
        print(f"  ERROR creating Chrome driver: {e}")
        raise


def get_page_with_driver(driver, url: str, wait_time: int = 5) -> Optional[BeautifulSoup]:
    """Fetch URL using Selenium and return BeautifulSoup."""
    try:
        driver.get(url)
        # Wait for products to load
        time.sleep(wait_time)
        # Try to wait for product elements
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item, .product-item-info, .products-grid li, [data-product-id]"))
            )
        except:
            pass  # Continue even if specific elements not found
        return BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_product_cards(soup: BeautifulSoup):
    """Yield product card elements from Mytek (Magento-based)."""
    # Try various Magento selectors
    selectors = [
        ".product-item",
        ".product-item-info", 
        "li.product-item",
        ".products-grid li.item",
        ".products.list .product-item",
        "ol.products.list li",
        ".products-grid .product-item-info",
        "[data-product-id]",
    ]
    
    for sel in selectors:
        blocks = soup.select(sel)
        if blocks and len(blocks) > 0:
            # Verify these are actual product blocks (have price or link)
            valid_blocks = [b for b in blocks if (
                b.select_one("a[href*='.html']") or 
                re.search(r"[\d,.]+\s*DT", b.get_text()) or
                b.get("data-product-id")
            )]
            if valid_blocks:
                for block in valid_blocks:
                    yield block
                return
    
    # Fallback: find any element with product-like structure
    for el in soup.select("li, div, article"):
        text = el.get_text()
        # Must have price pattern and product link
        if (re.search(r"\d{2,3},\d{3}\s*DT", text) and 
            el.select_one("a[href*='.html']") and
            len(text) > 50 and len(text) < 3000):
            yield el


def extract_product(card) -> dict:
    """Extract fields from one product card."""
    row = {
        "model": "",
        "brand": "",
        "reference": "",
        "price_dt": "",
        "old_price_dt": "",
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
    title_el = card.select_one(".product-item-link, .product-name a, h2 a, .product-item-name a, a.product-item-link")
    if title_el:
        row["model"] = title_el.get_text(strip=True)
        row["url"] = title_el.get("href", "")
    else:
        # Try other approaches
        link = card.select_one("a[href*='.html']")
        if link:
            row["url"] = link.get("href", "")
            if link.get_text(strip=True):
                row["model"] = link.get_text(strip=True)

    # Reference code [YOUNG6-2/16-WHITE]
    ref_m = re.search(r"\[([A-Z0-9\-/]+)\]", card.get_text())
    if ref_m:
        row["reference"] = ref_m.group(1)

    # Price - current/special price
    price_el = card.select_one(".price-wrapper .price, .special-price .price, .price-box .price, [data-price-type='finalPrice'] .price")
    if price_el:
        row["price_dt"] = parse_price(price_el.get_text(strip=True))
    else:
        # Try to find price from text
        text = card.get_text()
        prices = re.findall(r"([\d\s,]+)\s*DT", text)
        if prices:
            # Last price is usually the current price
            row["price_dt"] = parse_price(prices[-1] + " DT")
            if len(prices) > 1:
                row["old_price_dt"] = parse_price(prices[0] + " DT")

    # Old price (barred)
    old_price_el = card.select_one(".old-price .price, .price-box .old-price .price")
    if old_price_el:
        row["old_price_dt"] = parse_price(old_price_el.get_text(strip=True))

    # Description
    desc_el = card.select_one(".product-item-description, .product-description, .description")
    desc_text = ""
    if desc_el:
        desc_text = desc_el.get_text(strip=True)
    if not desc_text:
        # Use full card text
        desc_text = card.get_text(separator=" ", strip=True)
    row["description"] = desc_text[:800] if desc_text else ""

    # Parse specs from full card text
    full_card_text = card.get_text(separator=" ", strip=True)
    specs = parse_specs_from_text(full_card_text)
    
    # Also try model title for "X Go / Y Go" (RAM / Storage)
    if row["model"]:
        title_spec = re.search(r"(\d+)\s*Go\s*/?\s*(\d+)\s*Go", row["model"])
        if title_spec:
            if not specs.get("ram_gb"):
                specs["ram_gb"] = title_spec.group(1)
            if not specs.get("storage_gb"):
                specs["storage_gb"] = title_spec.group(2)
        # Also: "3/64Go" pattern
        title_spec2 = re.search(r"(\d+)/(\d+)\s*Go", row["model"])
        if title_spec2:
            if not specs.get("ram_gb"):
                specs["ram_gb"] = title_spec2.group(1)
            if not specs.get("storage_gb"):
                specs["storage_gb"] = title_spec2.group(2)

    for k, v in specs.items():
        if k in row and v:
            row[k] = v

    # Brand detection
    brands = ["Samsung", "Apple", "Xiaomi", "Huawei", "OPPO", "Vivo", "Realme", "Honor", 
              "Infinix", "Tecno", "Itel", "Lesia", "TCL", "Nokia", "Motorola", "OnePlus",
              "ZTE", "Alcatel", "Sony", "Google", "Nothing", "Poco", "Redmi"]
    model_lower = row["model"].lower()
    for brand in brands:
        if brand.lower() in model_lower:
            row["brand"] = brand
            break
    
    # Color from title: "- Noir", "- Blanc", etc.
    color_m = re.search(r"[-–]\s*([A-Za-zéèêëàâùûîïô\s]+)\s*$", row["model"])
    if color_m:
        c = color_m.group(1).strip()
        if len(c) <= 25:
            row["color"] = c
    if not row["color"]:
        # Try from reference: YOUNG6-2/16-WHITE -> WHITE
        if row["reference"]:
            ref_color = re.search(r"[-_](BLACK|WHITE|GOLD|SILVER|BLUE|GREEN|RED|PINK|GREY|PURPLE|DBLUE|SBLUE|IBLUE)$", row["reference"], re.I)
            if ref_color:
                color_map = {
                    "BLACK": "Noir", "WHITE": "Blanc", "GOLD": "Gold", "SILVER": "Silver",
                    "BLUE": "Bleu", "GREEN": "Vert", "RED": "Rouge", "PINK": "Rose",
                    "GREY": "Gris", "PURPLE": "Violet", "DBLUE": "Dark Blue", 
                    "SBLUE": "Sky Blue", "IBLUE": "Iris Blue"
                }
                row["color"] = color_map.get(ref_color.group(1).upper(), ref_color.group(1))

    # Warranty
    warranty_m = re.search(r"Garantie\s*:?\s*(\d+)\s*an", desc_text, re.I)
    if warranty_m:
        row["warranty"] = f"{warranty_m.group(1)} an"

    # Stock
    stock_el = card.select_one(".stock.available, .in-stock")
    if stock_el or "En stock" in card.get_text():
        row["in_stock"] = "Oui"
    elif "En arrivage" in card.get_text():
        row["in_stock"] = "En arrivage"
    elif "Rupture" in card.get_text() or "indisponible" in card.get_text().lower() or "Épuisé" in card.get_text():
        row["in_stock"] = "Non"

    # Ensure URL is absolute
    if row["url"] and not row["url"].startswith("http"):
        row["url"] = urljoin(BASE_URL, row["url"])

    return row


def fetch_product_details(driver, url: str) -> dict:
    """Fetch detailed specs from individual product page."""
    specs = {}
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Get full description
        desc_el = soup.select_one(".product.attribute.description, .product-description, #description, .description")
        if desc_el:
            desc_text = desc_el.get_text(separator=" ", strip=True)
            specs["full_description"] = desc_text
            
            # Parse specs from full description
            parsed = parse_specs_from_text(desc_text)
            specs.update(parsed)
        
        # Try to get specs from attribute table
        for row in soup.select(".additional-attributes tr, .product-attributes tr, table.data-table tr"):
            label = row.select_one("th, td:first-child")
            value = row.select_one("td:last-child, td:nth-child(2)")
            if label and value:
                label_text = label.get_text(strip=True).lower()
                value_text = value.get_text(strip=True)
                
                if "batterie" in label_text or "battery" in label_text:
                    match = re.search(r"(\d{4,5})", value_text)
                    if match:
                        specs["battery_mah"] = match.group(1)
                elif "écran" in label_text or "screen" in label_text:
                    match = re.search(r"([\d,\.]+)", value_text)
                    if match:
                        specs["screen_inches"] = match.group(1).replace(",", ".")
                elif "ram" in label_text:
                    match = re.search(r"(\d+)", value_text)
                    if match:
                        specs["ram_gb"] = match.group(1)
                elif "stockage" in label_text or "storage" in label_text:
                    match = re.search(r"(\d+)", value_text)
                    if match:
                        specs["storage_gb"] = match.group(1)
        
    except Exception as e:
        print(f"    Error fetching {url}: {e}")
    
    return specs


def get_total_pages(soup: BeautifulSoup) -> int:
    """Infer total pages from pagination."""
    # Magento pagination: .pages .items li a
    last_page = 1
    for a in soup.select(".pages-items a, .pages .items a, .pagination a, a.page"):
        t = a.get_text(strip=True)
        if t.isdigit():
            last_page = max(last_page, int(t))
    # Also check "page" parameter in links
    for a in soup.select("a[href*='p=']"):
        href = a.get("href", "")
        m = re.search(r"[?&]p=(\d+)", href)
        if m:
            last_page = max(last_page, int(m.group(1)))
    return last_page


def scrape_all_pages(max_pages: Optional[int] = None, fetch_details: bool = True) -> List[Dict]:
    """Scrape category and all pagination; return list of product dicts."""
    all_products = []
    
    print("Initializing Chrome driver...")
    driver = create_driver()
    
    try:
        soup = get_page_with_driver(driver, CATEGORY_URL)
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
                # Magento pagination: ?p=2
                url = f"{CATEGORY_URL}?p={page}"
            
            soup = get_page_with_driver(driver, url, wait_time=3)
            if not soup:
                continue

            cards = list(get_product_cards(soup))
            for card in cards:
                try:
                    prod = extract_product(card)
                    if prod.get("model") or prod.get("price_dt"):
                        all_products.append(prod)
                except Exception as e:
                    print(f"Skip product on page {page}: {e}")

            print(f"  Page {page}/{total_pages} -> {len(cards)} products (total: {len(all_products)})")
            time.sleep(1)
        
        # Fetch details for products with missing specs
        if fetch_details:
            print("\nFetching detailed specs from product pages...")
            missing_count = sum(1 for p in all_products if not p.get("battery_mah"))
            print(f"  {missing_count} products need detailed fetching")
            
            fetched = 0
            for i, prod in enumerate(all_products):
                # Check if we need more data
                needs_data = (
                    not prod.get("battery_mah") or 
                    not prod.get("camera_rear_mp") or
                    not prod.get("screen_inches")
                )
                
                if needs_data and prod.get("url"):
                    details = fetch_product_details(driver, prod["url"])
                    
                    # Update missing fields
                    for key, value in details.items():
                        if key in prod and (not prod[key] or prod[key] == ""):
                            prod[key] = value
                    
                    # Update description if we got a fuller one
                    if details.get("full_description") and len(details["full_description"]) > len(prod.get("description", "")):
                        prod["description"] = details["full_description"][:1000]
                    
                    fetched += 1
                    if fetched % 20 == 0:
                        print(f"    Fetched {fetched} product details...")
                    
                    time.sleep(0.5)
            
            print(f"  Fetched details for {fetched} products")
    
    finally:
        driver.quit()

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


def save_csv(products: List[Dict], path: str = "mytek_smartphones.csv") -> None:
    """Write products to CSV with all keys as columns."""
    products = deduplicate_by_url(products)
    if not products:
        print("No products to save.")
        return
    fieldnames = [
        "model", "brand", "reference", "price_dt", "old_price_dt", "ram_gb", "storage_gb",
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
    fetch_details = False  # Disabled by default for faster scraping
    
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            max_pages = int(sys.argv[1])
            print(f"Limiting to first {max_pages} page(s).")
        elif sys.argv[1] == "--details":
            fetch_details = True
            print("Will fetch detailed product pages.")
    
    print("=" * 50)
    print("Mytek.tn smartphone scraper")
    print("=" * 50)
    print("URL:", CATEGORY_URL)
    
    try:
        products = scrape_all_pages(max_pages=max_pages, fetch_details=fetch_details)
        
        if products:
            save_csv(products, path="mytek_smartphones.csv")
            print(f"\nSuccess! Saved {len(products)} products to mytek_smartphones.csv")
        else:
            print("\nERROR: No products were scraped!")
    except Exception as e:
        print(f"\nERROR: Scraping failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("Done.")


if __name__ == "__main__":
    main()
