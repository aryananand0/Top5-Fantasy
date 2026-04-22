# Top5 Fantasy — API

FastAPI backend for the Top5 Fantasy season-long fantasy soccer manager.

---

## Stack

| Tool | Purpose |
|---|---|
| FastAPI | REST API framework |
| SQLAlchemy 2.x | ORM (sync, psycopg v3 driver) |
| Alembic | Database migrations |
| Pydantic v2 + pydantic-settings | Request/response validation, config |
| psycopg v3 | PostgreSQL driver |
| APScheduler | Background jobs *(added in Step 7)* |
| python-jose | JWT *(added in Step 6)* |
| passlib + bcrypt | Password hashing *(added in Step 6)* |
| httpx | Async HTTP client for external APIs *(added in Step 7)* |

---

## Setup

```bash
# From apps/api/
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Install production deps
pip install -r requirements.txt

# Install dev/test deps
pip install -r requirements-dev.txt

# Copy and fill in environment variables
cp .env.example .env
# Edit .env — at minimum set DATABASE_URL, SECRET_KEY

# Run the server (development)
uvicorn main:app --reload
# API: http://localhost:8000
# Interactive docs: http://localhost:8000/docs  (only in DEBUG=true mode)
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | `postgresql+psycopg://user:pass@host/db` |
| `SECRET_KEY` | Yes | Random hex string, used for JWT signing |
| `ENVIRONMENT` | No | `development` / `staging` / `production` |
| `DEBUG` | No | Enables SQL echo and `/docs` endpoint |
| `FRONTEND_URL` | No | Exact origin for CORS (default: `http://localhost:3000`) |
| `FOOTBALL_DATA_API_KEY` | No | football-data.org API key (needed for Step 7+) |
| `THESPORTSDB_API_KEY` | No | Optional image enrichment |
| `REDIS_URL` | No | Not used in MVP; leave blank |

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Migrations

Alembic manages the database schema. All migrations live in `alembic/versions/`.

```bash
# From apps/api/

# Generate a new migration after changing models
alembic revision --autogenerate -m "describe_the_change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Check current migration state
alembic current
```

**Migration batches (Step 4 plan):**

| Batch | Files | Tables |
|---|---|---|
| 1 | 001, 002, 003 | seasons, competitions, teams, players |
| 2 | 004, 005 | gameweeks, fixtures |
| 3 | 006, 007 | users, squads, squad_players |
| 4 | 008, 009 | lineups, player_match_stats |
| 5 | 010, 011 | transfers, user_gameweek_scores |
| 6 | 012, 013 | mini_leagues, league_members, price_history |

---

## Project Structure

```
apps/api/
├── api/
│   └── v1/
│       ├── router.py          ← registers all v1 routes
│       └── routes/
│           └── health.py      ← /health and /info (no auth)
├── core/
│   ├── config.py              ← pydantic-settings Settings class
│   └── dependencies.py        ← FastAPI Annotated deps (DBSession, AppSettings)
├── db/
│   └── session.py             ← engine, SessionLocal, get_db(), check_db_connection()
├── models/                    ← SQLAlchemy ORM models (Step 4)
│   ├── __init__.py
│   └── *.py
├── schemas/
│   ├── common.py              ← MessageResponse, ErrorResponse
│   └── *.py                   ← domain schemas added per step
├── services/                  ← business logic modules (added per step)
├── tests/
│   ├── conftest.py            ← fixtures (mock_db, TestClient)
│   └── test_health.py
├── alembic/
│   ├── env.py                 ← loads DB URL from settings, imports all models
│   └── versions/              ← generated migration files
├── alembic.ini
├── main.py                    ← FastAPI app, CORS, lifespan, exception handlers
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

---

## Adding a New Route Module

1. Create `api/v1/routes/example.py` with an `APIRouter`
2. Add any request/response schemas to `schemas/example.py`
3. Add business logic to `services/example.py`
4. Register in `api/v1/router.py`:
   ```python
   from api.v1.routes import example
   router.include_router(example.router, prefix="/example", tags=["example"])
   ```

**Design rules:**
- Routes are thin: validate input, call a service, return a response
- Services contain business logic; they do not query the DB directly
- DB queries go in repository functions (added when needed — no empty repo files)
- Auth is enforced via a FastAPI dependency on the route (added in Step 6)
- Every protected route reads `user_id` from the JWT, never from the request body

---

## Running Tests

```bash
# From apps/api/
pytest

# Verbose output
pytest -v

# A specific file
pytest tests/test_health.py
```

Unit tests use a mocked DB and do not require a running PostgreSQL instance.

---

## API Conventions

- All routes are prefixed `/api/v1/`
- Responses are JSON
- HTTP status codes: 200, 201, 400, 401, 403, 404, 422, 500
- List endpoints are paginated (no unbounded responses)
- Internal database IDs are not exposed where a slug/code is appropriate
- The API is designed to be consumable by any HTTP client (web or future mobile app)
