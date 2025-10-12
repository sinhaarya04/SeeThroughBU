"""Checkout schemas."""

from datetime import datetime

from pydantic import BaseModel


class CheckoutOut(BaseModel):
    """Checkout output schema."""

    id: int
    merchant_id: int
    url: str
    created_at: datetime

    class Config:
        from_attributes = True

