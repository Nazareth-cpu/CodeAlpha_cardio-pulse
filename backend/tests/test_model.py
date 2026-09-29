"""
Unit tests for FastAPI Model Metadata Endpoint.

Covers:
  3. GET /api/v1/model succeeds
  4. Response contains model name
  5. Response contains model version
  6. Response contains evaluation metadata
  7. Response does not expose secrets or filesystem paths
"""

import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from backend.app.main import app


class TestModelEndpoint(unittest.TestCase):
    """Test suite for GET /api/v1/model."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_03_model_endpoint_succeeds(self):
        """3. GET /api/v1/model succeeds."""
        response = self.client.get("/api/v1/model")
        self.assertEqual(response.status_code, 200)

    def test_04_response_contains_model_name(self):
        """4. Response contains model name."""
        response = self.client.get("/api/v1/model")
        data = response.json()
        self.assertEqual(data.get("model_name"), "Logistic Regression")

    def test_05_response_contains_model_version(self):
        """5. Response contains model version."""
        response = self.client.get("/api/v1/model")
        data = response.json()
        self.assertEqual(data.get("model_version"), "heart-disease-logistic-regression-v1")

    def test_06_response_contains_evaluation_metadata(self):
        """6. Response contains evaluation metadata."""
        response = self.client.get("/api/v1/model")
        data = response.json()
        self.assertIn("metrics", data)
        metrics = data["metrics"]
        self.assertAlmostEqual(metrics.get("accuracy", 0), 0.8852, places=3)
        self.assertAlmostEqual(metrics.get("roc_auc", 0), 0.9665, places=3)
        self.assertIn("confusion_matrix", data)
        self.assertEqual(data["confusion_matrix"], {"TN": 28, "FP": 5, "FN": 2, "TP": 26})
        self.assertIn("disclaimer", data)

    def test_07_response_does_not_expose_secrets_or_filesystem_paths(self):
        """7. Response does not expose secrets or filesystem paths."""
        response = self.client.get("/api/v1/model")
        text = response.text.lower()

        # Check for absolute filesystem traces
        self.assertNotIn("/home/", text)
        self.assertNotIn("/app/applet", text)
        self.assertNotIn("/tmp/", text)
        self.assertNotIn("c:\\", text)

        # Check for credential strings
        self.assertNotIn("password", text)
        self.assertNotIn("secret", text)
        self.assertNotIn("token", text)


if __name__ == "__main__":
    unittest.main()
