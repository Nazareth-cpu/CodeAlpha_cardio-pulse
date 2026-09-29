"""
API router aggregation for CardioPulse FastAPI Backend.
"""

from fastapi import APIRouter

from backend.app.api.v1 import health, model, predictions

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(model.router, tags=["Model"])
api_router.include_router(predictions.router, tags=["Predictions"])
