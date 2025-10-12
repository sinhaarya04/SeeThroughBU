"""Risk scoring service."""

import logging
from typing import List

logger = logging.getLogger(__name__)


def calculate_risk_score(events: List[dict]) -> float:
    """Calculate aggregate risk score from events.

    Args:
        events: List of risk events with scores

    Returns:
        Aggregate risk score (0-100)
    """
    if not events:
        return 0.0

    # Simple sum with cap at 100
    total_score = sum(event.get("score", 0) for event in events)
    risk_score = min(total_score, 100.0)

    logger.info(f"Calculated risk score: {risk_score} from {len(events)} events")
    return risk_score

