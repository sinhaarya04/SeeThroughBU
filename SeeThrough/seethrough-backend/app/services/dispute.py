"""Dispute generation service."""

import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
    HTML = None

from app.config import get_settings
from app.models.capture import Capture
from app.models.dispute import Dispute, DisputeStatus
from app.models.transaction import Transaction

settings = get_settings()
logger = logging.getLogger(__name__)

# Output directories
DISPUTES_DIR = Path("app/static/disputes")
DISPUTES_DIR.mkdir(parents=True, exist_ok=True)

# Template environment
template_env = Environment(loader=FileSystemLoader("app/templates"))


def generate_dispute_letter(
    user_email: str,
    merchant_domain: str,
    amount: float,
    transaction_date: datetime,
    reason: str,
    evidence_hashes: List[str],
) -> str:
    """Generate dispute letter PDF.

    Args:
        user_email: User's email
        merchant_domain: Merchant domain
        amount: Transaction amount
        transaction_date: Transaction date
        reason: Dispute reason
        evidence_hashes: List of evidence hashes

    Returns:
        Path to generated PDF
    """
    template = template_env.get_template("dispute_letter.j2")

    html_content = template.render(
        user_email=user_email,
        merchant_domain=merchant_domain,
        amount=amount,
        transaction_date=transaction_date.strftime("%Y-%m-%d"),
        reason=reason,
        evidence_hashes=evidence_hashes,
        generated_date=datetime.now().strftime("%Y-%m-%d"),
    )

    # Generate PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"dispute_{timestamp}.pdf"
    pdf_path = DISPUTES_DIR / pdf_filename

    if WEASYPRINT_AVAILABLE:
        HTML(string=html_content).write_pdf(pdf_path)
        logger.info(f"Generated dispute letter: {pdf_path}")
    else:
        # Write HTML as fallback when WeasyPrint is not available
        html_path = DISPUTES_DIR / f"dispute_{timestamp}.html"
        html_path.write_text(html_content)
        logger.warning("WeasyPrint not available, saving HTML instead of PDF")
    
    return f"{settings.base_url}/static/disputes/{pdf_filename}"


def zip_evidence(capture_ids: List[int], db: Session) -> str:
    """Create evidence ZIP file from captures.

    Args:
        capture_ids: List of capture IDs
        db: Database session

    Returns:
        Path to generated ZIP
    """
    captures = db.query(Capture).filter(Capture.id.in_(capture_ids)).all()

    if not captures:
        logger.warning("No captures found for evidence ZIP")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"evidence_{timestamp}.zip"
    zip_path = DISPUTES_DIR / zip_filename

    # Create ZIP
    with zipfile.ZipFile(zip_path, "w") as zf:
        for capture in captures:
            # Add metadata
            metadata = (
                f"Capture ID: {capture.id}\n"
                f"SHA256: {capture.sha256}\n"
                f"Created: {capture.created_at}\n"
                f"Image URL: {capture.image_url or 'N/A'}\n"
                f"HTML URL: {capture.html_snapshot_url or 'N/A'}\n"
            )
            zf.writestr(f"capture_{capture.id}_metadata.txt", metadata)

    logger.info(f"Created evidence ZIP: {zip_path}")
    return f"{settings.base_url}/static/disputes/{zip_filename}"


def create_dispute(
    db: Session,
    user_id: int,
    transaction_id: int,
    reason: str,
    capture_ids: List[int],
) -> Dispute:
    """Create a dispute with letter and evidence.

    Args:
        db: Database session
        user_id: User ID
        transaction_id: Transaction ID
        reason: Dispute reason
        capture_ids: List of capture IDs for evidence

    Returns:
        Created Dispute instance
    """
    # Get transaction
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction or transaction.user_id != user_id:
        raise ValueError("Transaction not found")

    # Get user email
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()

    # Get evidence hashes
    captures = db.query(Capture).filter(Capture.id.in_(capture_ids)).all()
    evidence_hashes = [c.sha256 for c in captures]

    # Generate letter PDF
    letter_pdf_url = generate_dispute_letter(
        user_email=user.email,
        merchant_domain=transaction.merchant_domain,
        amount=transaction.amount,
        transaction_date=transaction.created_at,
        reason=reason,
        evidence_hashes=evidence_hashes,
    )

    # Generate evidence ZIP
    evidence_zip_url = zip_evidence(capture_ids, db) if capture_ids else None

    # Create dispute
    dispute = Dispute(
        user_id=user_id,
        transaction_id=transaction_id,
        reason=reason,
        letter_pdf_url=letter_pdf_url,
        evidence_zip_url=evidence_zip_url,
        status=DisputeStatus.DRAFT,
    )

    db.add(dispute)
    db.commit()
    db.refresh(dispute)

    logger.info(f"Created dispute {dispute.id} for transaction {transaction_id}")
    return dispute

