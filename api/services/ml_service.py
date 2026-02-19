"""
Machine Learning Service for model loading and predictions
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import mlflow
import mlflow.sklearn
from ..config import settings


class MLService:
    """Service for ML model operations"""
    
    def __init__(self):
        self.model = None
        self.model_info = {}
        self.feature_names = [
            'ram', 'storage', 'battery', 'screen_size',
            'main_camera', 'front_camera', 'processor_cores',
            'is_5g', 'has_nfc'
        ]
        self._load_model()
    
    def _load_model(self):
        """Load the best model from MLflow"""
        try:
            # Set MLflow tracking URI
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            
            # Try to load the latest model from MLflow
            # First, get the experiment
            experiment = mlflow.get_experiment_by_name(settings.mlflow_experiment_name)
            
            if experiment is None:
                print(f"Warning: Experiment '{settings.mlflow_experiment_name}' not found.")
                print("Model will need to be loaded manually or trained first.")
                return
            
            # Get all runs from the experiment, sorted by R2 score
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["metrics.r2_score DESC"],
                max_results=1
            )
            
            if runs.empty:
                print("Warning: No runs found in the experiment.")
                return
            
            # Get the best run
            best_run = runs.iloc[0]
            run_id = best_run.run_id
            
            # Load the model
            model_uri = f"runs:/{run_id}/model"
            self.model = mlflow.sklearn.load_model(model_uri)
            
            # Store model info
            self.model_info = {
                "run_id": run_id,
                "name": best_run.get("params.algorithm", "Unknown"),
                "r2_score": best_run.get("metrics.r2_score", 0),
                "rmse": best_run.get("metrics.rmse", 0),
                "mae": best_run.get("metrics.mae", 0),
            }
            
            print(f"✓ Model loaded successfully: {self.model_info['name']}")
            print(f"  R² Score: {self.model_info['r2_score']:.4f}")
            
        except Exception as e:
            print(f"Error loading model from MLflow: {e}")
            print("Model prediction will not be available.")
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
    
    def predict_price(
        self,
        features: Dict[str, Any],
        return_confidence: bool = True
    ) -> Tuple[float, Optional[Dict[str, float]]]:
        """
        Predict smartphone price
        
        Args:
            features: Dictionary of smartphone features
            return_confidence: Whether to return confidence interval
            
        Returns:
            Tuple of (predicted_price, confidence_interval)
        """
        if not self.is_model_loaded():
            raise RuntimeError("Model is not loaded. Please train a model first.")
        
        # Prepare features in correct order
        feature_values = [features.get(name, 0) for name in self.feature_names]
        X = np.array([feature_values])
        
        # Make prediction
        prediction = self.model.predict(X)[0]
        
        # Calculate confidence interval (simple approach)
        confidence_interval = None
        if return_confidence:
            # Use RMSE from model info to estimate confidence interval
            rmse = self.model_info.get('rmse', prediction * 0.1)  # 10% default if no RMSE
            confidence_interval = {
                'lower': max(0, prediction - 1.96 * rmse),  # 95% CI
                'upper': prediction + 1.96 * rmse
            }
        
        return float(prediction), confidence_interval
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_model_loaded():
            return {
                "loaded": False,
                "message": "No model is currently loaded"
            }
        
        return {
            "loaded": True,
            **self.model_info
        }
    
    def estimate_features_from_brand(
        self,
        brand: str,
        base_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adjust features based on brand (premium brands might have better specs)
        This is a simple heuristic - can be improved with actual brand analysis
        """
        premium_brands = ['Samsung', 'Apple', 'Xiaomi', 'OnePlus', 'OPPO', 'Vivo']
        
        # Make a copy of features
        adjusted_features = base_features.copy()
        
        # If brand is premium, slightly boost features (if not already high)
        if brand in premium_brands:
            # This is just a simple example - adjust based on your data analysis
            pass
        
        return adjusted_features


# Create singleton instance
ml_service = MLService()
