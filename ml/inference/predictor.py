"""
Production Predictor for CardioPulse ML Multi-Model Inference Layer.

Orchestrates input validation, DataFrame formatting, model selection & execution,
and structured response construction using cached Pipeline artifacts.
"""

from dataclasses import asdict, dataclass
import logging
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from ml.config import (
    DEFAULT_MODEL_ID,
    EDUCATIONAL_DISCLAIMER,
    PRODUCTION_MODEL_NAME,
    PRODUCTION_MODEL_VERSION,
    SUPPORTED_MODEL_IDS,
)
from ml.inference.exceptions import (
    InvalidFeatureInputError,
    InvalidModelError,
    ModelArtifactNotFoundError,
    PredictionError,
)
from ml.inference.model_loader import (
    get_metadata,
    get_model,
    get_registry,
    load_model,
)
from ml.inference.validator import build_dataframe, validate_input

logger = logging.getLogger("cardiopulse.predictor")


@dataclass(frozen=True)
class PredictionResult:
    """
    Strongly typed, structured internal prediction response.
    Never exposes internal scikit-learn or Python pipeline objects.
    Supports both attribute access (.prediction) and dictionary subscripting (['prediction']).
    """
    prediction: int
    probability: float
    model_name: str
    model_version: str
    disclaimer: str
    model_id: str = DEFAULT_MODEL_ID

    def to_dict(self, include_model_id: bool = False) -> Dict[str, Any]:
        """Convert result to clean dictionary representation."""
        data = {
            "prediction": self.prediction,
            "probability": self.probability,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "disclaimer": self.disclaimer,
        }
        if include_model_id:
            data["model_id"] = self.model_id
        return data

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in {"prediction", "probability", "model_id", "model_name", "model_version", "disclaimer"}

    def keys(self):
        return {"prediction", "probability", "model_id", "model_name", "model_version", "disclaimer"}


class HeartDiseasePredictor:
    """
    Stateless, multi-model inference engine for heart disease risk estimation.

    Encapsulates:
      - Multi-model registry lookup and artifact caching
      - Strict input schema validation and domain verification
      - Canonical DataFrame construction
      - Thread-safe scikit-learn pipeline inference
      - Model metadata retrieval for selected model
    """

    def __init__(
        self,
        model_path_or_id: Optional[Any] = None,
        metadata_path: Optional[Path] = None,
        model_path: Optional[Path] = None,
        model_id: Optional[str] = None,
    ) -> None:
        if model_path_or_id is not None:
            if isinstance(model_path_or_id, Path) or (
                isinstance(model_path_or_id, str)
                and (model_path_or_id.endswith(".joblib") or "/" in model_path_or_id or "\\" in model_path_or_id)
            ):
                model_path = Path(model_path_or_id)
            elif isinstance(model_path_or_id, str):
                model_id = model_path_or_id

        self.default_model_id = model_id or DEFAULT_MODEL_ID
        self.model_path = Path(model_path) if model_path is not None else None
        self.metadata_path = Path(metadata_path) if metadata_path is not None else None
        # Eagerly initialize/verify model on construction; force reload if specific path given
        force_reload = self.model_path is not None or self.metadata_path is not None
        self._pipeline = load_model(
            model_path=self.model_path,
            model_id=self.default_model_id,
            force_reload=force_reload,
        )
        self._metadata = get_metadata(self.default_model_id)
        logger.info(
            "Predictor initialized with default model: '%s' (version: '%s')",
            self.model_name,
            self.model_version,
        )

    @property
    def model_name(self) -> str:
        if self._metadata and "model_name" in self._metadata:
            return self._metadata["model_name"]
        return PRODUCTION_MODEL_NAME

    @property
    def model_version(self) -> str:
        if self._metadata and "model_version" in self._metadata:
            return self._metadata["model_version"]
        return PRODUCTION_MODEL_VERSION

    def get_model_metadata(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve frozen model metadata contract for specified or default model."""
        return get_metadata(model_id or self.default_model_id)

    def predict(
        self,
        raw_input: Mapping[str, Any],
        model_id: Optional[str] = None,
    ) -> PredictionResult:
        """
        Execute prediction pipeline for a single clinical observation using requested model.

        Args:
            raw_input: Dictionary containing the 13 canonical features.
            model_id: Optional model identifier from registry (e.g. 'xgboost', 'random_forest').

        Returns:
            PredictionResult: Structured result with prediction (0 or 1), probability, and metadata.

        Raises:
            InvalidModelError: If model_id is not in registry.
            InputValidationError: If validation fails (missing, invalid, or forbidden fields).
            PredictionError: If inference execution encounters an internal error.
        """
        effective_id = model_id.strip().lower() if model_id else self.default_model_id
        registry = get_registry()
        models_dict = registry.get("models", {})

        if effective_id not in models_dict and effective_id not in SUPPORTED_MODEL_IDS:
            raise InvalidModelError(
                f"Unknown model identifier '{effective_id}'. Supported models: {', '.join(SUPPORTED_MODEL_IDS)}"
            )

        # 1. Strict validation & domain checking
        validated_features = validate_input(raw_input)

        # 2. Canonical DataFrame construction
        input_df = build_dataframe(validated_features)

        # 3. Model retrieval & execution
        pipeline = get_model(effective_id)
        try:
            raw_pred = pipeline.predict(input_df)[0]
            raw_proba = pipeline.predict_proba(input_df)[0, 1]
        except Exception as exc:
            logger.error("Model prediction execution failed for '%s': %s", effective_id, type(exc).__name__)
            raise PredictionError(
                f"An unexpected error occurred while executing model '{effective_id}'."
            ) from exc

        prediction = int(raw_pred)
        probability = round(float(raw_proba), 4)

        model_info = models_dict.get(effective_id, {})
        model_name = model_info.get("display_name", self.model_name)
        if effective_id == "logistic_regression":
            model_version = PRODUCTION_MODEL_VERSION
        else:
            model_version = model_info.get("version", self.model_version)

        logger.info(
            "Inference completed successfully using [%s]. Prediction: %d, Probability: %.4f",
            model_name,
            prediction,
            probability,
        )

        return PredictionResult(
            prediction=prediction,
            probability=probability,
            model_id=effective_id,
            model_name=model_name,
            model_version=model_version,
            disclaimer=EDUCATIONAL_DISCLAIMER,
        )


# Global singleton instance for framework-level reuse
_PREDICTOR_INSTANCE: Optional[HeartDiseasePredictor] = None


def get_predictor() -> HeartDiseasePredictor:
    """Retrieve or initialize the global singleton HeartDiseasePredictor."""
    global _PREDICTOR_INSTANCE
    if _PREDICTOR_INSTANCE is None:
        _PREDICTOR_INSTANCE = HeartDiseasePredictor()
    return _PREDICTOR_INSTANCE


def predict(input_data: Mapping[str, Any], model_id: Optional[str] = None) -> PredictionResult:
    """Convenience functional interface for predictions using the singleton predictor."""
    return get_predictor().predict(input_data, model_id=model_id)


def get_model_metadata(model_id: Optional[str] = None) -> Dict[str, Any]:
    """Convenience functional interface for retrieving model metadata."""
    return get_predictor().get_model_metadata(model_id=model_id)
