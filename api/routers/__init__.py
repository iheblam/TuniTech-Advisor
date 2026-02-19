"""
API Routers
"""

from .health import router as health_router
from .predictions import router as predictions_router
from .recommendations import router as recommendations_router

__all__ = ["health_router", "predictions_router", "recommendations_router"]
