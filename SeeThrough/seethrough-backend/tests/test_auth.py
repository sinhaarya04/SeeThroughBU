"""Tests for authentication endpoints."""

import pytest


def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "secure123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, demo_user):
    """Test registration with duplicate email fails."""
    response = client.post(
        "/auth/register",
        json={"email": demo_user["email"], "password": "anotherpass"},
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, demo_user):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        json={"email": demo_user["email"], "password": demo_user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client, demo_user):
    """Test login with wrong password fails."""
    response = client.post(
        "/auth/login",
        json={"email": demo_user["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_refresh_token(client, demo_user):
    """Test refreshing access token."""
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": demo_user["refresh_token"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client, auth_headers):
    """Test getting current user profile."""
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data

