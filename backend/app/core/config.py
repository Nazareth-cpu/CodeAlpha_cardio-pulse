"""
Core configuration for CardioPulse FastAPI Backend.

Loads environment variables, defines API routes, and manages CORS settings.
Decoupled from machine-specific absolute paths.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

# Ensure repository root is on sys.path so ml package can be imported anywhere
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _get_default_firebase_project_id() -> str:
    env_val = os.getenv("FIREBASE_PROJECT_ID", "")
    if env_val:
        return env_val
    config_path = PROJECT_ROOT / "firebase-applet-config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("projectId", "")
        except Exception:
            return ""
    return ""


def _get_default_firestore_database_id() -> Optional[str]:
    env_val = os.getenv("FIRESTORE_DATABASE_ID", "")
    if env_val:
        return env_val
    config_path = PROJECT_ROOT / "firebase-applet-config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("firestoreDatabaseId", None)
        except Exception:
            return None
    return None


class Settings:
    PROJECT_NAME: str = "Heart Disease Prediction API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS configuration
    _cors_raw: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000",
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        if not self._cors_raw:
            return []
        return [origin.strip() for origin in self._cors_raw.split(",") if origin.strip()]

    CORS_ORIGIN_REGEX: str = (
        r"^https?://(localhost|127\.0\.0\.1|([a-zA-Z0-9-]+\.)*run\.app|([a-zA-Z0-9-]+\.)*web\.app|([a-zA-Z0-9-]+\.)*firebaseapp\.com|([a-zA-Z0-9-]+\.)*google\.com|([a-zA-Z0-9-]+\.)*googleusercontent\.com|([a-zA-Z0-9-]+\.)*google\.dev|([a-zA-Z0-9-]+\.)*cloudshell\.dev|([a-zA-Z0-9-]+\.)*usercontent\.goog)(:\d+)?$"
    )

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Firebase Authentication and Firestore configuration
    FIREBASE_PROJECT_ID: str = _get_default_firebase_project_id()
    FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    FIRESTORE_DATABASE_ID: Optional[str] = _get_default_firestore_database_id()

    @property
    def formatted_firebase_private_key(self) -> str:
        """Handle escaped newlines in private key string and ensure valid PEM framing."""
        if not self.FIREBASE_PRIVATE_KEY:
            return ""
        pk = self.FIREBASE_PRIVATE_KEY.replace("\\n", "\n").strip()
        # Auto-wrap with PEM headers if missing
        if not pk.startswith("-----BEGIN"):
            pk = f"-----BEGIN PRIVATE KEY-----\n{pk}\n-----END PRIVATE KEY-----\n"
        return pk


settings = Settings()
