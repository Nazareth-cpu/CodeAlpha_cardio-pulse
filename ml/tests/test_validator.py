"""
Unit tests for CardioPulse Input Validator.

Covers:
  4. valid input passes validation
  9-21: missing fields rejected (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal)
  22-29: invalid categorical input rejected (sex, cp, fbs, restecg, exang, slope, ca, thal)
  30-34: invalid numerical input rejected (non-numeric age, non-numeric chol, NaN, infinity, null)
  35-37: forbidden fields rejected (num, target, id)
  38: arbitrary unknown field rejected
"""

import unittest

from ml.inference.exceptions import (
    ForbiddenFieldError,
    InvalidCategoricalError,
    InvalidNumericalError,
    MissingFieldError,
    UnknownFieldError,
)
from ml.inference.validator import build_dataframe, validate_input


class TestValidator(unittest.TestCase):
    """Test suite for input schema validation and domain verification."""

    @classmethod
    def setUpClass(cls):
        # Canonical valid test record
        cls.valid_record = {
            "age": 52.0,
            "sex": 1.0,
            "cp": 4.0,
            "trestbps": 138.0,
            "chol": 246.0,
            "fbs": 0.0,
            "restecg": 0.0,
            "thalach": 150.0,
            "exang": 0.0,
            "oldpeak": 1.2,
            "slope": 2.0,
            "ca": 0.0,
            "thal": 3.0,
        }

    # 4. Valid input
    def test_04_valid_input_passes_validation(self):
        """4. valid input passes validation."""
        result = validate_input(self.valid_record)
        self.assertEqual(len(result), 13)
        self.assertEqual(result["age"], 52.0)
        self.assertEqual(result["sex"], 1.0)
        self.assertEqual(result["thal"], 3.0)

    # 9-21. Missing fields
    def test_09_missing_age_rejected(self):
        """9. missing age rejected."""
        data = dict(self.valid_record)
        del data["age"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_10_missing_sex_rejected(self):
        """10. missing sex rejected."""
        data = dict(self.valid_record)
        del data["sex"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_11_missing_cp_rejected(self):
        """11. missing cp rejected."""
        data = dict(self.valid_record)
        del data["cp"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_12_missing_trestbps_rejected(self):
        """12. missing trestbps rejected."""
        data = dict(self.valid_record)
        del data["trestbps"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_13_missing_chol_rejected(self):
        """13. missing chol rejected."""
        data = dict(self.valid_record)
        del data["chol"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_14_missing_fbs_rejected(self):
        """14. missing fbs rejected."""
        data = dict(self.valid_record)
        del data["fbs"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_15_missing_restecg_rejected(self):
        """15. missing restecg rejected."""
        data = dict(self.valid_record)
        del data["restecg"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_16_missing_thalach_rejected(self):
        """16. missing thalach rejected."""
        data = dict(self.valid_record)
        del data["thalach"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_17_missing_exang_rejected(self):
        """17. missing exang rejected."""
        data = dict(self.valid_record)
        del data["exang"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_18_missing_oldpeak_rejected(self):
        """18. missing oldpeak rejected."""
        data = dict(self.valid_record)
        del data["oldpeak"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_19_missing_slope_rejected(self):
        """19. missing slope rejected."""
        data = dict(self.valid_record)
        del data["slope"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_20_missing_ca_rejected(self):
        """20. missing ca rejected."""
        data = dict(self.valid_record)
        del data["ca"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    def test_21_missing_thal_rejected(self):
        """21. missing thal rejected."""
        data = dict(self.valid_record)
        del data["thal"]
        with self.assertRaises(MissingFieldError):
            validate_input(data)

    # 22-29. Invalid categorical input
    def test_22_invalid_sex_rejected(self):
        """22. invalid sex rejected."""
        data = dict(self.valid_record)
        data["sex"] = 2.0  # Allowed: {0, 1}
        with self.assertRaises(InvalidCategoricalError):
            validate_input(data)

    def test_23_invalid_cp_rejected(self):
        """23. invalid cp rejected."""
        data = dict(self.valid_record)
        data["cp"] = 5.0  # Allowed: {1, 2, 3, 4}
        with self.assertRaises(InvalidCategoricalError):
            validate_input(data)

    def test_24_invalid_fbs_rejected(self):
        """24. invalid fbs rejected."""
        data = dict(self.valid_record)
        data["fbs"] = 3.0  # Allowed: {0, 1}
        with self.assertRaises(InvalidCategoricalError):
            validate_input(data)

    def test_25_invalid_restecg_rejected(self):
        """25. invalid restecg rejected."""
        data = dict(self.valid_record)
        data["restecg"] = 4.0  # Allowed: {0, 1, 2}
        with self.assertRaises(InvalidCategoricalError):
            validate_input(data)

    def test_26_invalid_exang_rejected(self):
        """26. invalid exang rejected."""
        data = dict(self.valid_record)
        data["exang"] = -1.0  # Allowed: {0, 1}
        with self.assertRaises(InvalidCategoricalError):
            validate_input(data)

    def test_27_invalid_slope_rejected(self):
        """27. invalid slope rejected."""
        data = dict(self.valid_record)
        data["slope"] = 0.0  # Allowed: {1, 2, 3}
        with self.assertRaises(InvalidCategoricalError):
            validate_input(data)

    def test_28_invalid_ca_rejected(self):
        """28. invalid ca rejected."""
        data = dict(self.valid_record)
        data["ca"] = 5.0  # Allowed: {0, 1, 2, 3}
        with self.assertRaises(InvalidCategoricalError):
            validate_input(data)

    def test_29_invalid_thal_rejected(self):
        """29. invalid thal rejected."""
        data = dict(self.valid_record)
        data["thal"] = 4.0  # Allowed: {3, 6, 7}
        with self.assertRaises(InvalidCategoricalError):
            validate_input(data)

    # 30-34. Invalid numerical input
    def test_30_non_numeric_age_rejected(self):
        """30. non-numeric age rejected."""
        data = dict(self.valid_record)
        data["age"] = "fifty-two"
        with self.assertRaises(InvalidNumericalError):
            validate_input(data)

    def test_31_non_numeric_cholesterol_rejected(self):
        """31. non-numeric cholesterol rejected."""
        data = dict(self.valid_record)
        data["chol"] = "high"
        with self.assertRaises(InvalidNumericalError):
            validate_input(data)

    def test_32_nan_rejected(self):
        """32. NaN rejected."""
        data = dict(self.valid_record)
        data["trestbps"] = float("nan")
        with self.assertRaises(InvalidNumericalError):
            validate_input(data)

    def test_33_infinity_rejected(self):
        """33. infinity rejected."""
        data = dict(self.valid_record)
        data["thalach"] = float("inf")
        with self.assertRaises(InvalidNumericalError):
            validate_input(data)

    def test_34_null_numerical_field_rejected(self):
        """34. null numerical field rejected."""
        data = dict(self.valid_record)
        data["oldpeak"] = None
        with self.assertRaises(InvalidNumericalError):
            validate_input(data)

    # 35-37. Forbidden fields
    def test_35_num_rejected(self):
        """35. num rejected."""
        data = dict(self.valid_record)
        data["num"] = 1.0
        with self.assertRaises(ForbiddenFieldError):
            validate_input(data)

    def test_36_target_rejected(self):
        """36. target rejected."""
        data = dict(self.valid_record)
        data["target"] = 1.0
        with self.assertRaises(ForbiddenFieldError):
            validate_input(data)

    def test_37_id_rejected(self):
        """37. id rejected."""
        data = dict(self.valid_record)
        data["id"] = "patient_123"
        with self.assertRaises(ForbiddenFieldError):
            validate_input(data)

    # 38. Unknown fields
    def test_38_arbitrary_unknown_field_rejected(self):
        """38. arbitrary unknown field rejected."""
        data = dict(self.valid_record)
        data["bmi"] = 24.5
        with self.assertRaises(UnknownFieldError):
            validate_input(data)

    # DataFrame formatting
    def test_build_dataframe_canonical_columns(self):
        """Verify build_dataframe creates DataFrame matching exact canonical feature order."""
        validated = validate_input(self.valid_record)
        df = build_dataframe(validated)
        from ml.config import CANONICAL_FEATURES
        self.assertEqual(list(df.columns), CANONICAL_FEATURES)
        self.assertEqual(df.shape, (1, 13))


if __name__ == "__main__":
    unittest.main()
