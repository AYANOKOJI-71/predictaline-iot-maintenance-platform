VENV ?= .venv
PNPM := npx --yes pnpm@10.6.3

.PHONY: bootstrap api web lint test build compose-up compose-down

bootstrap:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -e ".[dev]"
	cd apps/web && $(PNPM) install --frozen-lockfile=false

api:
	$(VENV)/bin/uvicorn predictaline.main:app --app-dir apps/api/src --host 0.0.0.0 --port $${API_PORT:-4901}

web:
	cd apps/web && $(PNPM) dev

lint:
	$(VENV)/bin/ruff check .

test:
	$(VENV)/bin/pytest -q
	cd apps/web && $(PNPM) test

build:
	cd apps/web && $(PNPM) build

compose-up:
	docker compose up --build

compose-down:
	docker compose down
