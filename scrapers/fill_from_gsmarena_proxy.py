#!/usr/bin/env python3
"""
Fill missing smartphone specs from GSMArena using rotating proxies.
This script handles rate limiting by rotating through free proxy servers.

Authors: Iheb Lamouchi & Yassine Nemri
Date: February 2026
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from pathlib import Path

# Free proxy list - we'll fetch fresh ones
PROXY_SOURCES = [
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
]

# User agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def fetch_proxies():
    """Fetch fresh proxy list from multiple sources."""
    proxies = []
    for source in PROXY_SOURCES:
        try:
            resp = requests.get(source, timeout=10)
            if resp.status_code == 200:
                lines = resp.text.strip().split('\n')
                for line in lines[:100]:  # Limit per source
                    line = line.strip()
                    if ':' in line and line[0].isdigit():
                        proxies.append(line)
        except Exception as e:
            print(f"  Warning: Could not fetch from {source[:50]}...")
    
    # Remove duplicates
    proxies = list(set(proxies))
    random.shuffle(proxies)
    print(f"  Fetched {len(proxies)} proxies")
    return proxies

def test_proxy(proxy, timeout=5):
    """Test if a proxy is working."""
    try:
        resp = requests.get(
            'https://www.gsmarena.com/',
            proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
            timeout=timeout,
            headers={'User-Agent': random.choice(USER_AGENTS)}
        )
        return resp.status_code == 200
    except:
        return False

def get_working_proxies(proxy_list, max_test=50):
    """Get a list of working proxies."""
    working = []
    tested = 0
    for proxy in proxy_list:
        if tested >= max_test:
            break
        if test_proxy(proxy):
            working.append(proxy)
            print(f"    ✓ Working proxy: {proxy}")
            if len(working) >= 10:  # We only need 10 good ones
                break
        tested += 1
    return working

def search_gsmarena(phone_name, proxy=None, max_retries=3):
    """Search GSMArena for a phone and get its specs page URL."""
    search_query = re.sub(r'[^\w\s]', '', phone_name.lower())
    search_query = re.sub(r'\s+', '+', search_query.strip())
    
    url = f'https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName={search_query}'
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.gsmarena.com/',
    }
    
    proxies_dict = None
    if proxy:
        proxies_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, proxies=proxies_dict, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Find first result
                results = soup.select('.makers ul li a')
                if results:
                    return 'https://www.gsmarena.com/' + results[0]['href']
            
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))
    
    return None

def get_phone_specs(url, proxy=None, max_retries=3):
    """Get phone specifications from GSMArena specs page."""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    proxies_dict = None
    if proxy:
        proxies_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
    
    specs = {}
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, proxies=proxies_dict, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Find all spec tables
                spec_tables = soup.select('table[cellspacing="0"]')
                
                for table in spec_tables:
                    rows = table.select('tr')
                    for row in rows:
                        header = row.select_one('.ttl')
                        value = row.select_one('.nfo')
                        if header and value:
                            key = header.get_text(strip=True).lower()
                            val = value.get_text(strip=True)
                            
                            # Extract specific specs
                            if 'battery' in key or key == 'capacity':
                                match = re.search(r'(\d{3,5})\s*mah', val.lower())
                                if match:
                                    specs['battery_mah'] = int(match.group(1))
                            
                            if 'size' in key and 'screen' not in specs:
                                match = re.search(r'(\d+\.?\d*)\s*inches', val.lower())
                                if match:
                                    specs['screen_inches'] = float(match.group(1))
                            
                            if 'main camera' in key or 'single' in key or 'dual' in key or 'triple' in key or 'quad' in key:
                                match = re.search(r'(\d+)\s*mp', val.lower())
                                if match and 'camera_rear_mp' not in specs:
                                    specs['camera_rear_mp'] = int(match.group(1))
                            
                            if 'selfie' in key or 'front' in key:
                                match = re.search(r'(\d+)\s*mp', val.lower())
                                if match:
                                    specs['camera_front_mp'] = int(match.group(1))
                            
                            if 'technology' in key or 'network' in key:
                                if '5g' in val.lower():
                                    specs['network'] = '5G'
                                elif '4g' in val.lower() or 'lte' in val.lower():
                                    specs['network'] = '4G'
                                elif '3g' in val.lower():
                                    specs['network'] = '3G'
                            
                            if 'os' in key:
                                if 'android' in val.lower():
                                    match = re.search(r'android\s*(\d+)', val.lower())
                                    if match:
                                        specs['os'] = f'Android {match.group(1)}'
                                    else:
                                        specs['os'] = 'Android'
                                elif 'ios' in val.lower():
                                    specs['os'] = 'iOS'
                            
                            if 'chipset' in key or 'cpu' in key:
                                if 'snapdragon' in val.lower():
                                    match = re.search(r'snapdragon\s*(\d+)', val.lower())
                                    if match:
                                        specs['processor_type'] = f'Snapdragon {match.group(1)}'
                                elif 'exynos' in val.lower():
                                    specs['processor_type'] = 'Exynos'
                                elif 'dimensity' in val.lower():
                                    match = re.search(r'dimensity\s*(\d+)', val.lower())
                                    if match:
                                        specs['processor_type'] = f'Dimensity {match.group(1)}'
                                elif 'helio' in val.lower():
                                    match = re.search(r'helio\s*(\w+)', val.lower())
                                    if match:
                                        specs['processor_type'] = f'Helio {match.group(1).upper()}'
                                elif 'a1' in val.lower() or 'bionic' in val.lower():
                                    match = re.search(r'a(\d+)', val.lower())
                                    if match:
                                        specs['processor_type'] = f'A{match.group(1)} Bionic'
                
                return specs
            
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))
    
    return specs

def extract_model_for_search(name, brand):
    """Extract clean model name for GSMArena search."""
    name_lower = name.lower() if name else ''
    brand_lower = brand.lower() if brand else ''
    
    # Remove color and storage info
    clean = re.sub(r'\d+\s*(go|gb|to|tb)', '', name_lower, flags=re.IGNORECASE)
    clean = re.sub(r'(noir|blanc|bleu|vert|rouge|gris|silver|gold|black|white|blue|green|red|gray|grey|purple|violet|jaune|yellow|orange|rose|pink)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'[+-]$', '', clean.strip())
    
    # Add brand if not present
    if brand_lower and brand_lower not in clean:
        clean = f"{brand} {clean}"
    
    return clean.strip()

def main():
    print("=" * 70)
    print("GSMARENA SPEC FILLER WITH PROXY ROTATION")
    print("=" * 70)
    
    # Load unified dataset
    data_path = Path("dataset")
    df = pd.read_csv(data_path / "unified_smartphones.csv")
    print(f"\n📊 Loaded {len(df)} products")
    
    # Find rows with missing specs
    missing_mask = (
        df['screen_inches'].isna() | 
        df['camera_rear_mp'].isna() | 
        df['camera_front_mp'].isna() |
        df['battery_mah'].isna() |
        df['os'].isna()
    )
    rows_to_fill = df[missing_mask].copy()
    print(f"🔍 Found {len(rows_to_fill)} rows with missing specs")
    
    # Fetch and test proxies
    print("\n📡 Fetching proxy list...")
    all_proxies = fetch_proxies()
    
    if not all_proxies:
        print("⚠️ No proxies found, will try direct connection")
        working_proxies = [None]
    else:
        print("\n🔧 Testing proxies...")
        working_proxies = get_working_proxies(all_proxies)
        if not working_proxies:
            print("⚠️ No working proxies, will try direct connection")
            working_proxies = [None]
    
    print(f"\n✓ Using {len(working_proxies)} proxy sources")
    
    # Process each row
    filled_count = 0
    total_specs_filled = 0
    proxy_index = 0
    
    # Limit to avoid too many requests
    max_to_process = min(100, len(rows_to_fill))
    
    print(f"\n🔄 Processing up to {max_to_process} phones...")
    print("-" * 70)
    
    for idx, (row_idx, row) in enumerate(rows_to_fill.head(max_to_process).iterrows()):
        # Rotate proxy
        proxy = working_proxies[proxy_index % len(working_proxies)]
        proxy_index += 1
        
        name = row.get('name', '')
        brand = row.get('brand', '')
        
        if not name:
            continue
        
        search_name = extract_model_for_search(name, brand)
        print(f"\n[{idx+1}/{max_to_process}] Searching: {search_name[:50]}...")
        
        # Search GSMArena
        specs_url = search_gsmarena(search_name, proxy)
        
        if specs_url:
            print(f"  Found: {specs_url[:60]}...")
            
            # Get specs
            specs = get_phone_specs(specs_url, proxy)
            
            if specs:
                specs_added = 0
                for spec_key, spec_val in specs.items():
                    if pd.isna(df.at[row_idx, spec_key]) or str(df.at[row_idx, spec_key]).strip() == '':
                        df.at[row_idx, spec_key] = spec_val
                        specs_added += 1
                
                if specs_added > 0:
                    filled_count += 1
                    total_specs_filled += specs_added
                    print(f"  ✓ Filled {specs_added} specs: {list(specs.keys())}")
                else:
                    print(f"  - No new specs needed")
            else:
                print(f"  ✗ Could not parse specs")
        else:
            print(f"  ✗ Not found on GSMArena")
        
        # Random delay to avoid rate limiting
        time.sleep(random.uniform(2, 5))
        
        # Switch proxy periodically
        if idx % 10 == 9 and len(working_proxies) > 1:
            print("\n  🔄 Rotating to next proxy...")
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"  Products processed: {max_to_process}")
    print(f"  Products updated: {filled_count}")
    print(f"  Total specs filled: {total_specs_filled}")
    
    # Save updated dataset
    output_file = data_path / "unified_smartphones_enriched.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 Saved to {output_file}")
    
    # Show new coverage
    print("\n📊 Updated Coverage:")
    for col in ['battery_mah', 'screen_inches', 'camera_rear_mp', 'camera_front_mp', 'network', 'os', 'processor_type']:
        valid = df[col].notna() & (df[col].astype(str).str.strip() != '')
        pct = valid.sum() / len(df) * 100
        print(f"  {col}: {pct:.1f}%")

if __name__ == "__main__":
    main()
