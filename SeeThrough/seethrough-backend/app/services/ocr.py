"""OCR service using Tesseract."""

import io
import logging
from typing import Union

from PIL import Image

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Only import pytesseract if OCR is enabled
if settings.ocr_enabled:
    try:
        import pytesseract

        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    except ImportError:
        logger.warning("pytesseract not available, OCR will be disabled")
        settings.ocr_enabled = False


def extract_text(image_bytes: bytes) -> str:
    """Extract text from image using OCR.

    Args:
        image_bytes: Image data as bytes

    Returns:
        Extracted text string
    """
    if not settings.ocr_enabled:
        logger.info("OCR is disabled, returning empty string")
        return ""

    try:
        # Load image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to grayscale for better OCR
        if image.mode != "L":
            image = image.convert("L")

        # Run OCR
        text = pytesseract.image_to_string(image, lang="eng")
        logger.info(f"Extracted {len(text)} characters via OCR")
        return text

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""

