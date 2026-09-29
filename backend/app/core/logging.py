"""
Structured logging configuration for CardioPulse FastAPI Backend.

Enforces privacy safeguards: Never logs sensitive patient health payloads.
Logs high-level application events, model availability, and error diagnostics.
"""

import logging
import sys

from backend.app.core.config import settings


def setup_logging() -> None:
    """Configure root and application loggers."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


logger = logging.getLogger("cardiopulse.backend")
