"""Merchant schemas."""

from datetime import datetime

from pydantic import BaseModel


class MerchantOut(BaseModel):
    """Merchant output schema."""

    id: int
    domain: str
    display_name: str
    risk_score: float
    created_at: datetime

    class Config:
        from_attributes = True

