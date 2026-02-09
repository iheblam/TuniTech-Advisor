#!/usr/bin/env python3
"""
Enhanced script to fill missing specs in BestPhone data using all available sources.
Uses improved fuzzy matching to find more matches.
"""

import pandas as pd
import re
from pathlib import Path
from difflib import SequenceMatcher


def normalize_model(name):
    """Normalize model name for matching - extract core model identifier."""
    if pd.isna(name):
        return ""
    
    name = str(name).lower().strip()
    
    # Remove common prefixes
    name = re.sub(r'^smartphone\s+', '', name)
    
    # Remove colors
    colors = [
        'noir', 'blanc', 'bleu', 'vert', 'rose', 'gold', 'silver', 'gris', 
        'violet', 'rouge', 'orange', 'cyan', 'black', 'white', 'green', 'blue',
        'pink', 'grey', 'gray', 'purple', 'lavender', 'lime', 'light', 'natural',
        'navy', 'teal', 'ultramarine', 'glacier', 'titanium', 'midnight',
        'starlight', 'graphite', 'deep', 'ice', 'dark', 'menthe'
    ]
    for color in colors:
        name = re.sub(rf'\b{color}\b', '', name)
    
    # Remove storage/RAM patterns
    name = re.sub(r'\d+\s*(?:gb|go)\s*/?\s*\d*\s*(?:gb|go)?', '', name, flags=re.I)
    name = re.sub(r'\d+/\d+', '', name)
    
    # Remove network indicators
    name = re.sub(r'\b[45]g\b', '', name, flags=re.I)
    
    # Remove special chars, normalize spaces
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def extract_model_key(name):
    """Extract key model identifier like 'samsung galaxy a55' or 'iphone 16'."""
    normalized = normalize_model(name)
    
    # For iPhones, extract "iphone XX" pattern
    iphone_match = re.search(r'iphone\s*(\d+)(?:\s*(?:pro|plus|max|mini))*', normalized)
    if iphone_match:
        return f"iphone {iphone_match.group(1)}" + (' pro' if 'pro' in normalized else '') + (' max' if 'max' in normalized else '') + (' plus' if 'plus' in normalized else '') + (' mini' if 'mini' in normalized else '')
    
    # For Samsung Galaxy
    galaxy_match = re.search(r'(samsung\s*)?galaxy\s*([as]\d+)(?:\s*(?:fe|ultra|plus|\+))*', normalized)
    if galaxy_match:
        model = f"samsung galaxy {galaxy_match.group(2)}"
        if 'ultra' in normalized:
            model += ' ultra'
        if 'fe' in normalized:
            model += ' fe'
        if 'plus' in normalized or '+' in name.lower():
            model += ' plus'
        return model
    
    # For Redmi/Xiaomi
    redmi_match = re.search(r'(xiaomi\s*)?(redmi\s*)?note?\s*(\d+)(?:\s*(?:pro|plus))*', normalized)
    if redmi_match and redmi_match.group(3):
        model = f"redmi note {redmi_match.group(3)}"
        if 'pro' in normalized:
            model += ' pro'
        return model
    
    # For Honor
    honor_match = re.search(r'honor\s*(x?\d+\w*)', normalized)
    if honor_match:
        return f"honor {honor_match.group(1)}"
    
    # For Infinix
    infinix_match = re.search(r'infinix\s*(\w+\s*\d+\w*)', normalized)
    if infinix_match:
        return f"infinix {infinix_match.group(1)}"
    
    return normalized


def build_comprehensive_spec_db(dataframes):
    """Build a comprehensive spec database from multiple dataframes."""
    spec_db = {}
    
    for df_name, df in dataframes:
        # Find name column
        name_col = 'model' if 'model' in df.columns else 'name'
        if name_col not in df.columns:
            continue
        
        for _, row in df.iterrows():
            name = row.get(name_col, '')
            if pd.isna(name) or not str(name).strip():
                continue
            
            model_key = extract_model_key(name)
            if not model_key or len(model_key) < 5:
                continue
            
            # Collect specs
            specs = {}
            for col in ['battery_mah', 'screen_inches', 'camera_rear_mp', 'camera_front_mp', 
                       'network', 'os', 'processor_type']:
                val = row.get(col)
                if pd.notna(val) and str(val).strip():
                    specs[col] = str(val).strip()
            
            if not specs:
                continue
            
            # Update db - prefer more complete entries
            if model_key not in spec_db or len(specs) > len(spec_db[model_key]):
                spec_db[model_key] = specs
    
    return spec_db


