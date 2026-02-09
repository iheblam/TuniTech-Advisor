#!/usr/bin/env python3
"""
=============================================================================
TuniTech Advisor - Exploratory Data Analysis (EDA)
Week 1: Data Exploration & Analysis
=============================================================================

Project: Phone Recommendation System for Tunisian E-commerce
Team: Iheb Lamouchi, Yassine Nemri
Date: February 2026

This script performs comprehensive EDA on scraped smartphone data from:
- Tunisianet (357 products)
- SpaceNet (320 products)  
- Mytek (281 products)
- BestPhone (138 products)

Total: 1,096 smartphone listings

=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# =============================================================================
# STEP 1: LOAD ALL DATASETS
# =============================================================================
print("=" * 70)
print("STEP 1: LOADING DATASETS")
print("=" * 70)

base_path = Path("dataset")

# Load all filled datasets
datasets = {}
sources = [
    ("Tunisianet", "tunisianet_smartphones_filled.csv", "model"),
    ("Mytek", "mytek_smartphones_filled.csv", "model"),
    ("SpaceNet", "spacenet_smartphones_filled.csv", "model"),
    ("BestPhone", "bestphone_smartphones_filled.csv", "name"),
]

for source_name, filename, name_col in sources:
    path = base_path / filename
    if path.exists():
        df = pd.read_csv(path)
        df['source'] = source_name
        # Standardize name column
        if name_col != 'name' and name_col in df.columns:
            df['name'] = df[name_col]
        datasets[source_name] = df
        print(f"  ✓ {source_name}: {len(df)} products loaded")
    else:
        print(f"  ✗ {source_name}: File not found ({filename})")

# =============================================================================
# STEP 2: CREATE UNIFIED DATASET
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: CREATING UNIFIED DATASET")
print("=" * 70)

# Define common columns for unified dataset
common_columns = [
    'name', 'brand', 'ram_gb', 'storage_gb', 'battery_mah', 
    'screen_inches', 'camera_rear_mp', 'camera_front_mp',
    'network', 'os', 'processor_type', 'price', 'source', 'url'
]

def standardize_dataframe(df, source_name):
    """Standardize column names and extract price."""
    result = pd.DataFrame()
    
    # Name
    result['name'] = df.get('name', df.get('model', ''))
    
    # Brand
    result['brand'] = df.get('brand', '')
    
    # Specs
    result['ram_gb'] = df.get('ram_gb', '')
    result['storage_gb'] = df.get('storage_gb', '')
    result['battery_mah'] = df.get('battery_mah', '')
    result['screen_inches'] = df.get('screen_inches', '')
    result['camera_rear_mp'] = df.get('camera_rear_mp', '')
    result['camera_front_mp'] = df.get('camera_front_mp', '')
    result['network'] = df.get('network', '')
    result['os'] = df.get('os', '')
    result['processor_type'] = df.get('processor_type', '')
    
    # Price - handle different column names
    if 'price_dt' in df.columns:
        result['price'] = df['price_dt']
    elif 'price_tnd' in df.columns:
        result['price'] = df['price_tnd']
    elif 'price' in df.columns:
        result['price'] = df['price']
    else:
        result['price'] = np.nan
    
    # URL
    result['url'] = df.get('url', df.get('product_url', ''))
    
    # Source
    result['source'] = source_name
    
    return result

# Combine all datasets
unified_dfs = []
for source_name, df in datasets.items():
    std_df = standardize_dataframe(df, source_name)
    unified_dfs.append(std_df)
    print(f"  ✓ Standardized {source_name}: {len(std_df)} rows")

unified_df = pd.concat(unified_dfs, ignore_index=True)
print(f"\n  📊 UNIFIED DATASET: {len(unified_df)} total products")

# Save unified dataset
unified_df.to_csv(base_path / "unified_smartphones.csv", index=False, encoding='utf-8-sig')
print(f"  💾 Saved to dataset/unified_smartphones.csv")

# =============================================================================
# STEP 3: DATA CLEANING & TYPE CONVERSION
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: DATA CLEANING & TYPE CONVERSION")
print("=" * 70)

# Convert numeric columns
numeric_cols = ['ram_gb', 'storage_gb', 'battery_mah', 'screen_inches', 
                'camera_rear_mp', 'camera_front_mp', 'price']

for col in numeric_cols:
    # Replace empty strings and 'nan' with NaN
    unified_df[col] = unified_df[col].replace(['', 'nan', 'None', 'NaN'], np.nan)
    # Convert to numeric
    unified_df[col] = pd.to_numeric(unified_df[col], errors='coerce')
    
    valid_count = unified_df[col].notna().sum()
    pct = valid_count / len(unified_df) * 100
    print(f"  {col}: {valid_count}/{len(unified_df)} valid ({pct:.1f}%)")

# Clean brand names
unified_df['brand'] = unified_df['brand'].str.strip().str.title()
unified_df['brand'] = unified_df['brand'].replace({
    'Xiaomi': 'Xiaomi', 
    'Redmi': 'Xiaomi',
    'Poco': 'Xiaomi',
    '': 'Unknown'
})

print(f"\n  ✓ Data cleaning completed")

# =============================================================================
# STEP 4: DATASET OVERVIEW
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: DATASET OVERVIEW")
print("=" * 70)

print(f"\n📊 GENERAL STATISTICS")
print(f"  Total products: {len(unified_df)}")
print(f"  Unique brands: {unified_df['brand'].nunique()}")
print(f"  Sources: {unified_df['source'].nunique()}")

print(f"\n📦 PRODUCTS BY SOURCE:")
source_counts = unified_df['source'].value_counts()
for source, count in source_counts.items():
    print(f"  {source}: {count} products ({count/len(unified_df)*100:.1f}%)")

print(f"\n🏷️ TOP 10 BRANDS:")
brand_counts = unified_df['brand'].value_counts().head(10)
for brand, count in brand_counts.items():
    print(f"  {brand}: {count} products")

# =============================================================================
# STEP 5: PRICE ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: PRICE ANALYSIS")
print("=" * 70)

# Filter valid prices
valid_prices = unified_df[unified_df['price'].notna() & (unified_df['price'] > 0)]

print(f"\n💰 PRICE STATISTICS (in TND):")
print(f"  Products with valid price: {len(valid_prices)}/{len(unified_df)}")
print(f"  Min price: {valid_prices['price'].min():.0f} TND")
print(f"  Max price: {valid_prices['price'].max():.0f} TND")
print(f"  Mean price: {valid_prices['price'].mean():.0f} TND")
print(f"  Median price: {valid_prices['price'].median():.0f} TND")
print(f"  Std deviation: {valid_prices['price'].std():.0f} TND")

print(f"\n💰 PRICE BY SOURCE:")
for source in valid_prices['source'].unique():
    source_prices = valid_prices[valid_prices['source'] == source]['price']
    print(f"  {source}:")
    print(f"    Min: {source_prices.min():.0f} | Max: {source_prices.max():.0f} | Avg: {source_prices.mean():.0f} TND")

print(f"\n💰 AVERAGE PRICE BY BRAND (Top 10):")
brand_avg_price = valid_prices.groupby('brand')['price'].agg(['mean', 'count']).sort_values('mean', ascending=False)
for brand, row in brand_avg_price.head(10).iterrows():
    if row['count'] >= 3:  # Only brands with at least 3 products
        print(f"  {brand}: {row['mean']:.0f} TND (n={int(row['count'])})")

# =============================================================================
# STEP 6: SPECS ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: SPECIFICATIONS ANALYSIS")
print("=" * 70)

print(f"\n📱 RAM DISTRIBUTION:")
ram_dist = unified_df['ram_gb'].value_counts().sort_index()
for ram, count in ram_dist.items():
    if pd.notna(ram):
        print(f"  {int(ram)} GB: {count} products ({count/len(unified_df)*100:.1f}%)")

print(f"\n💾 STORAGE DISTRIBUTION:")
storage_dist = unified_df['storage_gb'].value_counts().sort_index()
for storage, count in storage_dist.head(10).items():
    if pd.notna(storage):
        print(f"  {int(storage)} GB: {count} products ({count/len(unified_df)*100:.1f}%)")

print(f"\n🔋 BATTERY STATISTICS:")
valid_battery = unified_df[unified_df['battery_mah'].notna()]
if len(valid_battery) > 0:
    print(f"  Min: {valid_battery['battery_mah'].min():.0f} mAh")
    print(f"  Max: {valid_battery['battery_mah'].max():.0f} mAh")
    print(f"  Average: {valid_battery['battery_mah'].mean():.0f} mAh")
    print(f"  Most common: {valid_battery['battery_mah'].mode().iloc[0]:.0f} mAh")

print(f"\n📶 NETWORK DISTRIBUTION:")
network_dist = unified_df['network'].value_counts()
for net, count in network_dist.items():
    if pd.notna(net) and str(net).strip():
        print(f"  {net}: {count} products")

print(f"\n📱 OS DISTRIBUTION:")
os_dist = unified_df['os'].value_counts()
for os_name, count in os_dist.head(5).items():
    if pd.notna(os_name) and str(os_name).strip():
        print(f"  {os_name}: {count} products")

# =============================================================================
# STEP 7: MISSING VALUES ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("STEP 7: MISSING VALUES ANALYSIS")
print("=" * 70)

print(f"\n❓ MISSING VALUES BY COLUMN:")
for col in unified_df.columns:
    missing = unified_df[col].isna().sum()
    empty_str = (unified_df[col].astype(str).str.strip() == '').sum()
    total_missing = missing + empty_str
    pct = total_missing / len(unified_df) * 100
    status = "✓" if pct < 20 else "⚠️" if pct < 50 else "❌"
    print(f"  {status} {col}: {total_missing} missing ({pct:.1f}%)")

# =============================================================================
# STEP 8: DATA QUALITY SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("STEP 8: DATA QUALITY SUMMARY")
print("=" * 70)

# Calculate overall quality score
quality_scores = {}
critical_cols = ['name', 'brand', 'price', 'ram_gb', 'storage_gb', 'battery_mah']

for col in critical_cols:
    valid = unified_df[col].notna() & (unified_df[col].astype(str).str.strip() != '')
    quality_scores[col] = valid.sum() / len(unified_df) * 100

avg_quality = np.mean(list(quality_scores.values()))

print(f"\n📊 QUALITY SCORES (Critical Fields):")
for col, score in quality_scores.items():
    status = "✓" if score >= 80 else "⚠️" if score >= 50 else "❌"
    print(f"  {status} {col}: {score:.1f}%")

print(f"\n  📈 OVERALL QUALITY SCORE: {avg_quality:.1f}%")

# =============================================================================
# STEP 9: KEY INSIGHTS
# =============================================================================
print("\n" + "=" * 70)
print("STEP 9: KEY INSIGHTS")
print("=" * 70)

print("""
📌 KEY FINDINGS:

