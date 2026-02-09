#!/usr/bin/env python3
"""
Fill missing specs in SpaceNet data using existing data from Tunisianet and Mytek.
This avoids rate-limiting issues with GSMArena by using specs we already have.
"""

import pandas as pd
import re
import sys
from pathlib import Path

def normalize_model_name(model_name):
    """Normalize model name for matching."""
    if pd.isna(model_name):
        return ""
    
    # Convert to lowercase
    name = str(model_name).lower()
    
    # Remove "smartphone" prefix
    name = re.sub(r'^smartphone\s+', '', name)
    
    # Remove color suffixes (common colors in French and English)
    colors = [
        'noir', 'blanc', 'bleu', 'vert', 'rose', 'gold', 'silver', 'gris', 
        'violet', 'rouge', 'orange', 'cyan', 'marron', 'dark', 'foncé',
        'black', 'white', 'green', 'blue', 'pink', 'grey', 'gray', 'purple',
        'menthe', 'midnight', 'titanium', 'marine', 'stellaire', 'satiné',
        'twilight'
    ]
    for color in colors:
        name = re.sub(rf'\b{color}\b', '', name)
    
    # Remove RAM/Storage specifications (e.g., "8Go 256Go", "8/256")
    name = re.sub(r'\d+\s*go\s*[\+\/]?\s*\d*\s*go', '', name)
    name = re.sub(r'\d+\s*go', '', name)
    name = re.sub(r'\d+\s*/\s*\d+', '', name)
    
    # Remove special characters and normalize spaces
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def extract_base_model(model_name):
    """Extract base model identifier for matching (brand + model series)."""
    normalized = normalize_model_name(model_name)
    
    # Common patterns: "Brand Model Number"
    # E.g., "Samsung Galaxy A55" -> "samsung galaxy a55"
    # E.g., "Xiaomi Redmi Note 14" -> "xiaomi redmi note 14"
    
    return normalized

def build_spec_database(df, source_name):
    """Build a database of specs from a dataframe."""
    spec_db = {}
    
    for idx, row in df.iterrows():
        base_model = extract_base_model(row.get('model', ''))
        if not base_model:
            continue
        
        specs = {
            'battery_mah': row.get('battery_mah'),
            'screen_inches': row.get('screen_inches'),
            'camera_rear_mp': row.get('camera_rear_mp'),
            'camera_front_mp': row.get('camera_front_mp'),
            'network': row.get('network'),
            'os': row.get('os'),
            'processor_type': row.get('processor_type'),
            'source': source_name
        }
        
        # Only add if at least one spec is valid
        valid_specs = {k: v for k, v in specs.items() if pd.notna(v) and str(v).strip() and k != 'source'}
        if valid_specs:
            if base_model not in spec_db:
                spec_db[base_model] = specs
            else:
                # Update with more complete data if available
                existing_count = sum(1 for k, v in spec_db[base_model].items() 
                                    if k != 'source' and pd.notna(v) and str(v).strip())
                new_count = sum(1 for k, v in valid_specs.items() if pd.notna(v))
                if new_count > existing_count:
                    spec_db[base_model] = specs
    
    return spec_db

def find_best_match(model_name, spec_db):
    """Find the best matching specs for a model."""
    base_model = extract_base_model(model_name)
    
    if not base_model:
        return None
    
    # Exact match
    if base_model in spec_db:
        return spec_db[base_model]
    
    # Try partial matches
    base_words = set(base_model.split())
    best_match = None
    best_score = 0
    
    for db_model, specs in spec_db.items():
        db_words = set(db_model.split())
        
        # Calculate Jaccard similarity
        intersection = len(base_words & db_words)
        union = len(base_words | db_words)
        
        if union > 0:
            score = intersection / union
            
            # Require at least 70% match
            if score > 0.7 and score > best_score:
                best_score = score
                best_match = specs
    
    return best_match

def main():
    # Paths
    base_path = Path("c:/Users/ihebl/Downloads/projet python sem 2/projet python sem 2/dataset")
    
    spacenet_path = base_path / "spacenet_smartphones.csv"
    tunisianet_path = base_path / "tunisianet_smartphones_filled.csv"
    mytek_path = base_path / "mytek_smartphones_filled.csv"
    output_path = base_path / "spacenet_smartphones_filled.csv"
    
    # Load datasets
    print("Loading datasets...")
    spacenet_df = pd.read_csv(spacenet_path)
    print(f"  SpaceNet: {len(spacenet_df)} rows")
    
    tunisianet_df = pd.read_csv(tunisianet_path)
    print(f"  Tunisianet: {len(tunisianet_df)} rows")
    
    mytek_df = pd.read_csv(mytek_path)
    print(f"  Mytek: {len(mytek_df)} rows")
    
    # Build spec database from existing data
    print("\nBuilding spec database from existing data...")
    spec_db = {}
    
    # Add Tunisianet specs
    tunisianet_specs = build_spec_database(tunisianet_df, 'tunisianet')
    spec_db.update(tunisianet_specs)
    print(f"  Tunisianet: {len(tunisianet_specs)} unique models")
    
    # Add Mytek specs (may override some)
    mytek_specs = build_spec_database(mytek_df, 'mytek')
    for key, value in mytek_specs.items():
        if key not in spec_db:
            spec_db[key] = value
    print(f"  Mytek: {len(mytek_specs)} unique models")
    print(f"  Total unique models in database: {len(spec_db)}")
    
    # Fill missing specs in SpaceNet
    print("\nFilling missing specs in SpaceNet data...")
    
    fill_count = 0
    match_count = 0
    
    spec_columns = ['battery_mah', 'screen_inches', 'camera_rear_mp', 
                   'camera_front_mp', 'network', 'os', 'processor_type']
    
    for idx, row in spacenet_df.iterrows():
        # Check if this row has missing specs
        has_missing = any(pd.isna(row.get(col)) or str(row.get(col, '')).strip() == '' 
                         for col in spec_columns)
        
        if not has_missing:
            continue
        
        # Find matching specs
        specs = find_best_match(row['model'], spec_db)
        
        if specs:
            match_count += 1
            
            # Fill each missing spec
            for col in spec_columns:
                current_val = row.get(col)
                if pd.isna(current_val) or str(current_val).strip() == '':
                    new_val = specs.get(col)
                    if pd.notna(new_val) and str(new_val).strip():
                        spacenet_df.at[idx, col] = new_val
                        fill_count += 1
    
    print(f"  Found matches for {match_count} models")
    print(f"  Filled {fill_count} missing values")
    
    # Save results
    spacenet_df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")
    
    # Summary statistics
    print("\n=== Summary ===")
    for col in spec_columns:
        non_null = spacenet_df[col].notna().sum()
        pct = (non_null / len(spacenet_df)) * 100
        print(f"  {col}: {non_null}/{len(spacenet_df)} ({pct:.1f}%)")

if __name__ == "__main__":
    main()
