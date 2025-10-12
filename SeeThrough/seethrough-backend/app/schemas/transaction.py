"""Transaction schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class AuthorizeRequest(BaseModel):
    """Payment authorization request."""

    merchant_domain: str
    amount: float
    virtual_card_id: Optional[int] = None


class AuthorizeResponse(BaseModel):
    """Payment authorization response."""

    transaction_id: int
    status: str
    message: Optional[str] = None


class TransactionOut(BaseModel):
    """Transaction output schema."""

    id: int
    user_id: int
    virtual_card_id: Optional[int] = None
    merchant_domain: str
    amount: float
    currency: str
    status: str
    meta: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

