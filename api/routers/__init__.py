"""
API Routers
"""

from .health import router as health_router
from .predictions import router as predictions_router
from .recommendations import router as recommendations_router
from .auth import router as auth_router
from .admin import router as admin_router

__all__ = [
    "health_router",
    "predictions_router",
    "recommendations_router",
    "auth_router",
    "admin_router",
]
