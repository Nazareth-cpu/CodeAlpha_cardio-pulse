"""
Prediction Service for CardioPulse FastAPI Backend.

Acts as an orchestration bridge between FastAPI route handlers,
the standalone Phase 1 ML multi-model inference layer, and the Phase 4 persistent Firestore data layer.
Does not duplicate preprocessing, model execution, or dataset handling.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from backend.app.dependencies.auth import AuthenticatedUser
from backend.app.repositories.prediction_repository import (
    BasePredictionRepository,
    DatabaseUnavailableError,
    RepositoryError,
)
from backend.app.schemas.prediction import (
    ModelInfoItem,
    ModelListResponse,
    ModelMetadataResponse,
    PredictionRequest,
    PredictionResponse,
)
from ml.config import CANONICAL_FEATURES, DEFAULT_MODEL_ID
from ml.inference import (
    HeartDiseasePredictor,
    InferenceBaseError,
    InvalidModelError,
    ModelLoadError,
    PredictionResult,
    get_available_models,
    get_metadata,
    get_model,
    get_model_metadata,
    get_predictor,
    predict as ml_predict,
)

logger = logging.getLogger("cardiopulse.service")


class PredictionService:
    """Orchestrates multi-model predictions, metadata retrieval, and persistence."""

    def __init__(self, repository: Optional[BasePredictionRepository] = None) -> None:
        self.repository = repository

    @staticmethod
    def is_model_available(model_id: Optional[str] = None) -> bool:
        """Check if requested model artifact is loaded and operational."""
        try:
            pipeline = get_model(model_id)
            return pipeline is not None and hasattr(pipeline, "predict")
        except Exception as exc:
            logger.error("Model availability check failed for '%s': %s", model_id, type(exc).__name__)
            return False

    @staticmethod
    def get_models_catalog() -> ModelListResponse:
        """Retrieve full catalog of all 4 models with test metrics and live availability."""
        models_data = get_available_models()
        items = [
            ModelInfoItem(
                id=m["id"],
                name=m["name"],
                version=m["version"],
                description=m.get("description"),
                metrics=m.get("metrics", {}),
                available=m.get("available", False),
            )
            for m in models_data
        ]
        return ModelListResponse(models=items, default_model_id=DEFAULT_MODEL_ID)

    @staticmethod
    def get_metadata(model_id: Optional[str] = None) -> ModelMetadataResponse:
        """Retrieve frozen model metadata contract for specific or default model."""
        meta = get_model_metadata(model_id)
        return ModelMetadataResponse(
            model_name=meta.get("model_name", "Logistic Regression"),
            model_version=meta.get("model_version", "heart-disease-logistic-regression-v1"),
            task=meta.get("task", "binary classification"),
            dataset=meta.get("dataset", "UCI Cleveland Heart Disease Dataset"),
            selection_criterion=meta.get("selection_criterion", "ROC-AUC"),
            metrics=meta.get("metrics", {}),
            features=meta.get("features", []),
            numerical_features=meta.get("numerical_features", []),
            categorical_features=meta.get("categorical_features", []),
            confusion_matrix=meta.get("confusion_matrix", {}),
            disclaimer=meta.get("disclaimer", ""),
        )

    def predict(
        self,
        request: PredictionRequest,
        current_user: Optional[AuthenticatedUser] = None,
        repository: Optional[BasePredictionRepository] = None,
        *args: Any,
        **kwargs: Any,
    ) -> PredictionResponse:
        """
        Execute prediction by passing validated dictionary and requested model_id to Phase 1 inference layer,
        then persist successful prediction under users/{uid}/predictions/{prediction_id}.
        """
        request_dict = request.model_dump()
        selected_model_id = request_dict.get("model_id") or DEFAULT_MODEL_ID

        # Extract only the 13 canonical features for ML inference input
        raw_features = {k: request_dict[k] for k in CANONICAL_FEATURES if k in request_dict}

        # Step 1: Execute ML inference with selected model
        try:
            result: PredictionResult = ml_predict(raw_features, model_id=selected_model_id)
        except InvalidModelError as err:
            logger.warning("Invalid model requested: %s", selected_model_id)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(err),
            )
        except ModelLoadError as err:
            logger.error("Selected model artifact could not be loaded: %s", err)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Requested model '{selected_model_id}' is temporarily unavailable.",
            )

        # Step 2: Determine repository
        repo = repository or self.repository
        if repo is None:
            from backend.app.dependencies.repository import get_prediction_repository
            repo = get_prediction_repository()

        # Step 3: Persist prediction if user context is available
        prediction_id = ""
        if current_user and current_user.uid:
            try:
                # Update user profile metadata
                repo.upsert_user(uid=current_user.uid, email=current_user.email)

                # Persist prediction record including selected model identity
                record_data = {
                    "input": raw_features,
                    "result": {
                        "prediction": result.prediction,
                        "probability": result.probability,
                    },
                    "model": {
                        "model_id": result.model_id,
                        "model_name": result.model_name,
                        "model_version": result.model_version,
                    },
                }
                prediction_id = repo.create_prediction(
                    uid=current_user.uid,
                    prediction_data=record_data,
                )
            except DatabaseUnavailableError as exc:
                logger.error("Database unavailable during persistence: %s", type(exc).__name__)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Prediction computed successfully but could not be saved to history.",
                )
            except RepositoryError as exc:
                logger.error("Failed to persist prediction record: %s", type(exc).__name__)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Prediction computed successfully but could not be saved to history.",
                )

        return PredictionResponse(
            prediction_id=prediction_id,
            model_id=result.model_id,
            model_name=result.model_name,
            model_version=result.model_version,
            prediction=result.prediction,
            probability=result.probability,
            disclaimer=result.disclaimer,
        )


prediction_service = PredictionService()
