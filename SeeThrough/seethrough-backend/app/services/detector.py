"""Dark pattern detection service."""

import json
import logging
import re
from typing import Dict, List
from urllib.parse import urlparse

from app.services.domain import check_against_known_brands

logger = logging.getLogger(__name__)

# Detection patterns
HIDDEN_FEE_PATTERNS = [
    r"service\s*fee[:\s]*\$?\d+\.?\d*",
    r"handling\s*fee[:\s]*\$?\d+\.?\d*",
    r"processing\s*fee[:\s]*\$?\d+\.?\d*",
    r"convenience\s*fee[:\s]*\$?\d+\.?\d*",
    r"\+\s*\$\d+\.?\d*\s*fee",
]

TRIAL_PATTERNS = [
    r"free\s*trial",
    r"trial\s*period",
    r"auto[- ]?renew",
    r"automatically\s*renew",
    r"after\s*\d+\s*days",
    r"then\s*\$\d+",
    r"cancel\s*anytime",
]

PRECHECKED_PATTERNS = [
    r"add.*protection",
    r"purchase.*protection",
    r"extended.*warranty",
    r"checked\s*by\s*default",
    r"opt[- ]?out",
]


def detect_hidden_fees(text: str) -> Dict:
    """Detect hidden fees in text.

    Args:
        text: Text to analyze

    Returns:
        Detection result with details
    """
    text_lower = text.lower()
    found_fees = []

    for pattern in HIDDEN_FEE_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            found_fees.append(match.group(0))

    if found_fees:
        logger.info(f"Found {len(found_fees)} hidden fee indicators")
        return {
            "detected": True,
            "lines": found_fees[:5],  # Limit to 5
            "count": len(found_fees),
        }

    return {"detected": False}


def detect_trial_autorenew(text: str) -> Dict:
    """Detect auto-renewing trial patterns.

    Args:
        text: Text to analyze

    Returns:
        Detection result with details
    """
    text_lower = text.lower()
    indicators = []

    for pattern in TRIAL_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            indicators.append(pattern)

    # Try to extract trial days
    trial_days = None
    days_match = re.search(r"(\d+)[- ]?day\s*trial", text_lower)
    if days_match:
        trial_days = int(days_match.group(1))

    if indicators:
        result = {
            "detected": True,
            "indicators": indicators[:3],
            "count": len(indicators),
        }
        if trial_days:
            result["trial_days"] = trial_days
        logger.info(f"Found trial auto-renew with {len(indicators)} indicators")
        return result

    return {"detected": False}


def detect_prechecked_addon(text: str) -> Dict:
    """Detect pre-checked addon patterns.

    Args:
        text: Text to analyze

    Returns:
        Detection result with details
    """
    text_lower = text.lower()
    found_patterns = []

    for pattern in PRECHECKED_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            found_patterns.append(pattern)

    if found_patterns:
        logger.info(f"Found {len(found_patterns)} prechecked addon indicators")
        return {
            "detected": True,
            "patterns": found_patterns[:3],
            "count": len(found_patterns),
        }

    return {"detected": False}


def detect_lookalike_domain(url: str, domain: str) -> Dict:
    """Detect lookalike domains.

    Args:
        url: Full URL
        domain: Parsed domain

    Returns:
        Detection result with details
    """
    is_lookalike, matched_brand, score = check_against_known_brands(domain)

    if is_lookalike:
        logger.warning(f"Detected lookalike domain: {domain} (similar to {matched_brand})")
        return {
            "detected": True,
            "domain": domain,
            "suspected_brand": matched_brand,
            "similarity_score": score,
        }

    return {"detected": False}


def analyze_checkout(raw_text: str, url: str, domain: str) -> List[Dict]:
    """Analyze checkout page for dark patterns.

    Args:
        raw_text: Combined text from OCR and HTML
        url: Checkout URL
        domain: Parsed domain

    Returns:
        List of detected risk events
    """
    events = []

    # Detect hidden fees
    fee_result = detect_hidden_fees(raw_text)
    if fee_result.get("detected"):
        events.append(
            {
                "kind": "HIDDEN_FEE",
                "score": 25,
                "detail": {
                    "lines": fee_result.get("lines", []),
                    "count": fee_result.get("count", 0),
                },
            }
        )

    # Detect trial auto-renew
    trial_result = detect_trial_autorenew(raw_text)
    if trial_result.get("detected"):
        events.append(
            {
                "kind": "TRIAL_AUTORENEW",
                "score": 20,
                "detail": {
                    "trial_days": trial_result.get("trial_days"),
                    "indicators": trial_result.get("indicators", []),
                },
            }
        )

    # Detect pre-checked addons
    addon_result = detect_prechecked_addon(raw_text)
    if addon_result.get("detected"):
        events.append(
            {
                "kind": "PRECHECKED_ADDON",
                "score": 15,
                "detail": {
                    "patterns": addon_result.get("patterns", []),
                    "count": addon_result.get("count", 0),
                },
            }
        )

    # Detect lookalike domain
    domain_result = detect_lookalike_domain(url, domain)
    if domain_result.get("detected"):
        events.append(
            {
                "kind": "LOOKALIKE_DOMAIN",
                "score": 30,
                "detail": {
                    "domain": domain_result.get("domain"),
                    "suspected_brand": domain_result.get("suspected_brand"),
                    "similarity_score": domain_result.get("similarity_score"),
                },
            }
        )

    logger.info(f"Detected {len(events)} risk events for {domain}")
    return events

