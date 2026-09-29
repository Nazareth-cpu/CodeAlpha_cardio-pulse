"""
Health check endpoints for CardioPulse FastAPI Backend.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from backend.app.schemas.common import HealthResponse
from backend.app.services.prediction_service import prediction_service

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Reports the operational status of the API and availability of the ML inference layer.",
    status_code=status.HTTP_200_OK,
)
def check_health():
    """Verify backend and ML model readiness."""
    is_ready = prediction_service.is_model_available()

    if not is_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "service": "heart-disease-prediction-api",
                "model_loaded": False,
                "model_name": None,
                "model_version": None,
            },
        )

    try:
        meta = prediction_service.get_metadata()
        model_name = meta.model_name
        model_version = meta.model_version
    except Exception:
        model_name = "Logistic Regression"
        model_version = "heart-disease-logistic-regression-v1"

    return HealthResponse(
        status="healthy",
        service="heart-disease-prediction-api",
        model_loaded=True,
        model_name=model_name,
        model_version=model_version,
    )
