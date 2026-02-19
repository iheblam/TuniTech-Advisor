"""
Data Service for loading and querying smartphone data
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..config import settings


class DataService:
    """Service for smartphone data operations"""
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self):
        """Load smartphone data from CSV"""
        try:
            data_path = Path(settings.data_path) / settings.unified_data_file
            
            if not data_path.exists():
                print(f"Warning: Data file not found at {data_path}")
                return
            
            self.data = pd.read_csv(data_path)
            print(f"✓ Data loaded successfully: {len(self.data)} smartphones")
            
            # Clean column names (remove leading/trailing spaces)
            self.data.columns = self.data.columns.str.strip()
            
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def is_data_loaded(self) -> bool:
        """Check if data is loaded"""
        return self.data is not None and not self.data.empty
    
    def get_recommendations(
        self,
        budget_min: float,
        budget_max: float,
        min_ram: Optional[float] = None,
        min_storage: Optional[float] = None,
        min_battery: Optional[float] = None,
        min_camera: Optional[float] = None,
        brand: Optional[str] = None,
        requires_5g: Optional[bool] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get smartphone recommendations based on criteria
        
        Args:
            budget_min: Minimum price
            budget_max: Maximum price
            min_ram: Minimum RAM (GB)
            min_storage: Minimum storage (GB)
            min_battery: Minimum battery (mAh)
            min_camera: Minimum main camera (MP)
            brand: Preferred brand
            requires_5g: Requires 5G support
            limit: Maximum number of results
            
        Returns:
            List of smartphone dictionaries
        """
        if not self.is_data_loaded():
            return []
        
        # Start with all data
        filtered_data = self.data.copy()
        
        # Apply filters
        if 'price' in filtered_data.columns:
            filtered_data = filtered_data[
                (filtered_data['price'] >= budget_min) &
                (filtered_data['price'] <= budget_max)
            ]
        
        if min_ram and 'ram' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['ram'] >= min_ram]
        
        if min_storage and 'storage' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['storage'] >= min_storage]
        
        if min_battery and 'battery' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['battery'] >= min_battery]
        
        if min_camera and 'main_camera' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['main_camera'] >= min_camera]
        
        if brand and 'brand' in filtered_data.columns:
            # Case-insensitive brand matching
            filtered_data = filtered_data[
                filtered_data['brand'].str.lower() == brand.lower()
            ]
        
        if requires_5g and 'is_5g' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['is_5g'] == True]
        
        # Sort by price (ascending) and limit results
        if 'price' in filtered_data.columns:
            filtered_data = filtered_data.sort_values('price')
        
        filtered_data = filtered_data.head(limit)
        
        # Convert to list of dicts
        recommendations = filtered_data.to_dict('records')
        
        # Calculate match score (simple heuristic)
        for rec in recommendations:
            score = 100.0
            # Adjust score based on how well it matches criteria
            # This is a simple example - can be made more sophisticated
            if 'price' in rec:
                price_range = budget_max - budget_min
                if price_range > 0:
                    # Prefer items closer to the lower end of the budget
                    price_score = (budget_max - rec['price']) / price_range * 20
                    score -= max(0, 20 - price_score)
            
            rec['match_score'] = round(score, 2)
        
        return recommendations
    
    def get_smartphone_by_id(self, smartphone_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific smartphone by ID"""
        if not self.is_data_loaded():
            return None
        
        if 'id' not in self.data.columns:
            return None
        
        result = self.data[self.data['id'] == smartphone_id]
        if result.empty:
            return None
        
        return result.iloc[0].to_dict()
    
    def get_all_brands(self) -> List[str]:
        """Get list of all unique brands"""
        if not self.is_data_loaded() or 'brand' not in self.data.columns:
            return []
        
        return sorted(self.data['brand'].dropna().unique().tolist())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the dataset"""
        if not self.is_data_loaded():
            return {}
        
        stats = {
            'total_smartphones': len(self.data),
            'brands': len(self.data['brand'].unique()) if 'brand' in self.data.columns else 0,
        }
        
        # Price statistics
        if 'price' in self.data.columns:
            stats['price'] = {
                'min': float(self.data['price'].min()),
                'max': float(self.data['price'].max()),
                'mean': float(self.data['price'].mean()),
                'median': float(self.data['price'].median()),
            }
        
        # Store distribution
        if 'store' in self.data.columns:
            stats['stores'] = self.data['store'].value_counts().to_dict()
        
        return stats


# Create singleton instance
data_service = DataService()
