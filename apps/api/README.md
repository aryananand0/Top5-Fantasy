# Top5 Fantasy — API (FastAPI)

The backend REST API and background scheduler. Handles all business logic, database access, external API sync, and gameweek scoring.

---

## Stack

| Tool | Purpose |
|---|---|
| FastAPI | REST API framework |
| SQLAlchemy | ORM for PostgreSQL |
| Alembic | Database migrations |
| Pydantic v2 | Request/response validation |
| APScheduler | Background jobs for data sync and scoring |
| python-jose | JWT signing and verification |
| passlib + bcrypt | Password hashing |
| httpx | Async HTTP client for external API calls |
| python-dotenv | Load `.env` in development |
| uvicorn | ASGI server |

---

## Setup

```bash
# From this directory (apps/api)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment variables
cp ../../.env.example .env
# Fill in DATABASE_URL, JWT_SECRET, FOOTBALL_DATA_API_KEY

# Run the server
uvicorn main:app --reload
# Runs on http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

---

## Dependency Strategy

### Add now (in requirements.txt)

```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
alembic
pydantic[email]
python-jose[cryptography]
passlib[bcrypt]
httpx
apscheduler
python-dotenv
```

### Add when the need arises

| Package | When |
|---|---|
| `redis-py` | If caching is introduced (not in MVP) |
| `celery` | If background jobs outgrow APScheduler (not in MVP) |
| `sentry-sdk` | When error monitoring is needed pre-launch |
| `pytest` + `httpx` | When writing API tests |
| `slowapi` | If rate limiting on the API is needed |

### Do not add

- `celery` or `rq` — APScheduler is sufficient for MVP
- `redis` — no caching layer in MVP
- Any ORM beyond SQLAlchemy
- `aiofiles` or async file I/O — not needed
- Anything that requires a broker or message queue

---

## Folder Structure (to be created when building begins)

```
apps/api/
├── main.py              FastAPI app entry point, router registration
├── config.py            Settings loaded from environment variables
├── database.py          SQLAlchemy engine and session setup
├── models/              SQLAlchemy ORM models (one file per domain)
├── schemas/             Pydantic request and response schemas
├── routers/             Route handlers (one file per domain)
├── services/            Business logic (one file per domain)
├── repositories/        Database query functions
├── jobs/                Background scheduler jobs
├── external/            Clients for football-data.org and TheSportsDB
├── tests/               pytest test files
├── alembic/             Database migration scripts
├── requirements.txt     Pinned production dependencies
└── .env                 Local environment variables (not committed)
```

---

## Key Design Rules

- Routes are thin: validate input, call a service, return a response.
- Services contain business logic; they do not touch the database directly.
- Repositories contain all database queries; they do not contain logic.
- External API calls only happen inside `jobs/` — never inside a route.
- Every route that requires authentication reads the user ID from the validated JWT, never from the request body.

---

## Background Jobs (overview)

| Job | Schedule | Purpose |
|---|---|---|
| Fixture sync | Daily | Pull upcoming and completed fixtures |
| Result sync | Every 3–6h on match days | Pull match results and player stats |
| Score calculation | After result sync | Compute gameweek points for all users |
| Badge enrichment | Weekly | Fetch club/player images from TheSportsDB |

Jobs run inside the same process as the API using APScheduler. They can be extracted later if needed.

---

## API Design Rules

- All endpoints return JSON.
- Use standard HTTP status codes (200, 201, 400, 401, 403, 404, 422, 500).
- Paginate all list endpoints — no unbounded responses.
- Prefix all routes: `/api/v1/...`
- Never expose internal database IDs in public-facing resources where a slug is appropriate.

---

## Mobile Compatibility

The API is designed to be consumed by any HTTP client. A future React Native or Flutter mobile app will use the same endpoints with the same JWT auth (stored in secure device storage instead of an HTTP-only cookie).

No backend changes are required to support a mobile app.
