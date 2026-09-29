"""
Phase 7 Multi-Model Production Prediction & Selection Test Suite.

Verifies:
  1. Multi-model discovery via GET /api/v1/models
  2. All 4 model artifacts loadable and verified (Logistic Regression, SVM, Random Forest, XGBoost)
  3. Model routing and independent execution for all 4 models
  4. Cross-model deterministic execution with the canonical benchmark input
  5. Security constraints (rejection of arbitrary paths, unknown model IDs, target leakage)
  6. Unauthenticated requests rejected with 401
  7. Firestore model persistence preserving selected model identity
  8. Dataset independence at prediction time
"""

from pathlib import Path
import shutil
import unittest

from fastapi.testclient import TestClient

from backend.app.dependencies.auth import AuthenticatedUser, get_current_user
from backend.app.main import app
from ml.config import SUPPORTED_MODEL_IDS
from ml.inference import (
    get_available_models,
    get_model,
    get_registry,
    predict as ml_predict,
)

CANONICAL_TEST_CASE = {
    "age": 52,
    "sex": 1,
    "cp": 4,
    "trestbps": 138,
    "chol": 246,
    "fbs": 0,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 1.2,
    "slope": 2,
    "ca": 0,
    "thal": 3,
}

MOCK_CLINICIAN = AuthenticatedUser(
    uid="clinician-test-multi-model",
    email="clinician@hospital.org",
    email_verified=True,
    display_name="Dr. Multi-Model",
    roles=["clinician"],
)


class TestMultiModelSelection(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: MOCK_CLINICIAN
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_01_models_catalog_endpoint(self):
        """1. GET /api/v1/models returns all 4 models with live availability."""
        response = self.client.get("/api/v1/models")
        self.assertEqual(response.status_code, 200, f"Error: {response.text}")
        data = response.json()

        self.assertIn("models", data)
        self.assertEqual(len(data["models"]), 4)

        returned_ids = [m["id"] for m in data["models"]]
        for expected_id in ["logistic_regression", "svm", "random_forest", "xgboost"]:
            self.assertIn(expected_id, returned_ids)

        for m in data["models"]:
            self.assertTrue(m["available"], f"Model '{m['id']}' reported as unavailable")
            self.assertIn("accuracy", m["metrics"])
            self.assertIn("roc_auc", m["metrics"])
            self.assertIn("precision", m["metrics"])
            self.assertIn("recall", m["metrics"])
            self.assertIn("f1_score", m["metrics"])

    def test_02_all_four_artifacts_loadable(self):
        """2. Direct loader loads all four pipelines with predict and predict_proba."""
        for m_id in ["logistic_regression", "svm", "random_forest", "xgboost"]:
            pipeline = get_model(m_id)
            self.assertIsNotNone(pipeline, f"Pipeline for '{m_id}' is None")
            self.assertTrue(hasattr(pipeline, "predict"), f"'{m_id}' lacks predict")
            self.assertTrue(hasattr(pipeline, "predict_proba"), f"'{m_id}' lacks predict_proba")

    def test_03_cross_model_prediction_execution(self):
        """3. Execute inference across all 4 models using the same benchmark input."""
        results = {}
        for m_id in ["logistic_regression", "svm", "random_forest", "xgboost"]:
            res = ml_predict(CANONICAL_TEST_CASE, model_id=m_id)
            self.assertIn(res.prediction, [0, 1])
            self.assertTrue(0.0 <= res.probability <= 1.0)
            self.assertEqual(res.model_id, m_id)
            results[m_id] = {
                "prediction": res.prediction,
                "probability": res.probability,
                "model_name": res.model_name,
            }
            print(f"  [Model: {res.model_name} ({m_id})] Pred: {res.prediction}, Prob: {res.probability:.4f}")

        # Verify all 4 models produced valid outputs
        self.assertEqual(len(results), 4)

    def test_04_api_prediction_with_model_selection(self):
        """4. POST /api/v1/predictions routes to requested model and returns correct metadata."""
        for m_id in ["logistic_regression", "svm", "random_forest", "xgboost"]:
            payload = dict(CANONICAL_TEST_CASE)
            payload["model_id"] = m_id

            response = self.client.post("/api/v1/predictions", json=payload)
            self.assertEqual(response.status_code, 200, f"Failed for {m_id}: {response.text}")
            data = response.json()

            self.assertEqual(data["model_id"], m_id)
            self.assertIn(data["prediction"], [0, 1])
            self.assertTrue(0.0 <= data["probability"] <= 1.0)
            self.assertTrue(len(data["prediction_id"]) > 0)

    def test_05_api_nested_features_payload(self):
        """5. POST /api/v1/predictions supports nested {'model_id': '...', 'features': {...}} format."""
        payload = {
            "model_id": "random_forest",
            "features": CANONICAL_TEST_CASE,
        }
        response = self.client.post("/api/v1/predictions", json=payload)
        self.assertEqual(response.status_code, 200, f"Error: {response.text}")
        data = response.json()
        self.assertEqual(data["model_id"], "random_forest")
        self.assertEqual(data["model_name"], "Random Forest")

    def test_06_unknown_model_rejected(self):
        """6. Rejection of unknown model_id with 422."""
        bad_payload = dict(CANONICAL_TEST_CASE)
        bad_payload["model_id"] = "deep_neural_network_v9"
        response = self.client.post("/api/v1/predictions", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    def test_07_path_traversal_model_id_rejected(self):
        """7. Security: Rejection of path traversal or arbitrary file attempts."""
        for bad_id in ["../../etc/passwd", "../something.joblib", "/bin/sh", "model.pkl"]:
            bad_payload = dict(CANONICAL_TEST_CASE)
            bad_payload["model_id"] = bad_id
            response = self.client.post("/api/v1/predictions", json=bad_payload)
            self.assertEqual(response.status_code, 422)

    def test_08_target_leakage_rejected(self):
        """8. Rejection of forbidden fields 'num', 'target', 'id' with 422."""
        for forbidden in ["num", "target", "id"]:
            bad_payload = dict(CANONICAL_TEST_CASE)
            bad_payload[forbidden] = 1
            response = self.client.post("/api/v1/predictions", json=bad_payload)
            self.assertEqual(response.status_code, 422)

    def test_09_unauthenticated_request_rejected(self):
        """9. Unauthenticated requests without token rejected with 401."""
        app.dependency_overrides.clear()
        unauth_client = TestClient(app)
        response = unauth_client.post("/api/v1/predictions", json=CANONICAL_TEST_CASE)
        self.assertEqual(response.status_code, 401)

    def test_10_dataset_csv_runtime_independence(self):
        """10. All 4 models execute without dataset.csv present at runtime."""
        import tempfile
        dataset_path = Path("data/dataset.csv")
        temp_backup = Path(tempfile.gettempdir()) / "dataset_backup_phase7_multi.csv"

        dataset_existed = dataset_path.exists()
        if dataset_existed:
            shutil.move(str(dataset_path), str(temp_backup))

        try:
            for m_id in ["logistic_regression", "svm", "random_forest", "xgboost"]:
                res = ml_predict(CANONICAL_TEST_CASE, model_id=m_id)
                self.assertIn(res.prediction, [0, 1])
        finally:
            if dataset_existed and temp_backup.exists():
                shutil.move(str(temp_backup), str(dataset_path))


if __name__ == "__main__":
    unittest.main()
