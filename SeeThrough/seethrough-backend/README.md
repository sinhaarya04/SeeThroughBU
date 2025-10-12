# See-Through Checkout (STC) Backend

A FastAPI-powered service that scans online checkout pages for dark patterns (hidden fees, auto-renew trials, pre-checked upsells, look-alike domains), shows a clean "truth layer," and lets users take protective actions.

## Features

- **🔍 Dark Pattern Detection**: Automatically detects hidden fees, trial auto-renewals, pre-checked add-ons, and lookalike domains
- **💳 Virtual Cards**: Create merchant-locked, spend-capped, auto-expiring virtual cards
- **⚖️ Dispute Kit Generation**: Generate dispute letters with evidence collection
- **📊 Impact Tracking**: Monitor blocked fees, paused subscriptions, and savings
- **🏦 Capital One Integration**: Mocked Nessie API for demo purposes

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI + Uvicorn
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Cache/Queue**: Redis
- **Auth**: JWT (access + refresh tokens), BCrypt password hashing
- **OCR**: Tesseract via pytesseract
- **Testing**: pytest + httpx AsyncClient
- **Deployment**: Docker + docker-compose

## Quick Start

### Prerequisites

- Docker and docker-compose
- Python 3.11+ (for local development)

### Running with Docker (Recommended)

1. **Clone and navigate to the project**:
   ```bash
   cd seethrough-backend
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Start all services**:
   ```bash
   make up
   # Or: docker-compose up -d
   ```

4. **Run migrations and seed data**:
   ```bash
   make migrate
   make seed
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

6. **View logs**:
   ```bash
   make logs
   ```

7. **Stop services**:
   ```bash
   make down
   ```

### Local Development (Without Docker)

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL and Redis locally**, then update `.env`

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Seed database**:
   ```bash
   python -m app.seed
   ```

6. **Start the server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

### Authentication

#### Register a new user
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Dark Pattern Detection

#### Scan a checkout page
```bash
curl -X POST http://localhost:8000/detect/scan \
  -F "url=https://tricky-sub.example/checkout" \
  -F "html_snapshot=<html><body>Free 7-day trial, then $29.99/month. Service fee: $5.99</body></html>"
```

Or with an image:
```bash
curl -X POST http://localhost:8000/detect/scan \
  -F "url=https://tricky-sub.example/checkout" \
  -F "image=@screenshot.png"
```

Response:
```json
{
  "checkout_id": 1,
  "domain": "tricky-sub.example",
  "risk_score": 45,
  "events": [
    {
      "kind": "HIDDEN_FEE",
      "score": 25,
      "detail": {
        "lines": ["service fee: $5.99"],
        "count": 1
      }
    },
    {
      "kind": "TRIAL_AUTORENEW",
      "score": 20,
      "detail": {
        "trial_days": 7,
        "indicators": ["free.*trial", "then.*$"]
      }
    }
  ],
  "clean_overlay": {
    "true_total": null,
    "callouts": [
      "Hidden fees detected",
      "Auto-renews in 7 days"
    ]
  }
}
```

### Virtual Cards

#### Create a virtual card
```bash
curl -X POST http://localhost:8000/virtual-cards/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_domain": "tricky-sub.example",
    "max_amount": 50.0,
    "expires_at": "2025-02-12T00:00:00Z",
    "merchant_lock": true
  }'
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "merchant_domain": "tricky-sub.example",
  "pan_last4": "4892",
  "alias_token": "stc_Xk9p2mN8vL4qR7tY3wZ5",
  "max_amount": 50.0,
  "currency": "USD",
  "expires_at": "2025-02-12T00:00:00Z",
  "status": "ACTIVE",
  "controls": {
    "merchant_lock": true,
    "spend_cap": true,
    "auto_expire": true
  },
  "created_at": "2025-01-12T10:30:00Z"
}
```

#### Freeze a card
```bash
curl -X POST http://localhost:8000/virtual-cards/1/freeze \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Close a card
```bash
curl -X POST http://localhost:8000/virtual-cards/1/close \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Payments

#### Authorize a payment
```bash
curl -X POST http://localhost:8000/payments/authorize \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_domain": "tricky-sub.example",
    "amount": 29.99,
    "virtual_card_id": 1
  }'
```

Response (authorized):
```json
{
  "transaction_id": 1,
  "status": "AUTHORIZED",
  "message": null
}
```

Response (declined):
```json
{
  "transaction_id": 2,
  "status": "DECLINED",
  "message": "Amount $100.0 exceeds card limit $50.0"
}
```

