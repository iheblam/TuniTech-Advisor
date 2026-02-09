#!/usr/bin/env python3
"""
Fill missing specs in BestPhone data using existing data from Tunisianet, Mytek, and SpaceNet.
This script matches products by model name and fills in missing specifications.
"""

import pandas as pd
import re
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
        'twilight', 'lavender', 'lime', 'light', 'natural', 'navy', 'teal',
        'ultramarine', 'glacier', 'starlight', 'graphite', 'deep', 'ice',
        'esim', 'dual', 'sim'
    ]
    for color in colors:
        name = re.sub(rf'\b{color}\b', '', name)
    
    # Remove RAM/Storage specifications
    name = re.sub(r'\d+\s*(?:gb|go)\s*[\+\/]?\s*\d*\s*(?:gb|go)?', '', name, flags=re.I)
    name = re.sub(r'\d+\s*/\s*\d+', '', name)
    
    # Remove network indicators for matching
    name = re.sub(r'\b[45]g\b', '', name, flags=re.I)
    
    # Remove special characters and normalize spaces
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def build_spec_database(df, source_name, name_col='model'):
    """Build a database of specs from a dataframe."""
    spec_db = {}
    
    # Find the name column
    if name_col not in df.columns:
        if 'name' in df.columns:
            name_col = 'name'
        elif 'model' in df.columns:
            name_col = 'model'
        else:
            print(f"  Warning: No name column found in {source_name}")
            return spec_db
    
    for idx, row in df.iterrows():
        base_model = normalize_model_name(row.get(name_col, ''))
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
                new_count = len(valid_specs)
                if new_count > existing_count:
                    spec_db[base_model] = specs
    
    return spec_db


def find_best_match(model_name, spec_db):
    """Find the best matching specs for a model."""
    base_model = normalize_model_name(model_name)
    
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
    
    bestphone_path = base_path / "bestphone_smartphones.csv"
    tunisianet_path = base_path / "tunisianet_smartphones_filled.csv"
    mytek_path = base_path / "mytek_smartphones_filled.csv"
    spacenet_path = base_path / "spacenet_smartphones_filled.csv"
    output_path = base_path / "bestphone_smartphones_filled.csv"
    
    # Load BestPhone data
    print("Loading datasets...")
    bestphone_df = pd.read_csv(bestphone_path)
    print(f"  BestPhone: {len(bestphone_df)} rows")
    
    # Load reference datasets
    spec_db = {}
    
    for ref_path, ref_name in [
        (tunisianet_path, 'Tunisianet'),
        (mytek_path, 'Mytek'),
        (spacenet_path, 'SpaceNet')
    ]:
        if ref_path.exists():
            ref_df = pd.read_csv(ref_path)
            ref_specs = build_spec_database(ref_df, ref_name)
            spec_db.update(ref_specs)
            print(f"  {ref_name}: {len(ref_df)} rows -> {len(ref_specs)} unique models")
        else:
            print(f"  {ref_name}: file not found, skipping")
    
    print(f"\nTotal unique models in spec database: {len(spec_db)}")
    
    # Ensure columns exist
    spec_columns = ['battery_mah', 'screen_inches', 'camera_rear_mp', 'camera_front_mp', 
                   'network', 'os', 'processor_type']
    for col in spec_columns:
        if col not in bestphone_df.columns:
            bestphone_df[col] = ""
    
    # Fill missing specs
    print("\nFilling missing specs...")
    filled_count = 0
    match_count = 0
    
    for idx, row in bestphone_df.iterrows():
        model_name = row.get('name', '')
        if not model_name:
            continue
        
        # Find matching specs
        matched_specs = find_best_match(model_name, spec_db)
        
        if matched_specs:
            match_count += 1
            
            # Fill missing fields
            for field in spec_columns:
                current_val = row.get(field)
                new_val = matched_specs.get(field)
                
                # Fill if current is empty and new value exists
                if (pd.isna(current_val) or str(current_val).strip() == '') and pd.notna(new_val) and str(new_val).strip():
                    # Convert to string to avoid dtype issues
                    bestphone_df.at[idx, field] = str(new_val) if pd.notna(new_val) else ""
                    filled_count += 1
    
    print(f"  Found matches for {match_count} models")
    print(f"  Filled {filled_count} missing values")
    
    # Save filled data
    bestphone_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nSaved to {output_path}")
    
    # Summary
    print("\nData coverage summary:")
    total = len(bestphone_df)
    for col in spec_columns:
        filled = bestphone_df[col].notna().sum()
        non_empty = sum(1 for v in bestphone_df[col] if pd.notna(v) and str(v).strip())
        pct = non_empty / total * 100 if total > 0 else 0
        print(f"  {col}: {non_empty}/{total} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
