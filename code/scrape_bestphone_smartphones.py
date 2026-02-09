"""
Scraper for BestPhone.tn smartphone categories.
Extracts: model, brand, RAM, storage, price, color, etc.
Output: CSV dataset (bestphone_smartphones.csv)
"""

import re
import csv
import time
import requests
from urllib.parse import urljoin
from typing import List, Dict, Optional

from bs4 import BeautifulSoup

BASE_URL = "https://bestphone.tn"
# Categories to scrape: smartphones and iPhones
CATEGORIES = [
    ("smartphone", f"{BASE_URL}/product-category/smartphone/"),
    ("iphone", f"{BASE_URL}/product-category/apple-store/iphone/"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

# Columns for CSV output
CSV_COLUMNS = [
    "name", "brand", "price_tnd", "original_price_tnd", "discount_percent",
    "ram_gb", "storage_gb", "color", "network", "availability",
    "product_url", "image_url", "category", "source"
]


def get_soup(url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
    """Fetch URL and return BeautifulSoup object."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as e:
            print(f"  Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None


def parse_price(price_text: str) -> Optional[float]:
    """
    Parse price from text like '549,000 DT' or '1.299,000 DT' -> 549.0 or 1299.0
    BestPhone format: uses comma for decimals, dot for thousands
    '549,000 DT' means 549 DT (the ,000 is decimal part)
    '1.299,000 DT' means 1299 DT
    """
    if not price_text:
        return None
    # Remove DT and whitespace
    price_text = price_text.replace("DT", "").strip()
    # Remove dots (thousand separators)
    price_text = price_text.replace(".", "")
    # Replace comma with dot for decimal
    price_text = price_text.replace(",", ".")
    try:
        # The format gives us values like 549000 for 549 DT, so divide by 1000
        value = float(price_text)
        # Prices are stored with ,000 suffix meaning they're in millimes
        # 549,000 = 549 dinars, so we need to handle this
        if value >= 1000:
            value = value / 1000
        return round(value, 2)
    except ValueError:
        return None


def extract_specs_from_title(title: str) -> dict:
    """
    Extract RAM, storage, color, network from product title.
    Examples:
    - 'Samsung Galaxy A16 6GB 128GB Noir' -> ram=6, storage=128, color=Noir
    - 'iPhone 16 128GB – Black' -> storage=128, color=Black
    - 'SAMSUNG GALAXY A56 5G 8GB 128GB Noir' -> ram=8, storage=128, network=5G, color=Noir
    - 'Redmi Note 14 Pro 8GB 256GB' -> ram=8, storage=256
    """
    specs = {}
    
    # Clean title - remove network indicators for RAM/storage parsing
    title_clean = title.strip()
    title_for_specs = re.sub(r'\b[45]G\b', '', title_clean)  # Remove 4G/5G
    
    # ---- Network (4G/5G) ----
    if "5G" in title.upper():
        specs["network"] = "5G"
    elif "4G" in title.upper():
        specs["network"] = "4G"
    
    # ---- RAM and Storage ----
    # Pattern: 6GB 128GB or 8Go 128Go (RAM before storage, RAM is usually smaller)
    # Match two consecutive memory values
    ram_storage_match = re.search(r"(\d{1,2})\s*(?:GB|Go)\s+(\d{2,4})\s*(?:GB|Go)", title_for_specs, re.I)
    if ram_storage_match:
        ram_val = int(ram_storage_match.group(1))
        storage_val = int(ram_storage_match.group(2))
        # RAM is typically 4-16GB, storage is 32-1024GB
        if ram_val <= 16 and storage_val >= 32:
            specs["ram_gb"] = str(ram_val)
            specs["storage_gb"] = str(storage_val)
    
    # If no RAM+storage found, try single storage value (common for iPhones)
    if "storage_gb" not in specs:
        storage_match = re.search(r"(\d{2,4})\s*(?:GB|Go)", title_for_specs, re.I)
        if storage_match:
            specs["storage_gb"] = storage_match.group(1)
    
    # ---- Color ----
    # Common colors in French and English
    colors = [
        "Noir", "Blanc", "Bleu", "Vert", "Rose", "Rouge", "Gris", "Or", "Gold",
        "Silver", "Black", "White", "Blue", "Green", "Pink", "Red", "Gray", "Grey",
        "Purple", "Violet", "Yellow", "Jaune", "Orange", "Lavender", "Lime",
        "Titanium", "Natural", "Navy", "Teal", "Ultramarine", "Light Green",
        "Glacier", "Midnight", "Starlight"
    ]
    title_lower = title.lower()
    for color in colors:
        if color.lower() in title_lower:
            specs["color"] = color
            break
    
    return specs


def extract_brand(title: str, brand_element=None) -> str:
    """Extract brand from title or brand element."""
    # Try brand element first
    if brand_element:
        brand_text = brand_element.get_text(strip=True).upper()
        if brand_text:
            return brand_text.title()
    
    # Extract from title
    title_upper = title.upper()
    brands = [
        ("SAMSUNG", "Samsung"),
        ("APPLE", "Apple"),
        ("IPHONE", "Apple"),
        ("XIAOMI", "Xiaomi"),
        ("REDMI", "Xiaomi"),
        ("HONOR", "Honor"),
        ("INFINIX", "Infinix"),
        ("OPPO", "Oppo"),
        ("HUAWEI", "Huawei"),
        ("REALME", "Realme"),
        ("VIVO", "Vivo"),
        ("TECNO", "Tecno"),
        ("MOTOROLA", "Motorola"),
        ("NOKIA", "Nokia"),
        ("ONEPLUS", "OnePlus"),
        ("GOOGLE", "Google"),
        ("POCO", "Poco"),
    ]
    
    for keyword, brand_name in brands:
        if keyword in title_upper:
            return brand_name
    
    return ""


def scrape_category_page(soup: BeautifulSoup, category: str) -> List[Dict]:
    """Extract product info from a category listing page."""
    products = []
    
    # Find product containers
    product_items = soup.select("li.product, div.product-wrapper, article.product")
    
    if not product_items:
        # Alternative selectors for WooCommerce
        product_items = soup.select(".products .product")
    
    for item in product_items:
        try:
            product = {"category": category, "source": "BestPhone.tn"}
            
            # Product name
            name_el = item.select_one("h2.product-title a, .woocommerce-loop-product__title, h3 a, .product-title a")
            if not name_el:
                name_el = item.select_one("a.woocommerce-LoopProduct-link")
            
            if name_el:
                product["name"] = name_el.get_text(strip=True)
                product["product_url"] = name_el.get("href", "")
            else:
                continue  # Skip if no name found
            
            # Brand
            brand_el = item.select_one("a[href*='/brand/'], .product-brand")
            product["brand"] = extract_brand(product.get("name", ""), brand_el)
            
            # Price - current price
            price_el = item.select_one("ins .woocommerce-Price-amount, .price ins .amount, span.price ins")
            if not price_el:
                price_el = item.select_one(".woocommerce-Price-amount, .price .amount, span.price")
            
            if price_el:
                price_text = price_el.get_text(strip=True)
                product["price_tnd"] = parse_price(price_text)
            
            # Original price (if on sale)
            orig_price_el = item.select_one("del .woocommerce-Price-amount, .price del .amount")
            if orig_price_el:
                orig_text = orig_price_el.get_text(strip=True)
                product["original_price_tnd"] = parse_price(orig_text)
                
                # Calculate discount
                if product.get("price_tnd") and product.get("original_price_tnd"):
                    discount = (1 - product["price_tnd"] / product["original_price_tnd"]) * 100
                    product["discount_percent"] = round(discount, 1)
            
            # Image
            img_el = item.select_one("img.attachment-woocommerce_thumbnail, img.wp-post-image, .product-thumbnail img")
            if img_el:
                product["image_url"] = img_el.get("src") or img_el.get("data-src", "")
            
            # Availability
            if item.select_one(".out-of-stock, .outofstock"):
                product["availability"] = "Out of Stock"
            else:
                product["availability"] = "In Stock"
            
            # Extract specs from title
            if product.get("name"):
                specs = extract_specs_from_title(product["name"])
                product.update(specs)
            
            products.append(product)
            
        except Exception as e:
            print(f"  Error parsing product: {e}")
            continue
    
    return products


def get_total_pages(soup: BeautifulSoup) -> int:
    """Get total number of pages in category."""
    # Look for pagination
    pagination = soup.select("a.page-numbers, ul.page-numbers a, nav.woocommerce-pagination a")
    
    max_page = 1
    for link in pagination:
        href = link.get("href", "")
        text = link.get_text(strip=True)
        
        # Try to get page number from text
        if text.isdigit():
            max_page = max(max_page, int(text))
        
        # Try to get from URL
        page_match = re.search(r"/page/(\d+)", href)
        if page_match:
            max_page = max(max_page, int(page_match.group(1)))
    
    return max_page


def scrape_category(category_name: str, category_url: str) -> List[Dict]:
    """Scrape all pages of a category."""
    all_products = []
    
    print(f"\nScraping category: {category_name}")
    print(f"URL: {category_url}")
    
    # Get first page
    soup = get_soup(category_url)
    if not soup:
        print(f"  Failed to fetch category page")
        return []
    
    # Get total pages
    total_pages = get_total_pages(soup)
    print(f"  Found {total_pages} pages")
    
    # Scrape first page
    products = scrape_category_page(soup, category_name)
    all_products.extend(products)
    print(f"  Page 1: {len(products)} products")
    
    # Scrape remaining pages
    for page in range(2, total_pages + 1):
        page_url = f"{category_url}page/{page}/"
        time.sleep(1)  # Be polite
        
        soup = get_soup(page_url)
        if not soup:
            print(f"  Page {page}: Failed to fetch")
            continue
        
        products = scrape_category_page(soup, category_name)
        all_products.extend(products)
        print(f"  Page {page}: {len(products)} products")
    
    return all_products


def save_to_csv(products: List[Dict], filename: str):
    """Save products to CSV file."""
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        
        for product in products:
            row = {col: product.get(col, "") for col in CSV_COLUMNS}
            writer.writerow(row)
    
    print(f"\nSaved {len(products)} products to {filename}")


def main():
    """Main scraping function."""
    print("=" * 60)
    print("BestPhone.tn Smartphone Scraper")
    print("=" * 60)
    
    all_products = []
    
    for category_name, category_url in CATEGORIES:
        products = scrape_category(category_name, category_url)
        all_products.extend(products)
        time.sleep(2)  # Delay between categories
    
    # Remove duplicates based on product URL
    seen_urls = set()
    unique_products = []
    for p in all_products:
        url = p.get("product_url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_products.append(p)
        elif not url:
            unique_products.append(p)
    
    print(f"\n{'=' * 60}")
    print(f"Total products scraped: {len(all_products)}")
    print(f"Unique products: {len(unique_products)}")
    
    # Summary by brand
    brands = {}
    for p in unique_products:
        brand = p.get("brand", "Unknown")
        brands[brand] = brands.get(brand, 0) + 1
    
    print("\nProducts by brand:")
    for brand, count in sorted(brands.items(), key=lambda x: -x[1]):
        print(f"  {brand}: {count}")
    
    # Save to CSV
    output_file = "dataset/bestphone_smartphones.csv"
    save_to_csv(unique_products, output_file)
    
    print(f"\nDone! Data saved to {output_file}")


if __name__ == "__main__":
    main()
