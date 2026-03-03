"""
Pydantic models for request/response validation
"""

from .schemas import (
    SmartphoneFeatures,
    PricePredictionRequest,
    PricePredictionResponse,
    RecommendationRequest,
    RecommendationResponse,
    SmartphoneDetail,
    HealthResponse,
    ErrorResponse
)

__all__ = [
    "SmartphoneFeatures",
    "PricePredictionRequest",
    "PricePredictionResponse",
    "RecommendationRequest",
    "RecommendationResponse",
    "SmartphoneDetail",
    "HealthResponse",
    "ErrorResponse"
]
