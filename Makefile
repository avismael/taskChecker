.PHONY: install migrate seed test lint run verify docker-up docker-down docker-logs

install:
	python -m pip install -e '.[dev]'

test:
	python -m pytest

migrate:
	python -m alembic -c backend/alembic.ini upgrade head

seed:
	python -m backend.app.scripts.seed

lint:
	python -m ruff check backend

run:
	python -m uvicorn backend.app.main:app --reload --port 8080

verify: lint test

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f app db
