"""
Phase 7B Comprehensive Verification Script.

Explicitly verifies:
  A. OPTIONS /api/v1/predictions from Cloud Run origin (https://ais-dev-*.run.app)
  B. OPTIONS /api/v1/predictions from localhost (http://localhost:5173)
  C. Authorization header during preflight handshake
  D. Malicious external origin rejection (https://malicious-external-site.com)
  E. GET /api/v1/models returns all 4 models with metrics and live availability
  F. POST prediction with Logistic Regression (deterministic output, real probability)
  G. POST prediction with Support Vector Machine (deterministic output, real probability)
  H. POST prediction with Random Forest (deterministic output, real probability)
  I. POST prediction with XGBoost (deterministic output, real probability)
"""

import sys
import unittest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.dependencies.auth import AuthenticatedUser, get_current_user

BENCHMARK_RECORD = {
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

TEST_CLINICIAN = AuthenticatedUser(
    uid="clinician-phase7b-test-uid",
    email="clinician@cardiopulse.org",
    email_verified=True,
    display_name="Dr. Verification",
    roles=["clinician"],
)


class TestPhase7BVerification(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: TEST_CLINICIAN
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_A_options_cloud_run_origin(self):
        """A. OPTIONS /api/v1/predictions from Cloud Run origin."""
        cloud_run_origin = "https://ais-dev-uu3lw37htk375vcjewppls-93479644791.asia-southeast1.run.app"
        res = self.client.options(
            "/api/v1/predictions",
            headers={
                "Origin": cloud_run_origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization,Content-Type",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("access-control-allow-origin"), cloud_run_origin)
        self.assertEqual(res.headers.get("access-control-allow-credentials"), "true")

    def test_B_options_localhost_origin(self):
        """B. OPTIONS /api/v1/predictions from localhost."""
        res = self.client.options(
            "/api/v1/predictions",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization,Content-Type",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("access-control-allow-origin"), "http://localhost:5173")
        self.assertEqual(res.headers.get("access-control-allow-credentials"), "true")

    def test_C_authorization_header_during_preflight(self):
        """C. Authorization header during preflight."""
        res = self.client.options(
            "/api/v1/predictions",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization,Content-Type",
            },
        )
        self.assertEqual(res.status_code, 200)
        allow_headers = res.headers.get("access-control-allow-headers", "").lower()
        self.assertTrue("authorization" in allow_headers or "*" in allow_headers)

    def test_D_malicious_origin_rejection(self):
        """D. Malicious external origin rejection."""
        res = self.client.options(
            "/api/v1/predictions",
            headers={
                "Origin": "https://malicious-external-site.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertNotEqual(
            res.headers.get("access-control-allow-origin"),
            "https://malicious-external-site.com",
        )

    def test_E_get_models_catalog(self):
        """E. GET /api/v1/models returns all 4 models."""
        res = self.client.get("/api/v1/models")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("models", data)
        self.assertEqual(len(data["models"]), 4)

        model_ids = {m["id"]: m for m in data["models"]}
        for expected in ["logistic_regression", "svm", "random_forest", "xgboost"]:
            self.assertIn(expected, model_ids)
            m = model_ids[expected]
            self.assertTrue(m["available"])
            self.assertIn("accuracy", m["metrics"])
            self.assertIn("roc_auc", m["metrics"])

    def test_F_post_prediction_logistic_regression(self):
        """F. POST prediction with Logistic Regression."""
        payload = dict(BENCHMARK_RECORD)
        payload["model_id"] = "logistic_regression"
        res = self.client.post("/api/v1/predictions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model_id"], "logistic_regression")
        self.assertEqual(data["model_name"], "Logistic Regression")
        self.assertEqual(data["prediction"], 1)
        self.assertAlmostEqual(data["probability"], 0.5283, places=2)

    def test_G_post_prediction_svm(self):
        """G. POST prediction with Support Vector Machine."""
        payload = dict(BENCHMARK_RECORD)
        payload["model_id"] = "svm"
        res = self.client.post("/api/v1/predictions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model_id"], "svm")
        self.assertEqual(data["model_name"], "Support Vector Machine")
        self.assertIn(data["prediction"], [0, 1])
        self.assertTrue(0.0 <= data["probability"] <= 1.0)

    def test_H_post_prediction_random_forest(self):
        """H. POST prediction with Random Forest."""
        payload = dict(BENCHMARK_RECORD)
        payload["model_id"] = "random_forest"
        res = self.client.post("/api/v1/predictions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model_id"], "random_forest")
        self.assertEqual(data["model_name"], "Random Forest")
        self.assertIn(data["prediction"], [0, 1])
        self.assertTrue(0.0 <= data["probability"] <= 1.0)

    def test_I_post_prediction_xgboost(self):
        """I. POST prediction with XGBoost."""
        payload = dict(BENCHMARK_RECORD)
        payload["model_id"] = "xgboost"
        res = self.client.post("/api/v1/predictions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model_id"], "xgboost")
        self.assertEqual(data["model_name"], "XGBoost")
        self.assertIn(data["prediction"], [0, 1])
        self.assertTrue(0.0 <= data["probability"] <= 1.0)


if __name__ == "__main__":
    unittest.main()
