"""Capture schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CaptureOut(BaseModel):
    """Capture output schema."""

    id: int
    checkout_id: int
    image_url: Optional[str] = None
    html_snapshot_url: Optional[str] = None
    sha256: str
    created_at: datetime

    class Config:
        from_attributes = True

