"""Logging configuration."""

import logging
import sys

from app.config import get_settings

settings = get_settings()


def setup_logging():
    """Configure application logging."""
    log_level = logging.DEBUG if settings.app_env == "local" else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from some libraries
    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

