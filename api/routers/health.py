"""
Health check and system status endpoints
"""

from fastapi import APIRouter
from datetime import datetime

from ..models.schemas import HealthResponse
from ..services.ml_service import ml_service
from ..services.data_service import data_service
from ..config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns system status and readiness
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(),
        model_loaded=ml_service.is_model_loaded(),
        data_loaded=data_service.is_data_loaded()
    )


@router.get("/model-info")
async def get_model_info():
    """Get information about the loaded ML model"""
    return ml_service.get_model_info()


@router.get("/data-stats")
async def get_data_statistics():
    """Get statistics about the smartphone dataset"""
    return data_service.get_statistics()


@router.get("/brands")
async def get_brands():
    """Get list of all available brands"""
    brands = data_service.get_all_brands()
    return {
        "total": len(brands),
        "brands": brands
    }
