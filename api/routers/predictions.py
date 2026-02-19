"""
Price prediction endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..models.schemas import (
    PricePredictionRequest,
    PricePredictionResponse,
    SmartphoneFeatures
)
from ..services.ml_service import ml_service

router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.post("/price", response_model=PricePredictionResponse)
async def predict_price(request: PricePredictionRequest):
    """
    Predict smartphone price based on specifications
    
    This endpoint uses the trained ML model to predict the price
    of a smartphone given its specifications.
    """
    if not ml_service.is_model_loaded():
        raise HTTPException(
            status_code=503,
            detail="ML model is not loaded. Please ensure the model is trained and available."
        )
    
    try:
        # Convert features to dict
        features_dict = request.features.model_dump()
        
        # Adjust features if brand is provided
        if request.brand:
            features_dict = ml_service.estimate_features_from_brand(
                request.brand,
                features_dict
            )
        
        # Predict price
        predicted_price, confidence_interval = ml_service.predict_price(
            features_dict,
            return_confidence=True
        )
        
        # Get model info
        model_info = ml_service.get_model_info()
        
        return PricePredictionResponse(
            predicted_price=predicted_price,
            confidence_interval=confidence_interval,
            model_info=model_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during prediction: {str(e)}"
        )


@router.post("/batch-price")
async def predict_batch_prices(features_list: list[SmartphoneFeatures]):
    """
    Predict prices for multiple smartphones at once
    
    Useful for bulk predictions
    """
    if not ml_service.is_model_loaded():
        raise HTTPException(
            status_code=503,
            detail="ML model is not loaded."
        )
    
    try:
        predictions = []
        
        for features in features_list:
            features_dict = features.model_dump()
            predicted_price, confidence_interval = ml_service.predict_price(
                features_dict,
                return_confidence=True
            )
            
            predictions.append({
                "features": features_dict,
                "predicted_price": predicted_price,
                "confidence_interval": confidence_interval
            })
        
        return {
            "total": len(predictions),
            "predictions": predictions,
            "model_info": ml_service.get_model_info()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during batch prediction: {str(e)}"
        )
