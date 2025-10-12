.PHONY: up down logs migrate seed test format lint clean

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f api

migrate:
	docker-compose exec api alembic upgrade head

seed:
	docker-compose exec api python -m app.seed

test:
	docker-compose exec api pytest tests/ -v

format:
	black app tests
	isort app tests

lint:
	ruff check app tests
	black --check app tests
	isort --check app tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

