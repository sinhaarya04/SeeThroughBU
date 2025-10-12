"""Hashing utilities."""

import hashlib


def sha256_hash(data: bytes) -> str:
    """Generate SHA256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_hash_str(data: str) -> str:
    """Generate SHA256 hash of string."""
    return hashlib.sha256(data.encode()).hexdigest()