def find_matching_specs(name, spec_db):
    """Find matching specs using multiple strategies."""
    model_key = extract_model_key(name)
    
    if not model_key:
        return None
    
    # Exact match
    if model_key in spec_db:
        return spec_db[model_key]
    
    # Fuzzy match
    best_match = None
    best_score = 0
    
    for db_key, specs in spec_db.items():
        # Use sequence matcher for similarity
        score = SequenceMatcher(None, model_key, db_key).ratio()
        
        # Also check word overlap
        key_words = set(model_key.split())
        db_words = set(db_key.split())
        if key_words and db_words:
            word_overlap = len(key_words & db_words) / max(len(key_words), len(db_words))
            score = max(score, word_overlap)
        
        if score > 0.75 and score > best_score:
            best_score = score
            best_match = specs
    
    return best_match


def main():
    base_path = Path("c:/Users/ihebl/Downloads/projet python sem 2/projet python sem 2/dataset")
    
    print("=" * 60)
    print("Enhanced BestPhone Spec Filler")
    print("=" * 60)
    
    # Load all datasets
    print("\nLoading all datasets...")
    datasets = []
    
    for name, filename in [
        ("Tunisianet", "tunisianet_smartphones_filled.csv"),
        ("Mytek", "mytek_smartphones_filled.csv"),
        ("SpaceNet", "spacenet_smartphones_filled.csv"),
    ]:
        path = base_path / filename
        if path.exists():
            df = pd.read_csv(path)
            datasets.append((name, df))
            print(f"  {name}: {len(df)} rows")
    
    # Load BestPhone
    bestphone_path = base_path / "bestphone_smartphones_filled.csv"
    bestphone = pd.read_csv(bestphone_path)
    print(f"  BestPhone: {len(bestphone)} rows")
    
    # Build comprehensive spec database
    print("\nBuilding spec database...")
    spec_db = build_comprehensive_spec_db(datasets)
    print(f"  Found {len(spec_db)} unique model patterns")
    
    # Show sample keys
    print("\nSample model patterns in database:")
    for key in list(spec_db.keys())[:10]:
        print(f"  - {key}")
    
    # Ensure columns exist and convert to object type for flexibility
    spec_cols = ['battery_mah', 'screen_inches', 'camera_rear_mp', 'camera_front_mp',
                 'network', 'os', 'processor_type']
    for col in spec_cols:
        if col not in bestphone.columns:
            bestphone[col] = ""
        # Convert to string type to avoid dtype issues
        bestphone[col] = bestphone[col].astype(str).replace('nan', '').replace('None', '')
    
    # Fill missing specs
    print("\nFilling missing specs...")
    filled_count = 0
    match_count = 0
    
    for idx, row in bestphone.iterrows():
        name = row.get('name', '')
        if pd.isna(name) or not str(name).strip():
            continue
        
        # Find specs
        specs = find_matching_specs(name, spec_db)
        
        if specs:
            match_count += 1
            for col in spec_cols:
                current = row.get(col)
                new_val = specs.get(col)
                
                if (pd.isna(current) or str(current).strip() == '') and new_val:
                    bestphone.at[idx, col] = new_val
                    filled_count += 1
    
    print(f"\n  Matched {match_count} products")
    print(f"  Filled {filled_count} values")
    
    # Save
    output_path = base_path / "bestphone_smartphones_filled.csv"
    bestphone.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nSaved to {output_path}")
    
    # Final coverage
    print("\nFinal coverage:")
    for col in spec_cols:
        filled = bestphone[col].notna() & (bestphone[col].astype(str).str.strip() != '')
        pct = filled.sum() / len(bestphone) * 100
        print(f"  {col}: {filled.sum()}/{len(bestphone)} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
