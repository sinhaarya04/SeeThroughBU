"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def demo_user(client):
    """Create a demo user and return credentials."""
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    assert response.status_code == 201
    data = response.json()
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }


@pytest.fixture
def auth_headers(demo_user):
    """Get authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {demo_user['access_token']}"}

