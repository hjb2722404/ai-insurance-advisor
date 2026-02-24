"""
API Package

Contains FastAPI route handlers for insurance consultation
and contract interpretation endpoints.
"""

from backend.app.api.consultation import router as consultation_router

__all__ = ["consultation_router"]
