"""Main FastAPI application."""

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.logging import setup_logging
from app.routes import (
    auth,
    captures,
    detect,
    disputes,
    impact,
    merchants,
    payments,
    users,
    virtual_cards,
)
from app.schemas.common import HealthResponse

# Setup logging
setup_logging()

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="See-Through Checkout API",
    description="Detect dark patterns and protect yourself from hidden fees",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception:
    # Directory might not exist yet
    pass

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(detect.router)
app.include_router(captures.router)
app.include_router(merchants.router)
app.include_router(virtual_cards.router)
app.include_router(payments.router)
app.include_router(disputes.router)
app.include_router(impact.router)


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to See-Through Checkout API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", timestamp=datetime.now())

