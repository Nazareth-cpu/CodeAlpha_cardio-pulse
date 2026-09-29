"""
Input Validation Layer for CardioPulse ML Inference.

Strictly enforces:
  - Exactly 13 canonical features
  - Rejection of forbidden fields ('num', 'target', 'id')
  - Rejection of missing fields
  - Rejection of unknown/arbitrary fields
  - Rejection of null, NaN, and infinite numerical values
  - Discrete categorical domain verification
  - Canonical DataFrame construction
"""

import logging
import math
from typing import Any, Dict, List, Mapping

import pandas as pd

from ml.config import CANONICAL_FEATURES, CATEGORICAL_FEATURES, EXCLUDED_FEATURES, NUMERICAL_FEATURES
from ml.inference.exceptions import (
    ForbiddenFieldError,
    InvalidCategoricalError,
    InvalidNumericalError,
    MissingFieldError,
    UnknownFieldError,
)

logger = logging.getLogger("cardiopulse.validator")

# Defined discrete domains for categorical features from UCI Cleveland dataset specification
ALLOWED_CATEGORICAL_VALUES: Dict[str, set] = {
    "sex": {0, 1},
    "cp": {1, 2, 3, 4},
    "fbs": {0, 1},
    "restecg": {0, 1, 2},
    "exang": {0, 1},
    "slope": {1, 2, 3},
    "ca": {0, 1, 2, 3},
    "thal": {3, 6, 7},
}


def validate_input(payload: Mapping[str, Any]) -> Dict[str, float]:
    """
    Validate raw input dictionary against canonical schema and clinical domain rules.

    Returns:
        Dict[str, float]: Cleaned, typed feature dictionary in canonical order.

    Raises:
        ForbiddenFieldError: If forbidden leakage fields ('num', 'target', 'id') are present.
        UnknownFieldError: If extra unexpected fields are present.
        MissingFieldError: If any canonical feature is absent.
        InvalidNumericalError: If a numerical field is non-numeric, null, NaN, or infinite.
        InvalidCategoricalError: If a categorical field value is not in its allowed discrete domain.
    """
    if not isinstance(payload, Mapping):
        logger.warning("Validation rejected: Payload is not a key-value mapping.")
        raise UnknownFieldError("Input payload must be a key-value dictionary.")

    payload_keys = set(payload.keys())

    # 1. Target leakage check (Forbidden fields)
    for forbidden in EXCLUDED_FEATURES:
        if forbidden in payload_keys:
            logger.warning("Validation rejected: Prohibited field '%s' detected.", forbidden)
            raise ForbiddenFieldError(
                f"Prohibited field '{forbidden}' is not accepted in prediction input.",
                field=forbidden,
            )

    # 2. Check for unknown/unexpected fields
    canonical_set = set(CANONICAL_FEATURES)
    unknown_fields = payload_keys - canonical_set
    if unknown_fields:
        field_list = sorted(list(unknown_fields))
        logger.warning("Validation rejected: Unknown field(s) %s detected.", field_list)
        raise UnknownFieldError(
            f"Unrecognized field(s) in prediction input: {field_list}. "
            f"Expected only the 13 canonical features.",
            field=field_list[0],
        )

    # 3. Check for missing required features
    missing_fields = canonical_set - payload_keys
    if missing_fields:
        ordered_missing = [f for f in CANONICAL_FEATURES if f in missing_fields]
        logger.warning("Validation rejected: Missing required feature '%s'.", ordered_missing[0])
        raise MissingFieldError(
            f"Missing required prediction feature: '{ordered_missing[0]}'. "
            f"All 13 canonical features must be provided.",
            field=ordered_missing[0],
        )

    validated: Dict[str, float] = {}

    # 4. Numerical validation
    for num_col in NUMERICAL_FEATURES:
        raw_val = payload[num_col]

        # Reject booleans (bool is a subclass of int in Python)
        if isinstance(raw_val, bool):
            logger.warning("Validation rejected: Boolean value provided for numerical field '%s'.", num_col)
            raise InvalidNumericalError(
                f"Numerical field '{num_col}' cannot be a boolean.",
                field=num_col,
            )

        if raw_val is None:
            logger.warning("Validation rejected: Null value provided for numerical field '%s'.", num_col)
            raise InvalidNumericalError(
                f"Numerical field '{num_col}' cannot be null or empty.",
                field=num_col,
            )

        try:
            num_val = float(raw_val)
        except (ValueError, TypeError) as exc:
            logger.warning("Validation rejected: Non-numeric value for field '%s'.", num_col)
            raise InvalidNumericalError(
                f"Numerical field '{num_col}' must be a valid number.",
                field=num_col,
            ) from exc

        if math.isnan(num_val) or math.isinf(num_val):
            logger.warning("Validation rejected: NaN or Infinite value for field '%s'.", num_col)
            raise InvalidNumericalError(
                f"Numerical field '{num_col}' cannot be NaN or infinite.",
                field=num_col,
            )

        validated[num_col] = num_val

    # 5. Categorical validation
    for cat_col in CATEGORICAL_FEATURES:
        raw_val = payload[cat_col]

        # Booleans are only acceptable if 0/1 are expected (like sex/fbs/exang), but strict int conversion is required
        if raw_val is None:
            logger.warning("Validation rejected: Null value for categorical field '%s'.", cat_col)
            raise InvalidCategoricalError(
                f"Categorical field '{cat_col}' cannot be null or empty.",
                field=cat_col,
            )

        try:
            float_val = float(raw_val)
        except (ValueError, TypeError) as exc:
            logger.warning("Validation rejected: Non-numeric categorical value for '%s'.", cat_col)
            raise InvalidCategoricalError(
                f"Categorical field '{cat_col}' must be numeric.",
                field=cat_col,
            ) from exc

        if math.isnan(float_val) or math.isinf(float_val):
            logger.warning("Validation rejected: NaN or Infinite categorical value for '%s'.", cat_col)
            raise InvalidCategoricalError(
                f"Categorical field '{cat_col}' cannot be NaN or infinite.",
                field=cat_col,
            )

        # Check integer equivalence (e.g. 1.0 -> 1, but 1.5 is invalid)
        if not float_val.is_integer():
            logger.warning("Validation rejected: Non-integer value %s for categorical '%s'.", float_val, cat_col)
            raise InvalidCategoricalError(
                f"Categorical field '{cat_col}' must be an integer, got {float_val}.",
                field=cat_col,
            )

        int_val = int(float_val)
        allowed = ALLOWED_CATEGORICAL_VALUES[cat_col]

        if int_val not in allowed:
            logger.warning("Validation rejected: Value %s not in allowed domain for '%s'.", int_val, cat_col)
            sorted_allowed = sorted(list(allowed))
            raise InvalidCategoricalError(
                f"Invalid value {int_val} for categorical field '{cat_col}'. "
                f"Allowed values are {sorted_allowed}.",
                field=cat_col,
            )

        # Preprocessor expects float representations as observed in training dataset
        validated[cat_col] = float(int_val)

    return validated


def build_dataframe(validated_features: Dict[str, float]) -> pd.DataFrame:
    """
    Construct a single-row pandas DataFrame using the strict canonical feature order.
    Guarantees column order matches the training matrix regardless of dictionary ordering.
    """
    ordered_row = {col: validated_features[col] for col in CANONICAL_FEATURES}
    return pd.DataFrame([ordered_row], columns=CANONICAL_FEATURES)
