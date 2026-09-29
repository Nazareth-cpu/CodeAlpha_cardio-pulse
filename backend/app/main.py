"""
Main FastAPI Application Entry Point for CardioPulse.

Exposes REST API endpoints, handles lifecycle initialization, configures CORS,
and provides centralized, privacy-safe error handling.
"""

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.router import api_router
from backend.app.core.config import settings
from backend.app.core.firebase import initialize_firebase
from backend.app.core.logging import logger, setup_logging
from backend.app.services.prediction_service import prediction_service
from ml.inference.exceptions import (
    InputValidationError,
    InvalidModelError,
    ModelLoadError,
    PredictionError,
)

# Initialize logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle events: startup and shutdown."""
    logger.info("Starting up %s (version: %s)...", settings.PROJECT_NAME, settings.VERSION)
    logger.info("Environment: %s", settings.ENVIRONMENT)
    logger.info("Allowed CORS origins: %s", settings.CORS_ORIGINS)

    # Initialize Firebase Admin SDK
    initialize_firebase()

    # Pre-verify ML model availability on startup
    is_available = prediction_service.is_model_available()
    if is_available:
        logger.info("Production ML model verified and ready for inference.")
    else:
        logger.warning("Production ML model could not be verified at startup.")

    yield

    logger.info("Shutting down %s...", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production REST API for Machine Learning-Based Heart Disease Risk Prediction. "
        "Strictly intended for educational and research purposes. "
        "Not a substitute for professional clinical medical advice."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(InvalidModelError)
async def invalid_model_exception_handler(request: Request, exc: InvalidModelError):
    """Handle unknown or unsupported model_id cleanly."""
    logger.warning("Invalid model requested on %s: %s", request.url.path, exc.message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


@app.exception_handler(InputValidationError)
async def input_validation_exception_handler(request: Request, exc: InputValidationError):
    """Handle ML input schema and domain validation errors cleanly."""
    logger.warning("Input validation error on %s: %s", request.url.path, exc.message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


@app.exception_handler(ModelLoadError)
async def model_load_exception_handler(request: Request, exc: ModelLoadError):
    """Handle missing or corrupted model artifacts cleanly without leaking filesystem paths."""
    logger.error("Model load error on %s: %s", request.url.path, exc.message)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Prediction service is temporarily unavailable."},
    )


@app.exception_handler(PredictionError)
async def prediction_exception_handler(request: Request, exc: PredictionError):
    """Handle inference execution failures cleanly without leaking internal traces."""
    logger.error("Prediction execution failure on %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred during prediction inference."},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Fallback handler to ensure raw system exceptions or stack traces are never exposed to clients."""
    logger.error("Unhandled exception processing %s: %s", request.url.path, type(exc).__name__, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


# Mount versioned API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root_info():
    """Root informative health summary."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "model": f"{settings.API_V1_STR}/model",
        "predictions": f"{settings.API_V1_STR}/predictions",
    }
