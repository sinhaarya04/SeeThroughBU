# Quick Start Guide

Get the See-Through Checkout backend running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- Terminal/Command prompt access

## Steps

### 1. Start the Backend

```bash
# Navigate to the project directory
cd seethrough-backend

# Start all services (API, Database, Redis)
docker-compose up -d

# Wait ~10 seconds for services to start
sleep 10

# Run database migrations
docker-compose exec api alembic upgrade head

# Seed demo data
docker-compose exec api python -m app.seed
```

### 2. Verify It's Running

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

You should see the interactive Swagger documentation!

### 3. Test the API

#### Option A: Use the Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Click on "POST /auth/register"
3. Click "Try it out"
4. Use these credentials:
   ```json
   {
     "email": "test@example.com",
     "password": "testpass123"
   }
   ```
5. Click "Execute"
6. Copy the `access_token` from the response
7. Click the "Authorize" button at the top
8. Paste your token and click "Authorize"
9. Now try other endpoints!

#### Option B: Use cURL

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Login (or use demo account)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@stc.app", "password": "demo1234"}'

# Save your token
export TOKEN="your_access_token_here"

# Scan a checkout page
curl -X POST http://localhost:8000/detect/scan \
  -F "url=https://tricky-sub.example/checkout" \
  -F 'html_snapshot=<html><body>Free trial for 7 days, then $29.99/month. Service fee: $5.99</body></html>'

# Create a virtual card
curl -X POST http://localhost:8000/virtual-cards/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_domain": "tricky-sub.example",
    "max_amount": 50.0,
    "expires_at": "2025-02-12T00:00:00Z",
    "merchant_lock": true
  }'
```

## Demo Account

The seed script creates a demo user:
- **Email**: `demo@stc.app`
- **Password**: `demo1234`

## Common Commands

```bash
# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Run tests
docker-compose exec api pytest tests/ -v

# Access database
docker-compose exec db psql -U stc -d stc
```

## Troubleshooting

### Port already in use
If port 8000, 5432, or 6379 is already in use, stop those services or modify `docker-compose.yml`.

### Services not starting
```bash
# Check status
docker-compose ps

# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

### Database issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
docker-compose exec api python -m app.seed
```

## Next Steps

1. Read the full [README.md](README.md) for detailed API documentation
2. Explore the interactive API docs at http://localhost:8000/docs
3. Check out the test suite in `tests/` for usage examples
4. Try the complete demo flow in the README

## Project Structure

```
seethrough-backend/
├── app/                    # Main application code
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── models/            # Database models
│   └── main.py            # FastAPI app
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── docker-compose.yml     # Docker services
└── README.md             # Full documentation
```

## Support

- Check logs: `docker-compose logs -f`
- API docs: http://localhost:8000/docs
- Run tests: `docker-compose exec api pytest -v`

---

Happy coding! 🚀

