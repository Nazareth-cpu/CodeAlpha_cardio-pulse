"""
Unit tests for CardioPulse Model Loader.

Covers:
  1. model artifact loads successfully
  2. loaded object is a valid sklearn pipeline
  3. metadata loads successfully
  - caching / reuse behavior
  - error handling for missing and corrupted files
"""

from pathlib import Path
import unittest

from sklearn.pipeline import Pipeline

from ml.inference.exceptions import CorruptedModelError, ModelNotFoundError
from ml.inference.model_loader import (
    clear_cache,
    get_metadata,
    get_model,
    load_metadata,
    load_model,
)


class TestModelLoader(unittest.TestCase):
    """Test suite for model loading and in-memory caching."""

    def setUp(self):
        clear_cache()

    def tearDown(self):
        clear_cache()

    def test_01_model_artifact_loads_successfully(self):
        """1. model artifact loads successfully."""
        pipeline = load_model()
        self.assertIsNotNone(pipeline)

    def test_02_loaded_object_is_valid_sklearn_pipeline(self):
        """2. loaded object is a valid sklearn pipeline."""
        pipeline = load_model()
        self.assertIsInstance(pipeline, Pipeline)
        self.assertTrue(hasattr(pipeline, "predict"))
        self.assertTrue(hasattr(pipeline, "predict_proba"))
        self.assertIn("preprocessor", pipeline.named_steps)
        self.assertIn("model", pipeline.named_steps)

    def test_03_metadata_loads_successfully(self):
        """3. metadata loads successfully."""
        metadata = load_metadata()
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata.get("model_name"), "Logistic Regression")
        self.assertEqual(metadata.get("model_version"), "heart-disease-logistic-regression-v1")
        self.assertIn("metrics", metadata)

    def test_caching_reuses_same_instance(self):
        """Verify that get_model() returns cached singleton in memory without disk reloading."""
        m1 = get_model()
        m2 = get_model()
        self.assertIs(m1, m2, "get_model() must return the identical cached instance.")

        d1 = get_metadata()
        d2 = get_metadata()
        self.assertIs(d1, d2, "get_metadata() must return the identical cached dictionary.")

    def test_missing_model_file_raises_model_not_found(self):
        """Verify ModelNotFoundError on non-existent path."""
        fake_path = Path("/tmp/non_existent_cardiopulse_model.joblib")
        with self.assertRaises(ModelNotFoundError):
            load_model(model_path=fake_path, force_reload=True)

    def test_missing_metadata_file_raises_model_not_found(self):
        """Verify ModelNotFoundError on non-existent metadata path."""
        fake_path = Path("/tmp/non_existent_metadata.json")
        with self.assertRaises(ModelNotFoundError):
            load_metadata(metadata_path=fake_path, force_reload=True)


if __name__ == "__main__":
    unittest.main()
