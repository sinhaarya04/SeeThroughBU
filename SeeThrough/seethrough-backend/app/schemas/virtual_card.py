"""Virtual card schemas."""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class VirtualCardCreate(BaseModel):
    """Virtual card creation request."""

    merchant_domain: str
    max_amount: float
    expires_at: datetime
    merchant_lock: bool = True


class VirtualCardOut(BaseModel):
    """Virtual card output schema."""

    id: int
    user_id: int
    merchant_domain: str
    pan_last4: str
    alias_token: str
    max_amount: float
    currency: str
    expires_at: datetime
    status: str
    controls: Dict[str, bool]
    created_at: datetime

    class Config:
        from_attributes = True

