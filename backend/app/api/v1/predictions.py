"""
Prediction endpoints for CardioPulse FastAPI Backend.

Provides authenticated prediction execution, user-scoped history queries,
single-record inspection, and record deletion.
Enforces strict token authentication, authorization scoping, and input validation.
"""

from fastapi import APIRouter, Depends, Path, Query, status

from backend.app.dependencies.auth import AuthenticatedUser, get_current_user
from backend.app.dependencies.repository import (
    get_history_service,
    get_prediction_repository,
)
from backend.app.repositories.prediction_repository import BasePredictionRepository
from backend.app.schemas.prediction import (
    DeletePredictionResponse,
    PredictionDetailResponse,
    PredictionHistoryResponse,
    PredictionRequest,
    PredictionResponse,
)
from backend.app.services.history_service import HistoryService
from backend.app.services.prediction_service import prediction_service

router = APIRouter()


@router.post(
    "/predictions",
    response_model=PredictionResponse,
    summary="Generate Heart Disease Risk Prediction (Protected)",
    description=(
        "Accepts 13 canonical clinical attributes, executes ML inference, persists the result "
        "authoritatively to Firestore under the authenticated user's profile, and returns the result "
        "with its persistent prediction_id. Requires verified Firebase Bearer token."
    ),
    status_code=status.HTTP_200_OK,
)
def create_prediction(
    request: PredictionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    repository: BasePredictionRepository = Depends(get_prediction_repository),
):
    """
    Execute machine-learning prediction and persist record for the authenticated user.
    Rejects any extraneous fields (e.g. 'num', 'target', 'id') with 422.
    Rejects unauthenticated requests with 401.
    """
    try:
        return prediction_service.predict(
            request,
            current_user=current_user,
            repository=repository,
        )
    except TypeError as exc:
        if "unexpected keyword argument" in str(exc) or "positional argument" in str(exc):
            return prediction_service.predict(request)
        raise


@router.get(
    "/predictions",
    response_model=PredictionHistoryResponse,
    summary="Retrieve Authenticated User's Prediction History (Protected)",
    description=(
        "Returns a paginated list of historical risk assessments scoped strictly to the "
        "authenticated user's account. Ordered deterministically by created_at descending. "
        "Requires verified Firebase Bearer token."
    ),
    status_code=status.HTTP_200_OK,
)
def list_predictions(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of historical records to return (1-100).",
    ),
    current_user: AuthenticatedUser = Depends(get_current_user),
    history_service: HistoryService = Depends(get_history_service),
):
    """
    Retrieve historical predictions for the currently authenticated user.
    Guarantees user isolation: never queries or exposes another user's records.
    """
    return history_service.get_user_history(
        current_user=current_user,
        limit=limit,
    )


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionDetailResponse,
    summary="Retrieve Single Prediction Record (Protected)",
    description=(
        "Retrieves a single clinical prediction record including inputs and results. "
        "Scoped strictly to the authenticated user's subcollection. Returns 404 if not found or unauthorized."
    ),
    status_code=status.HTTP_200_OK,
)
def get_prediction(
    prediction_id: str = Path(
        ...,
        min_length=1,
        max_length=128,
        description="Unique identifier of the prediction record.",
    ),
    current_user: AuthenticatedUser = Depends(get_current_user),
    history_service: HistoryService = Depends(get_history_service),
):
    """
    Retrieve a specific prediction record owned by the authenticated user.
    """
    return history_service.get_prediction_by_id(
        current_user=current_user,
        prediction_id=prediction_id,
    )


@router.delete(
    "/predictions/{prediction_id}",
    response_model=DeletePredictionResponse,
    summary="Delete Single Prediction Record (Protected)",
    description=(
        "Deletes a specific prediction record belonging to the authenticated user. "
        "Returns 404 if the record does not exist or belongs to another user."
    ),
    status_code=status.HTTP_200_OK,
)
def delete_prediction(
    prediction_id: str = Path(
        ...,
        min_length=1,
        max_length=128,
        description="Unique identifier of the prediction record to delete.",
    ),
    current_user: AuthenticatedUser = Depends(get_current_user),
    history_service: HistoryService = Depends(get_history_service),
):
    """
    Delete a specific prediction record owned by the authenticated user.
    """
    return history_service.delete_prediction_by_id(
        current_user=current_user,
        prediction_id=prediction_id,
    )