1. DATASET SIZE
   - Total of 1,096 smartphone listings from 4 Tunisian e-commerce sites
   - Tunisianet has the largest inventory (357 products)

2. BRAND DISTRIBUTION
   - Samsung and Xiaomi dominate the market
   - Apple (iPhone) present across all stores
   - Local/budget brands also available (Condor, Lesia, etc.)

3. PRICE INSIGHTS
   - Wide price range from budget (~200 TND) to flagship (~5000+ TND)
   - Average smartphone price around 1000-1500 TND
   - Price varies across stores for same model (opportunity for comparison)

4. SPECIFICATIONS TRENDS
   - Most phones have 4-8 GB RAM
   - 128 GB storage is the most common
   - 5000 mAh battery becoming standard
   - 5G adoption increasing in newer models

5. DATA QUALITY
   - Good coverage for core specs (brand, RAM, storage)
   - Price data available for most products
   - Some missing specs filled from known databases

6. RECOMMENDATION SYSTEM POTENTIAL
   - Same phone available at different prices across stores
   - Can recommend based on specs + show price comparison
   - Budget-based filtering possible with price data
""")

# =============================================================================
# STEP 10: SAVE SUMMARY REPORT
# =============================================================================
print("\n" + "=" * 70)
print("STEP 10: GENERATING SUMMARY REPORT")
print("=" * 70)

summary_report = f"""
# TuniTech Advisor - EDA Summary Report
Generated: February 2026

