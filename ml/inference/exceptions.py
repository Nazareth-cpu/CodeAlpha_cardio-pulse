"""
Custom Exceptions for CardioPulse ML Inference Layer.

Provides structured, clean exceptions that decouple internal ML errors
from web frameworks and hide internal file paths and system details.
"""


class InferenceBaseError(Exception):
    """Base exception for all CardioPulse ML inference errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ModelLoadError(InferenceBaseError):
    """Raised when the serialized model artifact or metadata fails to load."""
    pass


class ModelNotFoundError(ModelLoadError):
    """Raised when the serialized model artifact is missing from disk."""
    pass


class CorruptedModelError(ModelLoadError):
    """Raised when the serialized model artifact is damaged, incompatible, or lacks required methods."""
    pass


class InputValidationError(InferenceBaseError):
    """Raised when the prediction input violates schema, categorical domains, or types."""

    def __init__(self, message: str, field: str = None) -> None:
        super().__init__(message)
        self.field = field


class ForbiddenFieldError(InputValidationError):
    """Raised when a forbidden field (num, target, id) is passed, preventing target leakage."""
    pass


class MissingFieldError(InputValidationError):
    """Raised when a required canonical feature is missing from the input."""
    pass


class UnknownFieldError(InputValidationError):
    """Raised when an unrecognized/unexpected field is passed in the input."""
    pass


class InvalidCategoricalError(InputValidationError):
    """Raised when a categorical field contains a value outside its defined discrete domain."""
    pass


class InvalidNumericalError(InputValidationError):
    """Raised when a numerical field is non-numeric, null, NaN, or infinite."""
    pass


class PredictionError(InferenceBaseError):
    """Raised when model inference execution fails."""
    pass


class InvalidModelError(InferenceBaseError):
    """Raised when an unknown or unsupported model_id is requested."""
    pass


# Backward compatibility aliases for Phase 1B test suite
InvalidFeatureInputError = InputValidationError
ModelArtifactNotFoundError = ModelNotFoundError
