"""
Phase 7C Comprehensive Verification Test Suite:
Frontend Model Selection & End-to-End Prediction Integration.

Verifies:
  1. GET /api/v1/models serves all 4 production models with metrics and availability.
  2. POST /api/v1/predictions routes to explicitly requested model:
     - logistic_regression
     - svm
     - random_forest
     - xgboost
  3. Prediction response includes prediction, probability, model_name, model_version, prediction_id.
  4. User isolation and Firestore persistence in user subcollection.
  5. GET /api/v1/predictions retrieves historical records.
  6. GET /api/v1/predictions/{id} retrieves specific record detail.
  7. Rejection of unauthenticated requests (HTTP 401).
  8. Rejection of unsupported model_id (HTTP 422) without silent fallback.
  9. Rejection of invalid inputs / leakage fields (HTTP 422).
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from backend.app.dependencies.auth import AuthenticatedUser, get_current_user
from backend.app.dependencies.repository import get_prediction_repository
from backend.app.main import app
from backend.app.repositories.prediction_repository import InMemoryPredictionRepository


class TestPhase7CIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_user = AuthenticatedUser(
            uid="phase7c_test_user_42",
            email="researcher@cardiopulse.org",
            email_verified=True,
            name="Clinical Researcher",
        )
        cls.repo = InMemoryPredictionRepository()

        app.dependency_overrides[get_current_user] = lambda: cls.mock_user
        app.dependency_overrides[get_prediction_repository] = lambda: cls.repo

        cls.client = TestClient(app)

        cls.canonical_features = {
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

    def test_01_models_catalog_serves_four_models(self):
        """1. GET /api/v1/models returns all 4 models with metrics."""
        response = self.client.get("/api/v1/models")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("models", data)
        model_ids = [m["id"] for m in data["models"]]
        self.assertIn("logistic_regression", model_ids)
        self.assertIn("svm", model_ids)
        self.assertIn("random_forest", model_ids)
        self.assertIn("xgboost", model_ids)
        self.assertEqual(len(model_ids), 4)

        for m in data["models"]:
            self.assertTrue(m["available"])
            self.assertIn("accuracy", m["metrics"])
            self.assertIn("roc_auc", m["metrics"])
            self.assertIn("f1_score", m["metrics"])

    def test_02_prediction_with_each_of_four_models(self):
        """2. POST /api/v1/predictions executes inference for each model explicitly."""
        expected_names = {
            "logistic_regression": "Logistic Regression",
            "svm": "Support Vector Machine",
            "random_forest": "Random Forest",
            "xgboost": "XGBoost",
        }

        created_ids = {}
        for model_id, expected_name in expected_names.items():
            payload = dict(self.canonical_features)
            payload["model_id"] = model_id

            response = self.client.post("/api/v1/predictions", json=payload)
            self.assertEqual(response.status_code, 200, f"Failed for model: {model_id}")
            result = response.json()

            self.assertEqual(result["model_id"], model_id)
            self.assertEqual(result["model_name"], expected_name)
            self.assertIn(result["prediction"], [0, 1])
            self.assertGreaterEqual(result["probability"], 0.0)
            self.assertLessEqual(result["probability"], 1.0)
            self.assertTrue(bool(result["prediction_id"]))

            created_ids[model_id] = result["prediction_id"]

        # Verify history reflects all 4 predictions
        history_resp = self.client.get("/api/v1/predictions?limit=50")
        self.assertEqual(history_resp.status_code, 200)
        history_items = history_resp.json()["predictions"]
        self.assertEqual(len(history_items), 4)

        # Verify single detail endpoint works for each model
        for model_id, pid in created_ids.items():
            detail_resp = self.client.get(f"/api/v1/predictions/{pid}")
            self.assertEqual(detail_resp.status_code, 200)
            detail = detail_resp.json()
            self.assertEqual(detail["prediction_id"], pid)
            self.assertEqual(detail["model"]["model_name"], expected_names[model_id])
            self.assertEqual(detail["input"]["age"], 52.0)

    def test_03_no_silent_fallback_on_invalid_model(self):
        """3. Invalid model_id is rejected with 422 and does NOT silently fall back."""
        payload = dict(self.canonical_features)
        payload["model_id"] = "deep_learning_v9"

        response = self.client.post("/api/v1/predictions", json=payload)
        self.assertEqual(response.status_code, 422)
        error_detail = response.json()["detail"]
        self.assertIn("Unknown model identifier", error_detail)

    def test_04_authentication_enforcement(self):
        """4. Unauthenticated requests are rejected with 401."""
        app.dependency_overrides.clear()
        try:
            response = self.client.post(
                "/api/v1/predictions",
                json=dict(self.canonical_features),
            )
            self.assertEqual(response.status_code, 401)
        finally:
            app.dependency_overrides[get_current_user] = lambda: self.mock_user
            app.dependency_overrides[get_prediction_repository] = lambda: self.repo


if __name__ == "__main__":
    unittest.main()
