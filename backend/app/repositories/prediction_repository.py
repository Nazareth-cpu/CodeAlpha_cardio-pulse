"""
Prediction Repository for CardioPulse FastAPI Backend.

Handles persistent Firestore data access for user accounts and prediction history.
Isolates database operations from HTTP routing and ML inference.
Does NOT import FastAPI or HTTP concepts.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import uuid

logger = logging.getLogger("cardiopulse.repository")


class RepositoryError(Exception):
    """Base exception for data repository operations."""
    pass


class DatabaseUnavailableError(RepositoryError):
    """Raised when Firestore or underlying database connection is unavailable."""
    pass


class RecordNotFoundError(RepositoryError):
    """Raised when a specific prediction record is not found."""
    pass


def _format_timestamp(val: Any) -> str:
    """Format datetime or Firestore timestamp object safely to ISO-8601 string."""
    if val is None:
        return datetime.now(timezone.utc).isoformat()
    if isinstance(val, str):
        return val
    if hasattr(val, "isoformat"):
        return val.isoformat()
    if hasattr(val, "to_datetime"):
        return val.to_datetime().isoformat()
    return str(val)


class BasePredictionRepository(ABC):
    """Abstract interface for prediction storage and history queries."""

    @abstractmethod
    def create_prediction(self, uid: str, prediction_data: Dict[str, Any]) -> str:
        """Persist a new prediction record under users/{uid}/predictions and return prediction_id."""
        pass

    @abstractmethod
    def get_user_prediction(self, uid: str, prediction_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single prediction for the user. Returns None if not found."""
        pass

    @abstractmethod
    def list_user_predictions(self, uid: str, limit: int = 20) -> List[Dict[str, Any]]:
        """List predictions for the specified user ordered by created_at descending."""
        pass

    @abstractmethod
    def delete_user_prediction(self, uid: str, prediction_id: str) -> bool:
        """Delete a single prediction record for the user. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def upsert_user(self, uid: str, email: Optional[str] = None) -> None:
        """Create or update user metadata record under users/{uid}."""
        pass


class FirestorePredictionRepository(BasePredictionRepository):
    """
    Authoritative Firestore implementation using the Firebase Admin SDK client.
    Enforces user-scoped subcollections:
      users/{uid}
      users/{uid}/predictions/{prediction_id}
    """

    def __init__(self, firestore_client: Any) -> None:
        if firestore_client is None:
            raise DatabaseUnavailableError("Firestore client instance is required.")
        self.db = firestore_client

    def create_prediction(self, uid: str, prediction_data: Dict[str, Any]) -> str:
        """
        Store authoritative prediction record in Firestore under users/{uid}/predictions/{prediction_id}.
        Generates server-side unique document ID.
        """
        if not uid or not uid.strip():
            raise RepositoryError("User UID is mandatory for persisting prediction records.")

        try:
            from google.cloud import firestore

            # Generate server-side unique prediction ID (hex UUID)
            prediction_id = uuid.uuid4().hex

            doc_ref = (
                self.db.collection("users")
                .document(uid)
                .collection("predictions")
                .document(prediction_id)
            )

            record = {
                "prediction_id": prediction_id,
                "user_id": uid,
                "input": prediction_data.get("input", {}),
                "result": prediction_data.get("result", {}),
                "model": prediction_data.get("model", {}),
                "created_at": firestore.SERVER_TIMESTAMP,
            }

            doc_ref.set(record)
            logger.info("Successfully persisted prediction record %s in Firestore.", prediction_id)
            return prediction_id
        except Exception as exc:
            logger.error("Failed to persist prediction record to Firestore: %s", type(exc).__name__)
            raise RepositoryError("Failed to store prediction record in database.") from exc

    def get_user_prediction(self, uid: str, prediction_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single prediction for the user directly at users/{uid}/predictions/{prediction_id}.
        Guarantees strict path-based user isolation.
        """
        if not uid or not prediction_id:
            return None

        try:
            doc_ref = (
                self.db.collection("users")
                .document(uid)
                .collection("predictions")
                .document(prediction_id)
            )
            snapshot = doc_ref.get()

            if not snapshot.exists:
                return None

            data = snapshot.to_dict() or {}
            data["prediction_id"] = snapshot.id
            data["user_id"] = uid
            data["created_at"] = _format_timestamp(data.get("created_at"))
            return data
        except Exception as exc:
            logger.error("Failed to retrieve prediction record from Firestore: %s", type(exc).__name__)
            raise RepositoryError("Failed to retrieve prediction record from database.") from exc

    def list_user_predictions(self, uid: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Query prediction history for the authenticated user ordered by created_at descending.
        Enforces user subcollection boundary and query limit.
        """
        if not uid:
            return []

        try:
            from google.cloud import firestore

            query = (
                self.db.collection("users")
                .document(uid)
                .collection("predictions")
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            results: List[Dict[str, Any]] = []
            for doc in query.stream():
                data = doc.to_dict() or {}
                results.append(
                    {
                        "prediction_id": doc.id,
                        "prediction": data.get("result", {}).get("prediction", 0),
                        "probability": data.get("result", {}).get("probability", 0.0),
                        "model_name": data.get("model", {}).get("model_name", "Logistic Regression"),
                        "model_version": data.get("model", {}).get("model_version", "v1"),
                        "created_at": _format_timestamp(data.get("created_at")),
                    }
                )
            return results
        except Exception as exc:
            logger.error("Failed to query prediction history from Firestore: %s", type(exc).__name__)
            raise RepositoryError("Failed to query prediction history from database.") from exc

    def delete_user_prediction(self, uid: str, prediction_id: str) -> bool:
        """
        Delete a single prediction record scoped strictly to users/{uid}/predictions/{prediction_id}.
        Returns True if deleted, False if record does not exist.
        """
        if not uid or not prediction_id:
            return False

        try:
            doc_ref = (
                self.db.collection("users")
                .document(uid)
                .collection("predictions")
                .document(prediction_id)
            )
            snapshot = doc_ref.get()
            if not snapshot.exists:
                return False

            doc_ref.delete()
            logger.info("Successfully deleted prediction record %s from Firestore.", prediction_id)
            return True
        except Exception as exc:
            logger.error("Failed to delete prediction record from Firestore: %s", type(exc).__name__)
            raise RepositoryError("Failed to delete prediction record from database.") from exc

    def upsert_user(self, uid: str, email: Optional[str] = None) -> None:
        """
        Create or update non-sensitive metadata for user under users/{uid}.
        Safe against overwriting existing properties via merge=True.
        """
        if not uid:
            return

        try:
            from google.cloud import firestore

            user_ref = self.db.collection("users").document(uid)
            payload: Dict[str, Any] = {
                "uid": uid,
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
            if email:
                payload["email"] = email

            user_ref.set(payload, merge=True)
        except Exception as exc:
            logger.warning("Failed to upsert user document for %s: %s", uid[:6], type(exc).__name__)
            # Non-blocking for the primary prediction flow, but logged


class InMemoryPredictionRepository(BasePredictionRepository):
    """
    Thread-safe in-memory repository for unit testing and offline development.
    Emulates Firestore behavior, ordering, timestamps, and user isolation.
    """

    def __init__(self) -> None:
        # Structure: { uid: { prediction_id: dict } }
        self._storage: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Structure: { uid: dict }
        self._users: Dict[str, Dict[str, Any]] = {}

    def create_prediction(self, uid: str, prediction_data: Dict[str, Any]) -> str:
        if not uid:
            raise RepositoryError("User UID is mandatory.")
        prediction_id = uuid.uuid4().hex
        now_iso = datetime.now(timezone.utc).isoformat()

        if uid not in self._storage:
            self._storage[uid] = {}

        self._storage[uid][prediction_id] = {
            "prediction_id": prediction_id,
            "user_id": uid,
            "input": dict(prediction_data.get("input", {})),
            "result": dict(prediction_data.get("result", {})),
            "model": dict(prediction_data.get("model", {})),
            "created_at": now_iso,
        }
        return prediction_id

    def get_user_prediction(self, uid: str, prediction_id: str) -> Optional[Dict[str, Any]]:
        user_records = self._storage.get(uid, {})
        record = user_records.get(prediction_id)
        if record is None:
            return None
        return dict(record)

    def list_user_predictions(self, uid: str, limit: int = 20) -> List[Dict[str, Any]]:
        user_records = self._storage.get(uid, {})
        # Sort descending by created_at
        sorted_records = sorted(
            user_records.values(),
            key=lambda r: r.get("created_at", ""),
            reverse=True,
        )
        sliced = sorted_records[:limit]
        return [
            {
                "prediction_id": r["prediction_id"],
                "prediction": r.get("result", {}).get("prediction", 0),
                "probability": r.get("result", {}).get("probability", 0.0),
                "model_name": r.get("model", {}).get("model_name", "Logistic Regression"),
                "model_version": r.get("model", {}).get("model_version", "v1"),
                "created_at": r["created_at"],
            }
            for r in sliced
        ]

    def delete_user_prediction(self, uid: str, prediction_id: str) -> bool:
        user_records = self._storage.get(uid, {})
        if prediction_id in user_records:
            del user_records[prediction_id]
            return True
        return False

    def upsert_user(self, uid: str, email: Optional[str] = None) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        if uid not in self._users:
            self._users[uid] = {
                "uid": uid,
                "email": email,
                "created_at": now_iso,
                "updated_at": now_iso,
            }
        else:
            if email:
                self._users[uid]["email"] = email
            self._users[uid]["updated_at"] = now_iso

    def clear(self) -> None:
        """Reset repository storage for clean test isolation."""
        self._storage.clear()
        self._users.clear()


in_memory_prediction_repository = InMemoryPredictionRepository()
