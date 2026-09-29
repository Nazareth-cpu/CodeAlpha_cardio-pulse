"""
Dependencies package for CardioPulse FastAPI Backend.
"""

from backend.app.dependencies.auth import AuthenticatedUser, get_current_user

__all__ = ["AuthenticatedUser", "get_current_user"]
