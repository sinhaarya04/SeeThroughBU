"""Domain analysis service."""

import logging
from typing import Dict, Tuple

from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

# Known brand domains for lookalike detection
KNOWN_BRANDS = [
    "amazon.com",
    "apple.com",
    "paypal.com",
    "microsoft.com",
    "google.com",
    "facebook.com",
    "netflix.com",
    "spotify.com",
    "walmart.com",
    "target.com",
]


def is_lookalike(candidate_domain: str, legit_domain: str, threshold: int = 85) -> Tuple[bool, float]:
    """Check if a domain is a lookalike of a legitimate domain.

    Args:
        candidate_domain: Domain to check
        legit_domain: Legitimate domain to compare against
        threshold: Similarity threshold (0-100)

    Returns:
        Tuple of (is_lookalike, similarity_score)
    """
    # Clean domains
    candidate = candidate_domain.lower().replace("www.", "")
    legit = legit_domain.lower().replace("www.", "")

    # Calculate similarity
    similarity = fuzz.ratio(candidate, legit)

    # If very similar but not exact, it's a lookalike
    is_suspicious = similarity >= threshold and candidate != legit

    logger.info(f"Domain similarity: {candidate} vs {legit} = {similarity}")

    return is_suspicious, similarity


def check_against_known_brands(domain: str, threshold: int = 85) -> Tuple[bool, str, float]:
    """Check if domain looks like any known brand.

    Args:
        domain: Domain to check
        threshold: Similarity threshold

    Returns:
        Tuple of (is_lookalike, matched_brand, similarity_score)
    """
    for brand in KNOWN_BRANDS:
        is_suspicious, score = is_lookalike(domain, brand, threshold)
        if is_suspicious:
            return True, brand, score

    return False, "", 0.0


def whois_or_fake_metadata(domain: str) -> Dict[str, str]:
    """Get domain metadata (stub for future WHOIS integration).

    Args:
        domain: Domain to lookup

    Returns:
        Dictionary with domain metadata
    """
    return {
        "domain": domain,
        "registrar": "STUB_REGISTRAR",
        "created_date": "2024-01-01",
        "note": "This is a stub implementation for demo purposes",
    }

