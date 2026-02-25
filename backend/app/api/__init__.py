"""
API Package

Contains FastAPI route handlers for insurance consultation
and contract interpretation endpoints.
"""

from backend.app.api.consultation import router as consultation_router
from backend.app.api.interpretation import router as interpretation_router

__all__ = ["consultation_router", "interpretation_router"]
