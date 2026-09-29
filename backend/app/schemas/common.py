"""
Common schemas for CardioPulse FastAPI Backend.
"""

from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check status response."""
    status: str = Field(..., description="Operational status of the service ('healthy' or 'degraded')")
    service: str = Field(..., description="Service identifier")
    model_loaded: bool = Field(..., description="Whether the production ML model is loaded and ready")
    model_name: Optional[str] = Field(None, description="Name of the production model")
    model_version: Optional[str] = Field(None, description="Version string of the production model")


class ErrorResponse(BaseModel):
    """Standardized API error response."""
    detail: str = Field(..., description="Human-readable explanation of the error")
