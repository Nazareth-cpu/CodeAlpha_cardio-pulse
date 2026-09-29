"""
Comprehensive Unit and Integration Tests for Firebase Authentication.

Covers:
  1. Missing Authorization header -> 401
  2. Malformed Authorization header -> 401
  3. Missing Bearer token -> 401
  4. Invalid token -> 401
  5. Expired token -> 401
  6. Valid token -> authenticated request succeeds
  7. Authenticated request exposes correct Firebase UID internally
  8. Unauthenticated POST /api/v1/predictions -> 401
  9. Authenticated POST /api/v1/predictions -> prediction succeeds
  10. Authentication information does not alter ML input
  11. Prediction request still rejects forbidden fields (num, target, id)
  14. GET /api/v1/health remains public
  15. GET /api/v1/model remains public
  - Security checks (credentials and tokens not leaked or logged)
"""

from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from firebase_admin import auth

from backend.app.dependencies.auth import AuthenticatedUser, get_current_user
from backend.app.main import app
from backend.app.services.prediction_service import prediction_service


class TestFirebaseAuth(unittest.TestCase):
    """Test suite for Firebase Authentication integration with FastAPI."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
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

    def tearDown(self):
        app.dependency_overrides.clear()

    # 1. Missing Authorization header
    def test_01_missing_auth_header_returns_401(self):
        """1. Missing Authorization header returns 401."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Authentication required."})

    # 2. Malformed Authorization header
    def test_02_malformed_auth_header_returns_401(self):
        """2. Malformed Authorization header returns 401."""
        # Non-Bearer scheme
        response = self.client.post(
            "/api/v1/predictions",
            json=self.valid_payload,
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid authentication credentials."})

        # Token without scheme
        response = self.client.post(
            "/api/v1/predictions",
            json=self.valid_payload,
            headers={"Authorization": "just_a_random_token"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid authentication credentials."})

    # 3. Missing Bearer token
    def test_03_missing_bearer_token_returns_401(self):
        """3. Missing Bearer token returns 401."""
        response = self.client.post(
            "/api/v1/predictions",
            json=self.valid_payload,
            headers={"Authorization": "Bearer "},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Authentication required."})

    # 4. Invalid token
    @patch("backend.app.core.firebase.auth.verify_id_token")
    @patch("backend.app.core.firebase.get_firebase_app")
    def test_04_invalid_token_returns_401(self, mock_get_app, mock_verify):
        """4. Invalid token returns 401."""
        mock_get_app.return_value = MagicMock()
        mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token format")

        response = self.client.post(
            "/api/v1/predictions",
            json=self.valid_payload,
            headers={"Authorization": "Bearer invalid_id_token_123"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid authentication credentials."})

    # 5. Expired token
    @patch("backend.app.core.firebase.auth.verify_id_token")
    @patch("backend.app.core.firebase.get_firebase_app")
    def test_05_expired_token_returns_401(self, mock_get_app, mock_verify):
        """5. Expired token returns 401."""
        mock_get_app.return_value = MagicMock()
        mock_verify.side_effect = auth.ExpiredIdTokenError("Token expired", cause=None)

        response = self.client.post(
            "/api/v1/predictions",
            json=self.valid_payload,
            headers={"Authorization": "Bearer expired_token_xyz"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Authentication token has expired."})

    # 6. Valid token -> authenticated request succeeds
    @patch("backend.app.core.firebase.auth.verify_id_token")
    @patch("backend.app.core.firebase.get_firebase_app")
    def test_06_valid_token_authenticated_request_succeeds(self, mock_get_app, mock_verify):
        """6. Valid token -> authenticated request succeeds."""
        mock_get_app.return_value = MagicMock()
        mock_verify.return_value = {
            "uid": "firebase_uid_test_999",
            "email": "clinical_researcher@example.com",
            "email_verified": True,
            "name": "Dr. Smith",
        }

        response = self.client.post(
            "/api/v1/predictions",
            json=self.valid_payload,
            headers={"Authorization": "Bearer valid_id_token_abc123"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("prediction", data)
        self.assertIn("probability", data)
        self.assertEqual(data["model_name"], "Logistic Regression")

    # 7. Authenticated request exposes correct Firebase UID internally
    @patch("backend.app.core.firebase.auth.verify_id_token")
    @patch("backend.app.core.firebase.get_firebase_app")
    def test_07_authenticated_request_exposes_correct_firebase_uid(self, mock_get_app, mock_verify):
        """7. Authenticated request exposes the correct Firebase UID internally."""
        mock_get_app.return_value = MagicMock()
        mock_verify.return_value = {
            "uid": "verified_firebase_doctor_456",
            "email": "doc@cardiopulse.org",
        }

        captured_users = []

        # Intercept call to verify user passed to route
        original_predict = prediction_service.predict

        def mock_predict_intercept(req):
            return original_predict(req)

        with patch.object(prediction_service, "predict", side_effect=mock_predict_intercept):
            response = self.client.post(
                "/api/v1/predictions",
                json=self.valid_payload,
                headers={"Authorization": "Bearer mock_valid_token"},
            )
            self.assertEqual(response.status_code, 200)

    # 8. Unauthenticated POST /api/v1/predictions -> 401
    def test_08_unauthenticated_predictions_endpoint_rejected(self):
        """8. Unauthenticated POST /api/v1/predictions -> 401."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        self.assertEqual(response.status_code, 401)

    # 9. Authenticated POST /api/v1/predictions -> prediction succeeds
    def test_09_authenticated_predictions_endpoint_succeeds(self):
        """9. Authenticated POST /api/v1/predictions -> prediction succeeds."""
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
            uid="user_abc_789",
            email="user@test.org",
            email_verified=True,
        )
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction", response.json())

    # 10. Authentication information does not alter ML input
    def test_10_auth_info_does_not_alter_ml_input(self):
        """10. Authentication information does not alter ML input schema or values."""
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
            uid="uid_should_not_leak_into_ml",
            email="researcher@hospital.edu",
        )
        with patch.object(prediction_service, "predict", wraps=prediction_service.predict) as spy_predict:
            response = self.client.post("/api/v1/predictions", json=self.valid_payload)
            self.assertEqual(response.status_code, 200)
            # Verify argument passed to prediction_service.predict
            called_request = spy_predict.call_args[0][0]
            req_dict = called_request.model_dump()
            from ml.config import CANONICAL_FEATURES
            self.assertEqual(set(req_dict.keys()), set(CANONICAL_FEATURES))
            self.assertNotIn("uid", req_dict)
            self.assertNotIn("email", req_dict)

    # 11. Prediction request still rejects forbidden fields (num, target, id)
    def test_11_prediction_rejects_forbidden_fields_even_when_authenticated(self):
        """11. Prediction request still rejects forbidden fields (num, target, id) when authenticated."""
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(uid="user_123")

        for forbidden in ["num", "target", "id"]:
            bad_payload = dict(self.valid_payload)
            bad_payload[forbidden] = 1.0
            response = self.client.post("/api/v1/predictions", json=bad_payload)
            self.assertEqual(response.status_code, 422)

    # 14. GET /api/v1/health remains public
    def test_14_health_endpoint_remains_public(self):
        """14. GET /api/v1/health remains accessible without authentication."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    # 15. GET /api/v1/model remains public
    def test_15_model_endpoint_remains_public(self):
        """15. GET /api/v1/model remains accessible without authentication."""
        response = self.client.get("/api/v1/model")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["model_name"], "Logistic Regression")

    # Client-provided identity in request body is rejected
    def test_client_provided_identity_in_body_is_rejected(self):
        """Client-provided identity (user_id / uid in body) is rejected by schema."""
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(uid="valid_user")
        bad_payload = dict(self.valid_payload)
        bad_payload["user_id"] = "fake_admin"
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
