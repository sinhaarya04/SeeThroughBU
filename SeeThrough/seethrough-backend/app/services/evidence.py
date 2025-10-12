"""Evidence collection service."""

import logging
import os
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.utils.hashing import sha256_hash, sha256_hash_str

settings = get_settings()
logger = logging.getLogger(__name__)

# Evidence storage directory
EVIDENCE_DIR = Path("app/static/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def save_image(image_bytes: bytes, checkout_id: int) -> tuple[str, str]:
    """Save image evidence.

    Args:
        image_bytes: Image data
        checkout_id: Associated checkout ID

    Returns:
        Tuple of (url, sha256_hash)
    """
    # Calculate hash
    file_hash = sha256_hash(image_bytes)

    # Save to disk
    filename = f"checkout_{checkout_id}_{file_hash[:8]}.png"
    filepath = EVIDENCE_DIR / filename
    filepath.write_bytes(image_bytes)

    url = f"{settings.base_url}/static/evidence/{filename}"
    logger.info(f"Saved image evidence: {url}")

    return url, file_hash


def save_html_snapshot(html_content: str, checkout_id: int) -> tuple[str, str]:
    """Save HTML snapshot evidence.

    Args:
        html_content: HTML content
        checkout_id: Associated checkout ID

    Returns:
        Tuple of (url, sha256_hash)
    """
    # Calculate hash
    file_hash = sha256_hash_str(html_content)

    # Save to disk
    filename = f"checkout_{checkout_id}_{file_hash[:8]}.html"
    filepath = EVIDENCE_DIR / filename
    filepath.write_text(html_content, encoding="utf-8")

    url = f"{settings.base_url}/static/evidence/{filename}"
    logger.info(f"Saved HTML evidence: {url}")

    return url, file_hash


def hash_bytes_sha256(data: bytes) -> str:
    """Calculate SHA256 hash of bytes.

    Args:
        data: Data to hash

    Returns:
        Hex digest of hash
    """
    return sha256_hash(data)

