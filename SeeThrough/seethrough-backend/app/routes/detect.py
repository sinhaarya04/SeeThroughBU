"""Detection routes."""

import json
import logging
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.deps import DBSession
from app.models.capture import Capture
from app.models.checkout import Checkout
from app.models.merchant import Merchant
from app.models.risk_event import RiskEvent, RiskEventKind
from app.schemas.detect import CleanOverlay, RiskEventOut, ScanResponse
from app.services.detector import analyze_checkout
from app.services.evidence import save_html_snapshot, save_image
from app.services.ocr import extract_text
from app.services.risk import calculate_risk_score

router = APIRouter(prefix="/detect", tags=["Detection"])
logger = logging.getLogger(__name__)


@router.post("/scan", response_model=ScanResponse)
async def scan_checkout(
    url: str = Form(...),
    image: Optional[UploadFile] = File(None),
    html_snapshot: Optional[str] = Form(None),
    db: DBSession = None,
):
    """Scan a checkout page for dark patterns.

    Args:
        url: Checkout page URL
        image: Optional screenshot image
        html_snapshot: Optional HTML content
        db: Database session
    """
    logger.info(f"Scanning checkout: {url}")

    # Parse domain
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    # Get or create merchant
    merchant = db.query(Merchant).filter(Merchant.domain == domain).first()
    if not merchant:
        merchant = Merchant(domain=domain, display_name=domain, risk_score=0.0)
        db.add(merchant)
        db.commit()
        db.refresh(merchant)

    # Create checkout
    checkout = Checkout(merchant_id=merchant.id, url=url)
    db.add(checkout)
    db.commit()
    db.refresh(checkout)

    # Extract text from image if provided
    ocr_text = ""
    image_url = None
    image_hash = None

    if image:
        image_bytes = await image.read()
        ocr_text = extract_text(image_bytes)
        image_url, image_hash = save_image(image_bytes, checkout.id)

    # Process HTML snapshot if provided
    html_url = None
    html_hash = None

    if html_snapshot:
        html_url, html_hash = save_html_snapshot(html_snapshot, checkout.id)

    # Create capture
    capture_hash = image_hash or html_hash or "no_evidence"
    capture = Capture(
        checkout_id=checkout.id,
        image_url=image_url,
        html_snapshot_url=html_url,
        sha256=capture_hash,
    )
    db.add(capture)
    db.commit()

    # Combine text for analysis
    combined_text = f"{ocr_text}\n\n{html_snapshot or ''}"

    # Analyze for dark patterns
    detected_events = analyze_checkout(combined_text, url, domain)

    # Calculate risk score
    risk_score = calculate_risk_score(detected_events)

    # Store risk events
    for event in detected_events:
        risk_event = RiskEvent(
            checkout_id=checkout.id,
            kind=RiskEventKind(event["kind"]),
            score=event["score"],
            detail_json=json.dumps(event["detail"]),
        )
        db.add(risk_event)

    # Update merchant risk score
    merchant.risk_score = max(merchant.risk_score, risk_score)
    db.commit()

    # Build clean overlay
    callouts = []
    true_total = None

    for event in detected_events:
        if event["kind"] == "HIDDEN_FEE":
            callouts.append("Hidden fees detected")
        elif event["kind"] == "TRIAL_AUTORENEW":
            trial_days = event["detail"].get("trial_days")
            if trial_days:
                callouts.append(f"Auto-renews in {trial_days} days")
            else:
                callouts.append("Auto-renewal trial detected")
        elif event["kind"] == "PRECHECKED_ADDON":
            callouts.append("Pre-checked add-ons found")
        elif event["kind"] == "LOOKALIKE_DOMAIN":
            brand = event["detail"].get("suspected_brand")
            callouts.append(f"Domain similar to {brand}")

    clean_overlay = CleanOverlay(true_total=true_total, callouts=callouts)

    # Format response events
    response_events = [
        RiskEventOut(kind=event["kind"], score=event["score"], detail=event["detail"])
        for event in detected_events
    ]

    return ScanResponse(
        checkout_id=checkout.id,
        domain=domain,
        risk_score=risk_score,
        events=response_events,
        clean_overlay=clean_overlay,
    )

