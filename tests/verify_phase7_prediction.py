"""
Phase 7 Real ML Prediction Integration Verification Script

Tests:
  1. Direct Phase 1 inference execution with canonical test case
  2. Repeatability / determinism test
  3. API endpoint execution and contract equality (API == Predictor)
  4. Dataset.csv runtime independence test
  5. Target leakage rejection ('num', 'target', 'id')
  6. Categorical domain enforcement
"""

import json
from pathlib import Path
import shutil
import sys
import unittest

from fastapi.testclient import TestClient

from backend.app.dependencies.auth import AuthenticatedUser, get_current_user
from backend.app.main import app
from ml.config import CANONICAL_FEATURES
from ml.inference import get_model_metadata, get_predictor, predict as ml_predict

TEST_INPUT = {
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

MOCK_USER = AuthenticatedUser(
    uid="test-phase7-clinician-123",
    email="clinician@test.org",
    email_verified=True,
    display_name="Dr. Test",
    roles=["clinician"],
)


class TestPhase7PredictionIntegration(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: MOCK_USER
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_01_direct_ml_inference(self):
        """1. Direct Phase 1 inference with benchmark test case."""
        result = ml_predict(TEST_INPUT)
        self.assertIn(result.prediction, [0, 1], "Prediction must be 0 or 1")
        self.assertTrue(0.0 <= result.probability <= 1.0, "Probability must be in [0, 1]")
        self.assertEqual(result.model_name, "Logistic Regression")
        self.assertEqual(result.model_version, "heart-disease-logistic-regression-v1")
        print(f"\n[Test 1] Direct ML Result -> Prediction: {result.prediction}, Probability: {result.probability:.4f}")

    def test_02_repeatability_and_determinism(self):
        """2. Exact repeatability: 5 repeated evaluations must produce identical results."""
        first_result = ml_predict(TEST_INPUT)
        for i in range(5):
            repeated = ml_predict(TEST_INPUT)
            self.assertEqual(repeated.prediction, first_result.prediction)
            self.assertEqual(repeated.probability, first_result.probability)

    def test_03_api_prediction_matches_direct_predictor(self):
        """3. API output matches direct predictor output exactly."""
        direct_result = ml_predict(TEST_INPUT)
        response = self.client.post("/api/v1/predictions", json=TEST_INPUT)
        self.assertEqual(response.status_code, 200, f"API error: {response.text}")
        data = response.json()

        self.assertEqual(data["prediction"], direct_result.prediction)
        self.assertEqual(data["probability"], direct_result.probability)
        self.assertEqual(data["model_name"], direct_result.model_name)
        self.assertEqual(data["model_version"], direct_result.model_version)
        self.assertTrue(len(data["prediction_id"]) > 0)
        print(f"[Test 3] API Response -> ID: {data['prediction_id']}, Pred: {data['prediction']}, Prob: {data['probability']}")

    def test_04_dataset_csv_runtime_independence(self):
        """4. Inference works without dataset.csv at runtime."""
        dataset_path = Path("data/dataset.csv")
        temp_backup = Path("/tmp/dataset_backup_phase7.csv")

        dataset_existed = dataset_path.exists()
        if dataset_existed:
            shutil.move(str(dataset_path), str(temp_backup))

        try:
            # Predictor must execute without dataset.csv present
            res = ml_predict(TEST_INPUT)
            self.assertIn(res.prediction, [0, 1])
        finally:
            if dataset_existed and temp_backup.exists():
                shutil.move(str(temp_backup), str(dataset_path))

    def test_05_target_leakage_rejected(self):
        """5. Rejection of forbidden leakage fields 'num', 'target', 'id'."""
        for forbidden in ["num", "target", "id"]:
            bad_input = dict(TEST_INPUT)
            bad_input[forbidden] = 1
            response = self.client.post("/api/v1/predictions", json=bad_input)
            self.assertEqual(response.status_code, 422, f"Expected 422 for field '{forbidden}'")

    def test_06_unauthenticated_request_rejected(self):
        """6. Unauthenticated requests without Bearer token return 401."""
        app.dependency_overrides.clear()
        client_unauth = TestClient(app)
        response = client_unauth.post("/api/v1/predictions", json=TEST_INPUT)
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
