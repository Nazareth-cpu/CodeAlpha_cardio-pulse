"""
Comprehensive Test Suite for CardioPulse Production ML Artifact.

Verifies:
  1. model.joblib exists and is loadable
  2. Loaded object is a valid sklearn Pipeline
  3. Pipeline contains fitted ColumnTransformer and LogisticRegression
  4. Feature schema aligns with canonical 13 features
  5. Leakage prevention: 'num', 'target', 'id' are rejected
  6. Pipeline accepts valid single input record
  7. Pipeline produces prediction (0 or 1)
  8. Pipeline produces probability within [0.0, 1.0]
  9. Artifact operates independently without dataset.csv
 10. Model metadata file exists and matches reference project evaluation metrics
"""

import json
import unittest
from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from ml.config import (
    CANONICAL_FEATURES,
    CATEGORICAL_FEATURES,
    METADATA_PATH,
    MODEL_PATH,
    NUMERICAL_FEATURES,
    PRODUCTION_MODEL_NAME,
    PRODUCTION_MODEL_VERSION,
)
from ml.inference.predictor import (
    HeartDiseasePredictor,
    InvalidFeatureInputError,
    ModelArtifactNotFoundError,
)


class TestProductionMLArtifact(unittest.TestCase):
    """Unit and integration test cases for production model artifact."""

    @classmethod
    def setUpClass(cls):
        """Ensure paths and load predictor instance for tests."""
        cls.model_path = MODEL_PATH
        cls.metadata_path = METADATA_PATH

        # Sample valid clinical record (deterministic representative input)
        cls.valid_sample_record = {
            "age": 63.0,
            "sex": 1.0,
            "cp": 1.0,
            "trestbps": 145.0,
            "chol": 233.0,
            "fbs": 1.0,
            "restecg": 2.0,
            "thalach": 150.0,
            "exang": 0.0,
            "oldpeak": 2.3,
            "slope": 3.0,
            "ca": 0.0,
            "thal": 6.0,
        }

        # Elevated risk clinical record
        cls.elevated_risk_record = {
            "age": 67.0,
            "sex": 1.0,
            "cp": 4.0,
            "trestbps": 160.0,
            "chol": 286.0,
            "fbs": 0.0,
            "restecg": 2.0,
            "thalach": 108.0,
            "exang": 1.0,
            "oldpeak": 1.5,
            "slope": 2.0,
            "ca": 3.0,
            "thal": 3.0,
        }

    def test_01_artifact_exists_on_disk(self):
        """Assert that model.joblib exists in the expected artifact location."""
        self.assertTrue(
            self.model_path.exists(),
            f"Production model artifact not found at {self.model_path}",
        )

    def test_02_metadata_exists_on_disk(self):
        """Assert that model_metadata.json exists in the expected location."""
        self.assertTrue(
            self.metadata_path.exists(),
            f"Production metadata file not found at {self.metadata_path}",
        )

    def test_03_load_pipeline_structure(self):
        """Assert that loaded artifact is a scikit-learn Pipeline with preprocessor and model."""
        pipeline = joblib.load(self.model_path)
        self.assertIsInstance(pipeline, Pipeline, "Loaded artifact is not a Pipeline instance.")
        self.assertIn("preprocessor", pipeline.named_steps, "Pipeline missing 'preprocessor' step.")
        self.assertIn("model", pipeline.named_steps, "Pipeline missing 'model' step.")

        self.assertIsInstance(
            pipeline.named_steps["preprocessor"],
            ColumnTransformer,
            "Preprocessor step must be a ColumnTransformer.",
        )
        self.assertIsInstance(
            pipeline.named_steps["model"],
            LogisticRegression,
            "Model step must be a LogisticRegression estimator.",
        )

    def test_04_feature_schema_definition(self):
        """Verify feature schema contains exactly 13 canonical features."""
        self.assertEqual(len(CANONICAL_FEATURES), 13)
        self.assertEqual(len(NUMERICAL_FEATURES), 5)
        self.assertEqual(len(CATEGORICAL_FEATURES), 8)
        self.assertNotIn("num", CANONICAL_FEATURES)
        self.assertNotIn("target", CANONICAL_FEATURES)
        self.assertNotIn("id", CANONICAL_FEATURES)

    def test_05_metadata_contents_and_metrics(self):
        """Verify model_metadata.json contains exact evaluation metrics from baseline."""
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        self.assertEqual(metadata["model_name"], PRODUCTION_MODEL_NAME)
        self.assertEqual(metadata["model_version"], PRODUCTION_MODEL_VERSION)
        self.assertEqual(metadata["selection_criterion"], "ROC-AUC")
        self.assertEqual(metadata["random_state"], 42)
        self.assertEqual(metadata["test_size"], 0.20)

        # Assert reference metrics match existing benchmark
        metrics = metadata["metrics"]
        self.assertAlmostEqual(metrics["accuracy"], 0.8852, places=4)
        self.assertAlmostEqual(metrics["precision"], 0.8387, places=4)
        self.assertAlmostEqual(metrics["recall"], 0.9286, places=4)
        self.assertAlmostEqual(metrics["f1_score"], 0.8814, places=4)
        self.assertAlmostEqual(metrics["roc_auc"], 0.9665, places=4)

        # Assert confusion matrix matches
        cm = metadata["confusion_matrix"]
        self.assertEqual(cm["TN"], 28)
        self.assertEqual(cm["FP"], 5)
        self.assertEqual(cm["FN"], 2)
        self.assertEqual(cm["TP"], 26)

        # Assert educational disclaimer is present
        self.assertIn("educational and research purposes", metadata["disclaimer"].lower())

    def test_06_target_leakage_rejection(self):
        """Verify that predictor rejects payloads with 'num', 'target', or 'id'."""
        predictor = HeartDiseasePredictor(self.model_path, self.metadata_path)

        for prohibited_key in ["num", "target", "id"]:
            tampered_payload = dict(self.valid_sample_record)
            tampered_payload[prohibited_key] = 1.0
            with self.assertRaises(InvalidFeatureInputError):
                predictor.predict(tampered_payload)

    def test_07_missing_feature_rejection(self):
        """Verify that predictor rejects payloads with missing canonical features."""
        predictor = HeartDiseasePredictor(self.model_path, self.metadata_path)
        incomplete_payload = dict(self.valid_sample_record)
        del incomplete_payload["chol"]
        with self.assertRaises(InvalidFeatureInputError):
            predictor.predict(incomplete_payload)

    def test_08_single_record_prediction_output(self):
        """Verify structured output of predict() for valid record."""
        predictor = HeartDiseasePredictor(self.model_path, self.metadata_path)
        result = predictor.predict(self.valid_sample_record)

        self.assertIn("prediction", result)
        self.assertIn("probability", result)
        self.assertIn("model_name", result)
        self.assertIn("model_version", result)
        self.assertIn("disclaimer", result)

        self.assertIn(result["prediction"], [0, 1])
        self.assertGreaterEqual(result["probability"], 0.0)
        self.assertLessEqual(result["probability"], 1.0)
        self.assertEqual(result["model_name"], PRODUCTION_MODEL_NAME)
        self.assertEqual(result["model_version"], PRODUCTION_MODEL_VERSION)

    def test_09_elevated_risk_inference(self):
        """Verify inference on elevated risk clinical profile."""
        predictor = HeartDiseasePredictor(self.model_path, self.metadata_path)
        result = predictor.predict(self.elevated_risk_record)

        self.assertIn(result["prediction"], [0, 1])
        self.assertGreaterEqual(result["probability"], 0.0)
        self.assertLessEqual(result["probability"], 1.0)

    def test_10_missing_artifact_error_handling(self):
        """Verify descriptive error when artifact path does not exist."""
        non_existent_path = Path("/tmp/does_not_exist_model.joblib")
        with self.assertRaises(ModelArtifactNotFoundError):
            HeartDiseasePredictor(model_path=non_existent_path, metadata_path=self.metadata_path)

    def test_11_operates_without_dataset_csv(self):
        """Verify that inference operates without dataset.csv being loaded or present."""
        # Instantiate a fresh predictor pointing only to serialized artifacts
        predictor = HeartDiseasePredictor(model_path=self.model_path, metadata_path=self.metadata_path)
        # Execute prediction on valid input
        result = predictor.predict(self.valid_sample_record)
        self.assertIn("prediction", result)
        self.assertIn("probability", result)
        self.assertIsInstance(result["probability"], float)

    def test_12_inference_does_not_retrain_model(self):
        """Verify that inference does not fit or modify the pipeline."""
        pipeline = joblib.load(self.model_path)
        # Record preprocessor and model state
        initial_coef = pipeline.named_steps["model"].coef_.copy()
        initial_intercept = pipeline.named_steps["model"].intercept_.copy()

        # Run inference through predictor
        predictor = HeartDiseasePredictor(model_path=self.model_path, metadata_path=self.metadata_path)
        predictor.predict(self.valid_sample_record)

        # Confirm model parameters have not changed
        current_coef = predictor._pipeline.named_steps["model"].coef_
        current_intercept = predictor._pipeline.named_steps["model"].intercept_

        import numpy as np
        np.testing.assert_array_equal(initial_coef, current_coef)
        np.testing.assert_array_equal(initial_intercept, current_intercept)


if __name__ == "__main__":
    unittest.main()
