"""Capture routes."""

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUser, DBSession
from app.models.capture import Capture
from app.schemas.capture import CaptureOut

router = APIRouter(prefix="/captures", tags=["Captures"])


@router.get("/{capture_id}", response_model=CaptureOut)
def get_capture(capture_id: int, db: DBSession, user: CurrentUser):
    """Get a specific capture by ID."""
    capture = db.query(Capture).filter(Capture.id == capture_id).first()

    if not capture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capture not found",
        )

    return capture

