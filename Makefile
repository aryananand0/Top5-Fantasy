# Top5 Fantasy — local dev convenience commands
# Run all commands from the repo root.

.PHONY: db db-stop db-logs migrate sync api web setup help

# ── Postgres ──────────────────────────────────────────────────────────────────

db:
	docker compose up -d db
	@echo "Postgres starting on localhost:5432 (db=top5fantasy, user=postgres, password=postgres)"
	@echo "Wait a few seconds, then run: make migrate"

db-stop:
	docker compose stop db

db-logs:
	docker compose logs -f db

# ── Backend ───────────────────────────────────────────────────────────────────

migrate:
	cd apps/api && alembic upgrade head

sync:
	@echo "Syncing competitions, teams, players, fixtures from football-data.org..."
	cd apps/api && python3 scripts/sync.py all

api:
	cd apps/api && uvicorn main:app --reload --port 8000

# ── Frontend ──────────────────────────────────────────────────────────────────

web:
	cd apps/web && npm run dev

# ── First-time setup ──────────────────────────────────────────────────────────

setup:
	@echo "==> Installing Python dependencies"
	cd apps/api && pip install -r requirements.txt
	@echo "==> Installing Node dependencies"
	cd apps/web && npm install
	@echo ""
	@echo "Done. Next steps:"
	@echo "  1. Paste your FOOTBALL_DATA_API_KEY in apps/api/.env"
	@echo "  2. make db        — start Postgres"
	@echo "  3. make migrate   — apply DB migrations"
	@echo "  4. make sync      — pull soccer data (requires API key)"
	@echo "  5. make api       — start FastAPI on :8000"
	@echo "  6. make web       — start Next.js on :3000"

# ── Help ──────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "Top5 Fantasy — make targets"
	@echo ""
	@echo "  make setup     Install all dependencies (run once)"
	@echo "  make db        Start Postgres via Docker"
	@echo "  make db-stop   Stop Postgres"
	@echo "  make db-logs   Tail Postgres logs"
	@echo "  make migrate   Run Alembic migrations"
	@echo "  make sync      Pull soccer data from football-data.org"
	@echo "  make api       Start FastAPI dev server on :8000"
	@echo "  make web       Start Next.js dev server on :3000"
	@echo ""
