"""
Unit tests for FastAPI Health Endpoint.

Covers:
  1. GET /api/v1/health returns expected status
  2. Health reports model availability
  20. Model unavailable produces safe error (503 Service Unavailable)
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import patch

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.prediction_service import prediction_service


class TestHealthEndpoint(unittest.TestCase):
    """Test suite for GET /api/v1/health."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_returns_expected_status(self):
        """1. GET /api/v1/health returns expected status."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "heart-disease-prediction-api")

    def test_02_health_reports_model_availability(self):
        """2. Health reports model availability."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("model_loaded", data)
        self.assertTrue(data["model_loaded"])
        self.assertEqual(data["model_name"], "Logistic Regression")
        self.assertEqual(data["model_version"], "heart-disease-logistic-regression-v1")

    def test_20_model_unavailable_produces_safe_degraded_response(self):
        """20. Model unavailable produces safe error (503 status code and degraded status)."""
        with patch.object(prediction_service, "is_model_available", return_value=False):
            response = self.client.get("/api/v1/health")
            self.assertEqual(response.status_code, 503)
            data = response.json()
            self.assertEqual(data["status"], "degraded")
            self.assertFalse(data["model_loaded"])


if __name__ == "__main__":
    unittest.main()
