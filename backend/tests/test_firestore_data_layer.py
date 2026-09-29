"""
Unit and integration tests for Phase 4: Firestore Data Layer.

Verifies:
  AUTHENTICATION:
    1. Unauthenticated history request -> 401
    2. Unauthenticated single-record request -> 401
    3. Unauthenticated delete -> 401
  PREDICTION CREATION:
    4. Authenticated prediction creates record in repository
    5. Returned prediction_id matches stored record
    6. Stored UID comes from verified authentication context
    7. Client cannot provide a different UID
  HISTORY:
    8. Authenticated user receives only their own predictions
    9. History is ordered by created_at descending
    10. History respects the limit
    11. Excessive limit is rejected with 422
  SINGLE RECORD:
    12. User can retrieve own prediction
    13. User cannot retrieve another user's prediction (returns 404)
    14. Non-existent prediction returns 404
  DELETE:
    15. User can delete own prediction
    16. User cannot delete another user's prediction (returns 404)
    17. Non-existent prediction returns 404
  FAILURE HANDLING:
    18. Firestore write failure does not produce a false success (returns 500)
    19. Firestore read failure produces safe error (500)
    20. Firestore exceptions are not exposed to clients
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from backend.app.dependencies.auth import AuthenticatedUser, get_current_user
from backend.app.dependencies.repository import get_prediction_repository
from backend.app.main import app
from backend.app.repositories.prediction_repository import (
    BasePredictionRepository,
    DatabaseUnavailableError,
    InMemoryPredictionRepository,
    RepositoryError,
    in_memory_prediction_repository,
)


class TestFirestoreDataLayer(unittest.TestCase):
    """Test suite covering the Phase 4 Firestore data layer and endpoints."""

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

    def setUp(self):
        # Reset in-memory repository before each test
        in_memory_prediction_repository.clear()
        self.test_repo = InMemoryPredictionRepository()
        app.dependency_overrides[get_prediction_repository] = lambda: self.test_repo

        # Default authenticated user
        self.user_a = AuthenticatedUser(
            uid="user_alpha_111",
            email="alpha@cardiopulse.org",
            email_verified=True,
            name="Dr. Alpha",
        )
        self.user_b = AuthenticatedUser(
            uid="user_beta_222",
            email="beta@cardiopulse.org",
            email_verified=True,
            name="Dr. Beta",
        )
        app.dependency_overrides[get_current_user] = lambda: self.user_a

    def tearDown(self):
        app.dependency_overrides.clear()

    # =========================================================================
    # AUTHENTICATION TESTS (1 - 3)
    # =========================================================================

    def test_01_unauthenticated_history_request_rejected(self):
        """1. Unauthenticated history request -> 401."""
        app.dependency_overrides.pop(get_current_user, None)
        response = self.client.get("/api/v1/predictions")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Authentication required."})

    def test_02_unauthenticated_single_record_request_rejected(self):
        """2. Unauthenticated single-record request -> 401."""
        app.dependency_overrides.pop(get_current_user, None)
        response = self.client.get("/api/v1/predictions/sample_pred_123")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Authentication required."})

    def test_03_unauthenticated_delete_rejected(self):
        """3. Unauthenticated delete -> 401."""
        app.dependency_overrides.pop(get_current_user, None)
        response = self.client.delete("/api/v1/predictions/sample_pred_123")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Authentication required."})

    # =========================================================================
    # PREDICTION CREATION TESTS (4 - 7)
    # =========================================================================

    def test_04_authenticated_prediction_creates_record(self):
        """4. Authenticated prediction creates record in repository."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("prediction_id", data)
        self.assertTrue(len(data["prediction_id"]) > 0)

        # Verify record exists in user_a's storage
        stored = self.test_repo.get_user_prediction(
            uid=self.user_a.uid,
            prediction_id=data["prediction_id"],
        )
        self.assertIsNotNone(stored)
        self.assertEqual(stored["user_id"], self.user_a.uid)

    def test_05_returned_prediction_id_matches_stored_record(self):
        """5. Returned prediction_id matches stored record."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        returned_id = response.json()["prediction_id"]

        stored = self.test_repo.get_user_prediction(
            uid=self.user_a.uid,
            prediction_id=returned_id,
        )
        self.assertEqual(stored["prediction_id"], returned_id)

    def test_06_stored_uid_comes_from_verified_context(self):
        """6. Stored UID comes from verified authentication context."""
        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        pred_id = response.json()["prediction_id"]

        stored = self.test_repo.get_user_prediction(
            uid=self.user_a.uid,
            prediction_id=pred_id,
        )
        self.assertEqual(stored["user_id"], "user_alpha_111")

    def test_07_client_cannot_provide_different_uid(self):
        """7. Client cannot provide a different UID (rejected as extra field with 422)."""
        malicious_payload = dict(self.valid_payload)
        malicious_payload["uid"] = "victim_user_999"
        malicious_payload["user_id"] = "victim_user_999"

        response = self.client.post("/api/v1/predictions", json=malicious_payload)
        self.assertEqual(response.status_code, 422)

    # =========================================================================
    # HISTORY TESTS (8 - 11)
    # =========================================================================

    def test_08_authenticated_user_receives_only_their_own_predictions(self):
        """8. Authenticated user receives only their own predictions."""
        # Create predictions for User A
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        resp_a1 = self.client.post("/api/v1/predictions", json=self.valid_payload)
        resp_a2 = self.client.post("/api/v1/predictions", json=self.valid_payload)
        id_a1 = resp_a1.json()["prediction_id"]
        id_a2 = resp_a2.json()["prediction_id"]

        # Create prediction for User B
        app.dependency_overrides[get_current_user] = lambda: self.user_b
        resp_b = self.client.post("/api/v1/predictions", json=self.valid_payload)
        id_b = resp_b.json()["prediction_id"]

        # User A fetches history
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        history_a = self.client.get("/api/v1/predictions")
        self.assertEqual(history_a.status_code, 200)
        pred_ids_a = [p["prediction_id"] for p in history_a.json()["predictions"]]
        self.assertIn(id_a1, pred_ids_a)
        self.assertIn(id_a2, pred_ids_a)
        self.assertNotIn(id_b, pred_ids_a)

    def test_09_history_ordered_by_created_at_descending(self):
        """9. History is ordered by created_at descending."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        resp1 = self.client.post("/api/v1/predictions", json=self.valid_payload)
        resp2 = self.client.post("/api/v1/predictions", json=self.valid_payload)

        history = self.client.get("/api/v1/predictions").json()
        predictions = history["predictions"]
        self.assertGreaterEqual(len(predictions), 2)
        # Verify descending order of timestamps
        ts_first = predictions[0]["created_at"]
        ts_second = predictions[1]["created_at"]
        self.assertGreaterEqual(ts_first, ts_second)

    def test_10_history_respects_the_limit(self):
        """10. History respects the limit."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        for _ in range(5):
            self.client.post("/api/v1/predictions", json=self.valid_payload)

        history = self.client.get("/api/v1/predictions?limit=3").json()
        self.assertEqual(len(history["predictions"]), 3)
        self.assertEqual(history["limit"], 3)
        self.assertEqual(history["total"], 3)

    def test_11_excessive_limit_rejected_or_capped(self):
        """11. Excessive or invalid limit is rejected with 422."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        # Limit > 100
        res_high = self.client.get("/api/v1/predictions?limit=101")
        self.assertEqual(res_high.status_code, 422)

        # Limit <= 0
        res_zero = self.client.get("/api/v1/predictions?limit=0")
        self.assertEqual(res_zero.status_code, 422)

        res_neg = self.client.get("/api/v1/predictions?limit=-5")
        self.assertEqual(res_neg.status_code, 422)

    # =========================================================================
    # SINGLE RECORD TESTS (12 - 14)
    # =========================================================================

    def test_12_user_can_retrieve_own_prediction(self):
        """12. User can retrieve own prediction."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        post_resp = self.client.post("/api/v1/predictions", json=self.valid_payload)
        pred_id = post_resp.json()["prediction_id"]

        get_resp = self.client.get(f"/api/v1/predictions/{pred_id}")
        self.assertEqual(get_resp.status_code, 200)
        detail = get_resp.json()
        self.assertEqual(detail["prediction_id"], pred_id)
        self.assertEqual(detail["user_id"], self.user_a.uid)
        self.assertIn("input", detail)
        self.assertIn("result", detail)
        self.assertIn("model", detail)

    def test_13_user_cannot_retrieve_another_users_prediction(self):
        """13. User cannot retrieve another user's prediction (returns 404)."""
        # User A creates a prediction
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        post_resp = self.client.post("/api/v1/predictions", json=self.valid_payload)
        id_a = post_resp.json()["prediction_id"]

        # User B attempts to access User A's prediction
        app.dependency_overrides[get_current_user] = lambda: self.user_b
        get_resp = self.client.get(f"/api/v1/predictions/{id_a}")
        self.assertEqual(get_resp.status_code, 404)
        self.assertEqual(get_resp.json(), {"detail": "Prediction record not found."})

    def test_14_non_existent_prediction_returns_404(self):
        """14. Non-existent prediction returns 404."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        response = self.client.get("/api/v1/predictions/non_existent_uuid_99999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Prediction record not found."})

    # =========================================================================
    # DELETE TESTS (15 - 17)
    # =========================================================================

    def test_15_user_can_delete_own_prediction(self):
        """15. User can delete own prediction."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        post_resp = self.client.post("/api/v1/predictions", json=self.valid_payload)
        pred_id = post_resp.json()["prediction_id"]

        # Delete record
        del_resp = self.client.delete(f"/api/v1/predictions/{pred_id}")
        self.assertEqual(del_resp.status_code, 200)
        self.assertTrue(del_resp.json()["success"])
        self.assertEqual(del_resp.json()["prediction_id"], pred_id)

        # Confirm it is gone
        get_resp = self.client.get(f"/api/v1/predictions/{pred_id}")
        self.assertEqual(get_resp.status_code, 404)

    def test_16_user_cannot_delete_another_users_prediction(self):
        """16. User cannot delete another user's prediction (returns 404)."""
        # User A creates a prediction
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        post_resp = self.client.post("/api/v1/predictions", json=self.valid_payload)
        id_a = post_resp.json()["prediction_id"]

        # User B attempts to delete User A's prediction
        app.dependency_overrides[get_current_user] = lambda: self.user_b
        del_resp = self.client.delete(f"/api/v1/predictions/{id_a}")
        self.assertEqual(del_resp.status_code, 404)
        self.assertEqual(del_resp.json(), {"detail": "Prediction record not found."})

        # Confirm User A's record still exists
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        get_resp = self.client.get(f"/api/v1/predictions/{id_a}")
        self.assertEqual(get_resp.status_code, 200)

    def test_17_non_existent_prediction_delete_returns_404(self):
        """17. Non-existent prediction delete returns 404."""
        app.dependency_overrides[get_current_user] = lambda: self.user_a
        del_resp = self.client.delete("/api/v1/predictions/does_not_exist_xyz")
        self.assertEqual(del_resp.status_code, 404)
        self.assertEqual(del_resp.json(), {"detail": "Prediction record not found."})

    # =========================================================================
    # FAILURE HANDLING TESTS (18 - 20)
    # =========================================================================

    def test_18_firestore_write_failure_does_not_produce_false_success(self):
        """18. Firestore write failure does not produce a false success (returns 500 error)."""
        failing_repo = MagicMock(spec=BasePredictionRepository)
        failing_repo.create_prediction.side_effect = RepositoryError("Disk write simulated failure")
        app.dependency_overrides[get_prediction_repository] = lambda: failing_repo

        response = self.client.post("/api/v1/predictions", json=self.valid_payload)
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Prediction computed successfully but could not be saved to history.")
        # Ensure it never claimed false success
        self.assertNotIn("prediction_id", data)

    def test_19_firestore_read_failure_produces_safe_error(self):
        """19. Firestore read failure produces safe 500/503 error."""
        failing_repo = MagicMock(spec=BasePredictionRepository)
        failing_repo.list_user_predictions.side_effect = RepositoryError("Query timeout")
        failing_repo.get_user_prediction.side_effect = RepositoryError("Network drop")
        app.dependency_overrides[get_prediction_repository] = lambda: failing_repo

        # History read
        resp_hist = self.client.get("/api/v1/predictions")
        self.assertEqual(resp_hist.status_code, 500)
        self.assertEqual(resp_hist.json(), {"detail": "Unable to retrieve prediction history."})

        # Single record read
        resp_single = self.client.get("/api/v1/predictions/some_record_id")
        self.assertEqual(resp_single.status_code, 500)
        self.assertEqual(resp_single.json(), {"detail": "Unable to retrieve prediction record."})

    def test_20_firestore_exceptions_are_not_exposed_to_clients(self):
        """20. Raw Firestore exceptions or stack traces are not exposed to clients."""
        failing_repo = MagicMock(spec=BasePredictionRepository)
        failing_repo.get_user_prediction.side_effect = Exception("google.cloud.exceptions.InternalServerError: secret DB path")
        app.dependency_overrides[get_prediction_repository] = lambda: failing_repo

        response = self.client.get("/api/v1/predictions/some_record_id")
        self.assertEqual(response.status_code, 500)
        # Ensure no traceback or internal DB paths are leaked
        response_text = response.text
        self.assertNotIn("google.cloud", response_text)
        self.assertNotIn("secret DB path", response_text)
        self.assertNotIn("Traceback", response_text)


if __name__ == "__main__":
    unittest.main()
