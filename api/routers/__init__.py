"""
API Routers
"""

from .health import router as health_router
from .predictions import router as predictions_router
from .recommendations import router as recommendations_router
from .auth import router as auth_router
from .admin import router as admin_router
from .analytics import router as analytics_router
from .scheduler import router as scheduler_router
from .community import router as community_router

__all__ = [
    "health_router",
    "predictions_router",
    "recommendations_router",
    "auth_router",
    "admin_router",
    "analytics_router",
    "scheduler_router",
    "community_router",
]
