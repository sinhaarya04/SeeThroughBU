"""Dispute routes."""

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUser, DBSession
from app.models.dispute import Dispute
from app.schemas.dispute import DisputeCreate, DisputeOut
from app.services.dispute import create_dispute

router = APIRouter(prefix="/disputes", tags=["Disputes"])


@router.post("/", response_model=DisputeOut, status_code=status.HTTP_201_CREATED)
def create_dispute_endpoint(data: DisputeCreate, db: DBSession, user: CurrentUser):
    """Create a new dispute."""
    try:
        dispute = create_dispute(
            db=db,
            user_id=user.id,
            transaction_id=data.transaction_id,
            reason=data.reason,
            capture_ids=data.capture_ids,
        )

        return DisputeOut(
            id=dispute.id,
            user_id=dispute.user_id,
            transaction_id=dispute.transaction_id,
            reason=dispute.reason,
            letter_pdf_url=dispute.letter_pdf_url,
            evidence_zip_url=dispute.evidence_zip_url,
            status=dispute.status.value,
            created_at=dispute.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[DisputeOut])
def list_disputes(db: DBSession, user: CurrentUser, skip: int = 0, limit: int = 100):
    """List all disputes for the current user."""
    disputes = (
        db.query(Dispute)
        .filter(Dispute.user_id == user.id)
        .order_by(Dispute.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        DisputeOut(
            id=d.id,
            user_id=d.user_id,
            transaction_id=d.transaction_id,
            reason=d.reason,
            letter_pdf_url=d.letter_pdf_url,
            evidence_zip_url=d.evidence_zip_url,
            status=d.status.value,
            created_at=d.created_at,
        )
        for d in disputes
    ]


@router.get("/{dispute_id}", response_model=DisputeOut)
def get_dispute(dispute_id: int, db: DBSession, user: CurrentUser):
    """Get a specific dispute."""
    dispute = db.query(Dispute).filter(
        Dispute.id == dispute_id, Dispute.user_id == user.id
    ).first()

    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found",
        )

    return DisputeOut(
        id=dispute.id,
        user_id=dispute.user_id,
        transaction_id=dispute.transaction_id,
        reason=dispute.reason,
        letter_pdf_url=dispute.letter_pdf_url,
        evidence_zip_url=dispute.evidence_zip_url,
        status=dispute.status.value,
        created_at=dispute.created_at,
    )

