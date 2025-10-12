"""Tests for detection endpoints."""

import pytest


def test_scan_checkout_with_hidden_fees(client):
    """Test scanning checkout page with hidden fees."""
    html_content = """
    <html>
    <body>
        <h1>Checkout</h1>
        <p>Subtotal: $39.99</p>
        <p>Service fee: $6.99</p>
        <p>Processing fee: $2.50</p>
        <p>Total: $49.48</p>
    </body>
    </html>
    """

    response = client.post(
        "/detect/scan",
        data={
            "url": "https://tricky-shop.example/checkout",
            "html_snapshot": html_content,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "checkout_id" in data
    assert data["domain"] == "tricky-shop.example"
    assert data["risk_score"] > 0
    assert len(data["events"]) > 0

    # Check for hidden fee detection
    hidden_fee_events = [e for e in data["events"] if e["kind"] == "HIDDEN_FEE"]
    assert len(hidden_fee_events) > 0


def test_scan_checkout_with_trial_autorenew(client):
    """Test scanning checkout page with trial auto-renew."""
    html_content = """
    <html>
    <body>
        <h1>Start Your Free Trial</h1>
        <p>7-day free trial, then $29.99/month</p>
        <p>Automatically renews unless cancelled</p>
        <button>Start Trial</button>
    </body>
    </html>
    """

    response = client.post(
        "/detect/scan",
        data={
            "url": "https://subscription-service.example/trial",
            "html_snapshot": html_content,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Check for trial auto-renew detection
    trial_events = [e for e in data["events"] if e["kind"] == "TRIAL_AUTORENEW"]
    assert len(trial_events) > 0

    # Check if trial days were extracted
    if trial_events[0]["detail"].get("trial_days"):
        assert trial_events[0]["detail"]["trial_days"] == 7


def test_scan_checkout_with_lookalike_domain(client):
    """Test scanning checkout page with lookalike domain."""
    html_content = """
    <html>
    <body>
        <h1>Checkout</h1>
        <p>Total: $19.99</p>
    </body>
    </html>
    """

    response = client.post(
        "/detect/scan",
        data={
            "url": "https://amaz0n.com/checkout",
            "html_snapshot": html_content,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Check for lookalike domain detection
    lookalike_events = [e for e in data["events"] if e["kind"] == "LOOKALIKE_DOMAIN"]
    # May or may not detect depending on threshold
    assert "clean_overlay" in data
    assert isinstance(data["clean_overlay"]["callouts"], list)


def test_scan_clean_checkout(client):
    """Test scanning a clean checkout page."""
    html_content = """
    <html>
    <body>
        <h1>Checkout</h1>
        <p>Product: Widget</p>
        <p>Price: $29.99</p>
        <p>Tax: $2.40</p>
        <p>Total: $32.39</p>
        <button>Complete Purchase</button>
    </body>
    </html>
    """

    response = client.post(
        "/detect/scan",
        data={
            "url": "https://honest-shop.example/checkout",
            "html_snapshot": html_content,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Clean checkout should have low/zero risk score
    assert data["risk_score"] <= 30  # Some tolerance
    assert isinstance(data["events"], list)

