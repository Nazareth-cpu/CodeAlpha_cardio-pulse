"""
Repository dependencies for CardioPulse FastAPI Backend.

Provides injectable repository instances for route handlers.
Supports clean dependency overriding in unit and integration test suites.
"""

import os
import sys
from fastapi import Depends

from backend.app.core.firebase import get_firestore_client
from backend.app.repositories.prediction_repository import (
    BasePredictionRepository,
    FirestorePredictionRepository,
    in_memory_prediction_repository,
)
from backend.app.services.history_service import HistoryService


def is_test_environment() -> bool:
    """Detect if running under a testing runner (unittest/pytest) or test environment."""
    if os.getenv("TESTING") == "1" or os.getenv("ENVIRONMENT") == "testing":
        return True
    if "unittest" in sys.modules or "pytest" in sys.modules:
        return True
    if any("unittest" in arg for arg in sys.argv):
        return True
    return False


def get_prediction_repository() -> BasePredictionRepository:
    """
    Dependency provider returning the active prediction repository.
    Uses Firestore when Firebase Admin client is operational and not running tests.
    Falls back to thread-safe in-memory store for unit tests and offline development.
    """
    if is_test_environment():
        return in_memory_prediction_repository

    client = get_firestore_client()
    if client is not None:
        return FirestorePredictionRepository(client)
    return in_memory_prediction_repository


def get_history_service(
    repository: BasePredictionRepository = Depends(get_prediction_repository),
) -> HistoryService:
    """Dependency provider returning HistoryService with injected repository."""
    return HistoryService(repository)
