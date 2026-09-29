"""
CardioPulse ML Standalone Inference Package.

Exposes clean, framework-independent multi-model inference and validation APIs.
"""

from ml.inference.exceptions import (
    CorruptedModelError,
    ForbiddenFieldError,
    InferenceBaseError,
    InvalidCategoricalError,
    InvalidModelError,
    InvalidNumericalError,
    InputValidationError,
    MissingFieldError,
    ModelLoadError,
    ModelNotFoundError,
    PredictionError,
    UnknownFieldError,
)
from ml.inference.model_loader import (
    clear_cache,
    get_available_models,
    get_metadata,
    get_model,
    get_registry,
    load_all_models,
    load_metadata,
    load_model,
    load_registry,
)
from ml.inference.predictor import (
    HeartDiseasePredictor,
    PredictionResult,
    get_model_metadata,
    get_predictor,
    predict,
)
from ml.inference.validator import ALLOWED_CATEGORICAL_VALUES, build_dataframe, validate_input

__all__ = [
    "HeartDiseasePredictor",
    "PredictionResult",
    "get_predictor",
    "predict",
    "get_model_metadata",
    "load_model",
    "get_model",
    "load_all_models",
    "get_available_models",
    "get_registry",
    "load_registry",
    "clear_cache",
    "get_metadata",
    "load_metadata",
    "validate_input",
    "build_dataframe",
    "ALLOWED_CATEGORICAL_VALUES",
    "InferenceBaseError",
    "ModelLoadError",
    "ModelNotFoundError",
    "CorruptedModelError",
    "InvalidModelError",
    "InputValidationError",
    "ForbiddenFieldError",
    "MissingFieldError",
    "UnknownFieldError",
    "InvalidCategoricalError",
    "InvalidNumericalError",
    "PredictionError",
]
