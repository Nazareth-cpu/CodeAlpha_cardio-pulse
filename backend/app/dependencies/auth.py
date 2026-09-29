"""
Authentication Dependencies for CardioPulse FastAPI Backend.

Enforces server-side Firebase ID token verification.
Exposes get_current_user dependency providing verified user context.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from backend.app.core.firebase import verify_firebase_token

logger = logging.getLogger("cardiopulse.auth")

# HTTPBearer configured with auto_error=False to allow exact error responses
security = HTTPBearer(
    auto_error=False,
    description="Enter your Firebase ID token (format: Bearer <ID_TOKEN>)",
)


class AuthenticatedUser(BaseModel):
    """Verified identity derived from validated Firebase ID token."""
    uid: str = Field(..., description="Unique Firebase user identifier")
    email: Optional[str] = Field(None, description="User email address")
    email_verified: bool = Field(False, description="Whether email has been verified")
    name: Optional[str] = Field(None, description="Display name of user")


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> AuthenticatedUser:
    """
    FastAPI dependency that extracts and validates the Firebase ID token from the Authorization header.

    Enforces:
      - Authorization header present and formatted as 'Bearer <token>'
      - Rejection of missing, malformed, invalid, or expired tokens with HTTP 401
      - Returns AuthenticatedUser with verified Firebase UID
    """
    raw_auth_header = request.headers.get("Authorization")

    # 1. Missing Authorization header
    if not raw_auth_header or not raw_auth_header.strip():
        logger.info("Authentication rejected: Missing Authorization header on %s", request.url.path)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    cleaned_header = raw_auth_header.strip()
    # Missing Bearer token (e.g. 'Bearer' or 'Bearer   ')
    if cleaned_header.lower() == "bearer":
        logger.info("Authentication rejected: Missing Bearer token value.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Malformed Authorization header (e.g. Basic, missing Bearer, or invalid format)
    header_parts = cleaned_header.split()
    if len(header_parts) != 2 or header_parts[0].lower() != "bearer":
        logger.info("Authentication rejected: Malformed Authorization header scheme.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = header_parts[1].strip()
    if not token:
        logger.info("Authentication rejected: Empty Bearer token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verify token with Firebase Admin SDK
    decoded_token = verify_firebase_token(token)

    # 4. Extract verified identity (uid is mandatory in valid Firebase tokens)
    uid = decoded_token.get("uid")
    if not uid:
        logger.warning("Authentication rejected: Decoded token missing 'uid' claim.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedUser(
        uid=uid,
        email=decoded_token.get("email"),
        email_verified=decoded_token.get("email_verified", False),
        name=decoded_token.get("name"),
    )