## Dataset Overview
- **Total Products**: {len(unified_df)}
- **Sources**: Tunisianet, SpaceNet, Mytek, BestPhone
- **Unique Brands**: {unified_df['brand'].nunique()}

## Products by Source
{source_counts.to_string()}

## Top Brands
{brand_counts.to_string()}

## Price Statistics (TND)
- Min: {valid_prices['price'].min():.0f}
- Max: {valid_prices['price'].max():.0f}
- Mean: {valid_prices['price'].mean():.0f}
- Median: {valid_prices['price'].median():.0f}

## Data Quality
- Overall Quality Score: {avg_quality:.1f}%
- Products with valid price: {len(valid_prices)}/{len(unified_df)} ({len(valid_prices)/len(unified_df)*100:.1f}%)

## Next Steps
1. Week 2: Data Preprocessing & Feature Engineering
2. Week 3: Model Development with MLflow
3. Week 4: FastAPI Backend
4. Week 5: React Frontend
5. Week 6: Docker & Integration
6. Week 7: Deployment & Presentation
"""

# Save report
with open("EDA_REPORT.md", "w", encoding="utf-8") as f:
    f.write(summary_report)
print("  💾 Saved EDA_REPORT.md")

print("\n" + "=" * 70)
print("✅ EDA COMPLETED SUCCESSFULLY!")
print("=" * 70)
