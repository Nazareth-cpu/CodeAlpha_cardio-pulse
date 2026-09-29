"""
Unit tests for CardioPulse Predictor.

Covers:
  5. valid input produces prediction
  6. valid input produces probability
  7. prediction is 0 or 1
  8. probability is between 0 and 1
  39. repeated prediction with identical input is deterministic
  40. inference does not retrain the model
  41. inference does not require dataset.csv
  42. inference does not regenerate plots
  - PredictionResult structure and to_dict()
  - Metadata retrieval via get_model_metadata()
"""

import os
from pathlib import Path
import tempfile
import unittest

import numpy as np

from ml.config import DATASET_PATH, OUTPUT_DIR
from ml.inference.predictor import (
    HeartDiseasePredictor,
    PredictionResult,
    get_model_metadata,
    get_predictor,
    predict,
)


class TestPredictor(unittest.TestCase):
    """Test suite for standalone inference execution and model behavior."""

    @classmethod
    def setUpClass(cls):
        # Valid test record (same as test_validator)
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

    def test_05_valid_input_produces_prediction(self):
        """5. valid input produces prediction."""
        result = predict(self.valid_record)
        self.assertIsInstance(result, PredictionResult)
        self.assertIsNotNone(result.prediction)

    def test_06_valid_input_produces_probability(self):
        """6. valid input produces probability."""
        result = predict(self.valid_record)
        self.assertIsInstance(result.probability, float)

    def test_07_prediction_is_0_or_1(self):
        """7. prediction is 0 or 1."""
        result = predict(self.valid_record)
        self.assertIn(result.prediction, [0, 1])

    def test_08_probability_is_between_0_and_1(self):
        """8. probability is between 0 and 1."""
        result = predict(self.valid_record)
        self.assertGreaterEqual(result.probability, 0.0)
        self.assertLessEqual(result.probability, 1.0)

    def test_39_repeated_prediction_is_deterministic(self):
        """39. repeated prediction with identical input is deterministic."""
        r1 = predict(self.valid_record)
        r2 = predict(self.valid_record)
        r3 = predict(self.valid_record)

        self.assertEqual(r1.prediction, r2.prediction)
        self.assertEqual(r2.prediction, r3.prediction)
        self.assertAlmostEqual(r1.probability, r2.probability, places=6)
        self.assertAlmostEqual(r2.probability, r3.probability, places=6)

    def test_40_inference_does_not_retrain_model(self):
        """40. inference does not retrain the model."""
        predictor = get_predictor()
        model = predictor._pipeline.named_steps["model"]

        # Record model coefficients and intercept before inference
        coef_before = model.coef_.copy()
        intercept_before = model.intercept_.copy()

        # Run multiple inference passes
        for _ in range(5):
            predictor.predict(self.valid_record)

        coef_after = model.coef_
        intercept_after = model.intercept_

        np.testing.assert_array_equal(coef_before, coef_after)
        np.testing.assert_array_equal(intercept_before, intercept_after)

    def test_41_inference_does_not_require_dataset_csv(self):
        """41. inference does not require dataset.csv."""
        # Point ML_DATASET_PATH to a non-existent file
        original_env = os.environ.get("ML_DATASET_PATH")
        try:
            os.environ["ML_DATASET_PATH"] = "/tmp/completely_non_existent_dataset.csv"
            # Instantiate a fresh predictor and execute inference
            fresh_predictor = HeartDiseasePredictor()
            result = fresh_predictor.predict(self.valid_record)
            self.assertIn(result.prediction, [0, 1])
            self.assertGreaterEqual(result.probability, 0.0)
        finally:
            if original_env is not None:
                os.environ["ML_DATASET_PATH"] = original_env
            else:
                os.environ.pop("ML_DATASET_PATH", None)

    def test_42_inference_does_not_regenerate_plots(self):
        """42. inference does not regenerate plots."""
        # Record mtimes of output plots if they exist
        mtimes_before = {}
        plot_names = ["roc_curves.png", "confusion_matrices.png", "feature_importance.png"]
        for p in plot_names:
            file_path = OUTPUT_DIR / p
            if file_path.exists():
                mtimes_before[p] = file_path.stat().st_mtime

        # Run inference
        predict(self.valid_record)

        # Check mtimes have not changed
        for p, original_mtime in mtimes_before.items():
            file_path = OUTPUT_DIR / p
            self.assertEqual(
                file_path.stat().st_mtime,
                original_mtime,
                f"File {p} was modified during inference!",
            )

    def test_response_structure_and_serialization(self):
        """Verify PredictionResult attributes and to_dict() serialization."""
        result = predict(self.valid_record)
        res_dict = result.to_dict()

        expected_keys = {"prediction", "probability", "model_name", "model_version", "disclaimer"}
        self.assertEqual(set(res_dict.keys()), expected_keys)
        self.assertEqual(res_dict["model_name"], "Logistic Regression")
        self.assertEqual(res_dict["model_version"], "heart-disease-logistic-regression-v1")
        self.assertIn("educational and research purposes", res_dict["disclaimer"].lower())

    def test_get_model_metadata(self):
        """Verify model metadata retrieval interface."""
        metadata = get_model_metadata()
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata["model_name"], "Logistic Regression")
        self.assertIn("features", metadata)
        self.assertIn("metrics", metadata)
        self.assertIn("disclaimer", metadata)


if __name__ == "__main__":
    unittest.main()
