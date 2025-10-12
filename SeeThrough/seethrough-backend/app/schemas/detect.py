"""Detection schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class RiskEventOut(BaseModel):
    """Risk event output schema."""

    kind: str
    score: float
    detail: Dict[str, Any]


class CleanOverlay(BaseModel):
    """Clean overlay information."""

    true_total: Optional[float] = None
    callouts: List[str]


class ScanResponse(BaseModel):
    """Scan response schema."""

    checkout_id: int
    domain: str
    risk_score: float
    events: List[RiskEventOut]
    clean_overlay: CleanOverlay

