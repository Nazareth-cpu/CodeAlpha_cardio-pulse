"""
Model catalog and metadata endpoints for CardioPulse FastAPI Backend.

Exposes:
  - GET /models: Multi-model catalog of all four available models with real artifact availability and test metrics.
  - GET /model: Backward-compatible metadata contract for default model.
"""

from fastapi import APIRouter, status

from backend.app.schemas.prediction import ModelListResponse, ModelMetadataResponse
from backend.app.services.prediction_service import prediction_service

router = APIRouter()


@router.get(
    "/models",
    response_model=ModelListResponse,
    summary="Multi-Model Catalog & Performance Metrics",
    description="Exposes all four machine learning models with their test-set evaluation metrics and live artifact availability.",
    status_code=status.HTTP_200_OK,
)
def get_all_models():
    """Retrieve catalog of all four models (Logistic Regression, SVM, Random Forest, XGBoost)."""
    return prediction_service.get_models_catalog()


@router.get(
    "/model",
    response_model=ModelMetadataResponse,
    summary="Model Metadata & Performance Contract (Default)",
    description="Exposes verified evaluation metrics, canonical feature schema, and operational parameters for default model.",
    status_code=status.HTTP_200_OK,
)
def get_model_info():
    """Retrieve default model information without exposing system paths or sensitive configuration."""
    return prediction_service.get_metadata()