#### List transactions
```bash
curl -X GET "http://localhost:8000/payments/transactions?merchant_domain=shop.example" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Disputes

#### Create a dispute
```bash
curl -X POST http://localhost:8000/disputes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": 1,
    "reason": "Hidden fees were not disclosed during checkout. The final amount charged was $15 higher than shown.",
    "capture_ids": [1, 2]
  }'
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "transaction_id": 1,
  "reason": "Hidden fees were not disclosed...",
  "letter_pdf_url": "http://localhost:8000/static/disputes/dispute_20250112_103000.pdf",
  "evidence_zip_url": "http://localhost:8000/static/disputes/evidence_20250112_103000.zip",
  "status": "DRAFT",
  "created_at": "2025-01-12T10:30:00Z"
}
```

### Impact Summary

#### Get user impact summary
```bash
curl -X GET http://localhost:8000/impact/summary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "blocked_transactions": 5,
  "fees_blocked_usd": 67.45,
  "subscriptions_paused": 2,
  "disputes_filed": 1,
  "estimated_savings_usd": 67.45
}
```

## Demo Flow (Hackathon Script)

Here's a complete end-to-end demo flow:

```bash
# 1. Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@stc.app", "password": "demo1234"}'

# Save the access_token from response
export TOKEN="your_access_token_here"

# 2. Scan a checkout page
curl -X POST http://localhost:8000/detect/scan \
  -F "url=https://tricky-sub.example/checkout" \
  -F 'html_snapshot=<html><body><h1>Checkout</h1><p>7-day free trial</p><p>Then $29.99/month</p><p>Service fee: $6.99</p><p>Processing fee: $2.50</p></body></html>'

# 3. Create a virtual card (merchant-locked, spend-capped)
curl -X POST http://localhost:8000/virtual-cards/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_domain": "tricky-sub.example",
    "max_amount": 35.0,
    "expires_at": "2025-02-12T00:00:00Z",
    "merchant_lock": true
  }'

# Save the card ID
export CARD_ID=1

# 4. Authorize a payment (within limit - succeeds)
curl -X POST http://localhost:8000/payments/authorize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"merchant_domain\": \"tricky-sub.example\",
    \"amount\": 29.99,
    \"virtual_card_id\": $CARD_ID
  }"

# 5. Try to authorize over limit (fails)
curl -X POST http://localhost:8000/payments/authorize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"merchant_domain\": \"tricky-sub.example\",
    \"amount\": 99.99,
    \"virtual_card_id\": $CARD_ID
  }"

# Save the declined transaction ID
export TXN_ID=2

# 6. Create a dispute
curl -X POST http://localhost:8000/disputes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction_id\": $TXN_ID,
    \"reason\": \"Unauthorized charge attempt. Hidden fees were not disclosed.\",
    \"capture_ids\": [1]
  }"

# 7. Check impact summary
curl -X GET http://localhost:8000/impact/summary \
  -H "Authorization: Bearer $TOKEN"
```

## Testing

Run the test suite:

```bash
# Using Docker
make test

# Or locally
pytest tests/ -v
```

Run specific test files:
```bash
pytest tests/test_auth.py -v
pytest tests/test_detect.py -v
pytest tests/test_virtual_card.py -v
pytest tests/test_payments.py -v
pytest tests/test_disputes.py -v
```

## Project Structure

```
seethrough-backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── db.py                # Database session
│   ├── deps.py              # FastAPI dependencies
│   ├── logging.py           # Logging configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routes/              # API route handlers
│   ├── services/            # Business logic
│   │   ├── ocr.py           # OCR service
│   │   ├── detector.py      # Dark pattern detection
│   │   ├── domain.py        # Domain analysis
│   │   ├── risk.py          # Risk scoring
│   │   ├── virtual_card.py  # Virtual card management
│   │   ├── payments.py      # Payment authorization
│   │   ├── dispute.py       # Dispute generation
│   │   └── nessie_mock.py   # Capital One mock
│   ├── security/            # Auth & JWT
│   ├── utils/               # Utility functions
│   └── templates/           # Jinja2 templates
├── tests/                   # Pytest test suite
├── alembic/                 # Database migrations
├── docker-compose.yml       # Docker services
├── Dockerfile               # API container
├── Makefile                 # Development commands
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Environment Variables

See `.env.example` for all available configuration options:

- `APP_ENV`: Environment (local/production)
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OCR_ENABLED`: Enable/disable OCR (true/false)
- `CORS_ORIGINS`: Allowed CORS origins

## Development

### Code Formatting

```bash
make format
```

### Linting

```bash
make lint
```

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

## Demo Credentials

When you run `make seed`, the following demo data is created:

- **User**: `demo@stc.app` / `demo1234`
- **Merchants**:
  - `tricky-sub.example` (Risk Score: 78)
  - `clean-shop.example` (Risk Score: 5)

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ for consumer protection and transparency in online checkout.

