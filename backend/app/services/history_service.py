"""
History Service for CardioPulse FastAPI Backend.

Orchestrates user-scoped prediction history queries, single-record retrieval, and record deletion.
Enforces business rules, pagination constraints, and authorization boundaries.
Never exposes raw database exceptions or internal stack traces to callers.
"""

import logging
from typing import Optional

from fastapi import HTTPException, status

from backend.app.dependencies.auth import AuthenticatedUser
from backend.app.repositories.prediction_repository import (
    BasePredictionRepository,
    DatabaseUnavailableError,
    RepositoryError,
)
from backend.app.schemas.prediction import (
    DeletePredictionResponse,
    PredictionDetailResponse,
    PredictionHistoryResponse,
    PredictionSummaryItem,
)

logger = logging.getLogger("cardiopulse.history_service")


class HistoryService:
    """Manages prediction retrieval and lifecycle operations for authenticated users."""

    def __init__(self, repository: BasePredictionRepository) -> None:
        self.repository = repository

    def get_user_history(
        self,
        current_user: AuthenticatedUser,
        limit: int = 20,
    ) -> PredictionHistoryResponse:
        """
        Retrieve paginated prediction history strictly scoped to the authenticated user.
        Enforces server-side limit ceiling and deterministic ordering.
        """
        # Validate limit boundary
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Query parameter 'limit' must be an integer between 1 and 100.",
            )

        try:
            raw_records = self.repository.list_user_predictions(
                uid=current_user.uid,
                limit=limit,
            )
            items = [
                PredictionSummaryItem(
                    prediction_id=r["prediction_id"],
                    prediction=r["prediction"],
                    probability=r["probability"],
                    model_name=r["model_name"],
                    model_version=r["model_version"],
                    created_at=r["created_at"],
                )
                for r in raw_records
            ]
            return PredictionHistoryResponse(
                predictions=items,
                total=len(items),
                limit=limit,
            )
        except DatabaseUnavailableError as exc:
            logger.error("Database unavailable during history retrieval: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service temporarily unavailable.",
            )
        except RepositoryError as exc:
            logger.error("Failed to query prediction history: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve prediction history.",
            )
        except Exception as exc:
            logger.error("Unexpected error during history retrieval: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve prediction history.",
            )

    def get_prediction_by_id(
        self,
        current_user: AuthenticatedUser,
        prediction_id: str,
    ) -> PredictionDetailResponse:
        """
        Retrieve a single prediction record scoped strictly to users/{current_user.uid}/predictions/{prediction_id}.
        Guarantees authorization: cannot access records belonging to other users.
        """
        if not prediction_id or not prediction_id.strip():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction record not found.",
            )

        try:
            record = self.repository.get_user_prediction(
                uid=current_user.uid,
                prediction_id=prediction_id.strip(),
            )
            if not record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Prediction record not found.",
                )

            return PredictionDetailResponse(
                prediction_id=record["prediction_id"],
                user_id=record.get("user_id", current_user.uid),
                input=record.get("input", {}),
                result=record.get("result", {}),
                model=record.get("model", {}),
                created_at=record.get("created_at", ""),
            )
        except HTTPException:
            raise
        except DatabaseUnavailableError as exc:
            logger.error("Database unavailable during single prediction lookup: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service temporarily unavailable.",
            )
        except RepositoryError as exc:
            logger.error("Failed to retrieve prediction record: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve prediction record.",
            )
        except Exception as exc:
            logger.error("Unexpected error during single prediction lookup: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve prediction record.",
            )

    def delete_prediction_by_id(
        self,
        current_user: AuthenticatedUser,
        prediction_id: str,
    ) -> DeletePredictionResponse:
        """
        Delete a single prediction record scoped strictly to users/{current_user.uid}/predictions/{prediction_id}.
        Guarantees authorization: cannot delete records belonging to other users.
        """
        if not prediction_id or not prediction_id.strip():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction record not found.",
            )

        try:
            deleted = self.repository.delete_user_prediction(
                uid=current_user.uid,
                prediction_id=prediction_id.strip(),
            )
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Prediction record not found.",
                )

            return DeletePredictionResponse(
                success=True,
                message="Prediction record deleted successfully.",
                prediction_id=prediction_id.strip(),
            )
        except HTTPException:
            raise
        except DatabaseUnavailableError as exc:
            logger.error("Database unavailable during prediction deletion: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service temporarily unavailable.",
            )
        except RepositoryError as exc:
            logger.error("Failed to delete prediction record: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to delete prediction record.",
            )
        except Exception as exc:
            logger.error("Unexpected error during prediction deletion: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to delete prediction record.",
            )
