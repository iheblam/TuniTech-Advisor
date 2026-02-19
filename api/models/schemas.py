"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class SmartphoneFeatures(BaseModel):
    """Features for smartphone prediction"""
    
    ram: float = Field(..., description="RAM in GB", ge=1, le=64)
    storage: float = Field(..., description="Storage in GB", ge=16, le=1024)
    battery: float = Field(..., description="Battery capacity in mAh", ge=1000, le=10000)
    screen_size: float = Field(..., description="Screen size in inches", ge=3.0, le=10.0)
    main_camera: float = Field(..., description="Main camera in MP", ge=2, le=200)
    front_camera: float = Field(..., description="Front camera in MP", ge=2, le=100)
    processor_cores: int = Field(default=8, description="Number of processor cores", ge=2, le=16)
    is_5g: bool = Field(default=False, description="5G support")
    has_nfc: bool = Field(default=False, description="NFC support")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ram": 8,
                "storage": 128,
                "battery": 5000,
                "screen_size": 6.5,
                "main_camera": 64,
                "front_camera": 16,
                "processor_cores": 8,
                "is_5g": True,
                "has_nfc": True
            }
        }


class PricePredictionRequest(BaseModel):
    """Request for price prediction"""
    
    features: SmartphoneFeatures
    brand: Optional[str] = Field(None, description="Smartphone brand")
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": {
                    "ram": 8,
                    "storage": 128,
                    "battery": 5000,
                    "screen_size": 6.5,
                    "main_camera": 64,
                    "front_camera": 16,
                    "processor_cores": 8,
                    "is_5g": True,
                    "has_nfc": True
                },
                "brand": "Samsung"
            }
        }


class PricePredictionResponse(BaseModel):
    """Response for price prediction"""
    
    predicted_price: float = Field(..., description="Predicted price in TND")
    confidence_interval: Optional[Dict[str, float]] = Field(
        None, 
        description="95% confidence interval"
    )
    model_info: Dict[str, Any] = Field(..., description="Model metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_price": 1250.50,
                "confidence_interval": {
                    "lower": 1100.00,
                    "upper": 1400.00
                },
                "model_info": {
                    "name": "Random Forest",
                    "version": "1.0",
                    "r2_score": 0.92
                }
            }
        }


class RecommendationRequest(BaseModel):
    """Request for smartphone recommendations"""
    
    budget_min: float = Field(..., description="Minimum budget in TND", ge=0)
    budget_max: float = Field(..., description="Maximum budget in TND", ge=0)
    min_ram: Optional[float] = Field(None, description="Minimum RAM in GB", ge=1)
    min_storage: Optional[float] = Field(None, description="Minimum storage in GB", ge=16)
    min_battery: Optional[float] = Field(None, description="Minimum battery in mAh", ge=1000)
    min_camera: Optional[float] = Field(None, description="Minimum main camera in MP", ge=2)
    brand: Optional[str] = Field(None, description="Preferred brand")
    requires_5g: Optional[bool] = Field(None, description="Requires 5G support")
    limit: int = Field(10, description="Number of recommendations", ge=1, le=50)
    
    @validator('budget_max')
    def budget_max_must_be_greater(cls, v, values):
        if 'budget_min' in values and v < values['budget_min']:
            raise ValueError('budget_max must be greater than or equal to budget_min')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "budget_min": 800,
                "budget_max": 1500,
                "min_ram": 6,
                "min_storage": 128,
                "min_battery": 4000,
                "min_camera": 48,
                "brand": "Samsung",
                "requires_5g": True,
                "limit": 10
            }
        }


class SmartphoneDetail(BaseModel):
    """Detailed smartphone information"""
    
    name: str
    brand: str
    price: float
    store: str
    url: Optional[str] = None
    
    # Specifications
    ram: Optional[float] = None
    storage: Optional[float] = None
    battery: Optional[float] = None
    screen_size: Optional[float] = None
    main_camera: Optional[float] = None
    front_camera: Optional[float] = None
    processor: Optional[str] = None
    is_5g: Optional[bool] = None
    has_nfc: Optional[bool] = None
    
    # Additional info
    availability: Optional[str] = "In Stock"
    match_score: Optional[float] = Field(None, description="How well it matches criteria (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Samsung Galaxy A54",
                "brand": "Samsung",
                "price": 1299.00,
                "store": "Tunisianet",
                "url": "https://www.tunisianet.com.tn/...",
                "ram": 8,
                "storage": 128,
                "battery": 5000,
                "screen_size": 6.4,
                "main_camera": 50,
                "front_camera": 32,
                "processor": "Exynos 1380",
                "is_5g": True,
                "has_nfc": True,
                "availability": "In Stock",
                "match_score": 95.5
            }
        }


class RecommendationResponse(BaseModel):
    """Response for smartphone recommendations"""
    
    total_found: int = Field(..., description="Total smartphones found matching criteria")
    recommendations: List[SmartphoneDetail] = Field(..., description="List of recommended smartphones")
    filters_applied: Dict[str, Any] = Field(..., description="Filters that were applied")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_found": 15,
                "recommendations": [
                    {
                        "name": "Samsung Galaxy A54",
                        "brand": "Samsung",
                        "price": 1299.00,
                        "store": "Tunisianet",
                        "ram": 8,
                        "storage": 128,
                        "battery": 5000,
                        "match_score": 95.5
                    }
                ],
                "filters_applied": {
                    "budget_min": 800,
                    "budget_max": 1500,
                    "min_ram": 6,
                    "brand": "Samsung"
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current server time")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    data_loaded: bool = Field(..., description="Whether data is loaded")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2026-02-16T10:30:00",
                "model_loaded": True,
                "data_loaded": True
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "budget_max must be greater than budget_min",
                "timestamp": "2026-02-16T10:30:00"
            }
        }
