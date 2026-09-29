"""
Unit and integration tests for FastAPI Prediction Endpoints.

Covers:
  8. POST /api/v1/predictions with valid input succeeds
  9. Response contains prediction
  10. Response contains probability
  11. Response contains model_name
  12. Response contains model_version
  13. Missing field rejected
  14. Invalid categorical value rejected
  15. Invalid numerical value rejected
  16. Unknown field rejected
  17. 'num' rejected
  18. 'target' rejected
  19. 'id' rejected
  21. Internal inference failure does not expose stack trace
  22. Configured frontend origin is accepted
  23. Arbitrary production origins are not automatically allowed
  - Dataset independence during prediction
"""

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from backend.app.dependencies.auth import AuthenticatedUser, get_current_user
from backend.app.main import app
from backend.app.services.prediction_service import prediction_service
from ml.config import DATASET_PATH
from ml.inference.exceptions import PredictionError


class TestPredictionsEndpoint(unittest.TestCase):
    """Test suite for POST /api/v1/predictions."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Default override for predictions integration tests
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
            uid="test_verified_user_123",
            email="test_user@example.com",
            email_verified=True,
            name="Test User",
        )
        cls.valid_payload = {
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

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def test_unauthenticated_request_rejected(self):
        """Unauthenticated request without dependency override returns 401."""
        app.dependency_overrides.clear()
        try:
            response = self.client.post("/api/v1/predictions", json=self.valid_payload)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json(), {"detail": "Authentication required."})
        finally:
            app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
                uid="test_verified_user_123",
                email="test_user@example.com",
                email_verified=True,
                name="Test User",
            )

    # 8-12. Valid prediction tests
    def test_08_prediction_with_valid_input_succeeds(self):
        """8. POST /api/v1/predictions with valid input succeeds."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)

    def test_09_response_contains_prediction(self):
        """9. Response contains prediction (0 or 1)."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        data = response.json()
        self.assertIn("prediction", data)
        self.assertIn(data["prediction"], [0, 1])

    def test_10_response_contains_probability(self):
        """10. Response contains probability between 0 and 1."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        data = response.json()
        self.assertIn("probability", data)
        self.assertIsInstance(data["probability"], float)
        self.assertGreaterEqual(data["probability"], 0.0)
        self.assertLessEqual(data["probability"], 1.0)

    def test_11_response_contains_model_name(self):
        """11. Response contains model_name."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        data = response.json()
        self.assertEqual(data.get("model_name"), "Logistic Regression")

    def test_12_response_contains_model_version(self):
        """12. Response contains model_version."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        data = response.json()
        self.assertEqual(data.get("model_version"), "heart-disease-logistic-regression-v1")
        self.assertIn("disclaimer", data)

    # 13-19. Validation rejection tests
    def test_13_missing_field_rejected(self):
        """13. Missing field rejected (422 Unprocessable Entity)."""
        bad_payload = dict(self.valid_payload)
        del bad_payload["age"]
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    def test_14_invalid_categorical_value_rejected(self):
        """14. Invalid categorical value rejected (e.g. sex=5, cp=9)."""
        bad_payload = dict(self.valid_payload)
        bad_payload["sex"] = 5.0
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    def test_15_invalid_numerical_value_rejected(self):
        """15. Invalid numerical value rejected (e.g. non-numeric string)."""
        bad_payload = dict(self.valid_payload)
        bad_payload["chol"] = "extremely_high"
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    def test_16_unknown_field_rejected(self):
        """16. Unknown field rejected."""
        bad_payload = dict(self.valid_payload)
        bad_payload["body_mass_index"] = 24.2
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    def test_17_num_rejected(self):
        """17. 'num' rejected (target leakage prevention)."""
        bad_payload = dict(self.valid_payload)
        bad_payload["num"] = 1.0
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    def test_18_target_rejected(self):
        """18. 'target' rejected (target leakage prevention)."""
        bad_payload = dict(self.valid_payload)
        bad_payload["target"] = 1.0
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    def test_19_id_rejected(self):
        """19. 'id' rejected."""
        bad_payload = dict(self.valid_payload)
        bad_payload["id"] = "patient_001"
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    # 21. Error handling without stack trace leak
    def test_21_internal_inference_failure_does_not_expose_stack_trace(self):
        """21. Internal inference failure produces safe 500 error without exposing stack trace."""
        with patch.object(prediction_service, "predict", side_effect=PredictionError("Internal failure")):
            response = self.client.post("/api/v1/predictions", json=self.valid_payload)
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn("detail", data)
            # Ensure no traceback or internal path is in response text
            self.assertNotIn("Traceback", response.text)
            self.assertNotIn(".py", response.text)
            self.assertNotIn("/app/", response.text)

    # 22-23. CORS origin testing
    def test_22_configured_frontend_origin_is_accepted(self):
        """22. Configured frontend origin is accepted in CORS headers."""
        response = self.client.options(
            "/api/v1/predictions",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://localhost:5173",
        )

    def test_22b_cloud_run_preview_origin_is_accepted(self):
        """22b. Cloud Run preview origin is accepted in CORS headers with Authorization header."""
        cloud_run_origin = "https://ais-dev-uu3lw37htk375vcjewppls-93479644791.asia-southeast1.run.app"
        response = self.client.options(
            "/api/v1/predictions",
            headers={
                "Origin": cloud_run_origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization,Content-Type",
            },
        )
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            cloud_run_origin,
        )
        self.assertEqual(
            response.headers.get("access-control-allow-credentials"),
            "true",
        )
        allow_headers = response.headers.get("access-control-allow-headers", "").lower()
        self.assertTrue("authorization" in allow_headers or "*" in allow_headers)

    def test_23_arbitrary_production_origins_are_not_automatically_allowed(self):
        """23. Arbitrary production origins not in configured list are not allowed."""
        response = self.client.options(
            "/api/v1/predictions",
            headers={
                "Origin": "https://malicious-external-site.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertNotEqual(
            response.headers.get("access-control-allow-origin"),
            "https://malicious-external-site.com",
        )

    # Dataset independence test
    def test_dataset_independent_prediction(self):
        """Verify POST /api/v1/predictions does not require dataset.csv."""
        temp_renamed = False
        backup_path = DATASET_PATH.parent / "dataset.csv.test_bak"
        try:
            if DATASET_PATH.exists():
                DATASET_PATH.rename(backup_path)
                temp_renamed = True

            self.assertFalse(DATASET_PATH.exists())
            response = self.client.post("/api/v1/predictions", json=self.valid_payload)
            self.assertEqual(response.status_code, 200)
            self.assertIn("probability", response.json())
        finally:
            if temp_renamed and backup_path.exists():
                backup_path.rename(DATASET_PATH)


if __name__ == "__main__":
    unittest.main()
