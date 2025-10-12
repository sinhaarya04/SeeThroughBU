"""Dispute schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DisputeCreate(BaseModel):
    """Dispute creation request."""

    transaction_id: int
    reason: str
    capture_ids: List[int] = []


class DisputeOut(BaseModel):
    """Dispute output schema."""

    id: int
    user_id: int
    transaction_id: int
    reason: str
    letter_pdf_url: Optional[str] = None
    evidence_zip_url: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

