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

## Step 9 — Custom Pricing Engine

### How the pricing system works

Top5 Fantasy uses an **app-owned custom pricing model** — no dependency on FPL prices, no scraping, no external fantasy price feeds. Prices are computed from data we already have: player position, team quality, and recent fantasy output.

### Initial price formula

```
raw_price = POSITION_BASE[position]
          + STRENGTH_BONUS[team.strength]      # team.strength is 1–5
          + SC_BONUS[starter_confidence]        # player.starter_confidence is 1–5
price = round_to_nearest_0.5(clamp(raw_price, POSITION_MIN, POSITION_MAX))
```

**Position base prices (neutral team, regular starter):**

| Position | Base | Min | Max |
|----------|------|-----|-----|
| GK  | £4.5 | £3.5 | £6.5 |
| DEF | £4.5 | £3.5 | £8.0 |
| MID | £5.5 | £4.0 | £11.0 |
| FWD | £6.0 | £4.5 | £12.0 |

**Team strength bonus (team.strength 1–5):**

| Strength | Bonus | Example |
|----------|-------|---------|
| 1 | -£1.0 | Newly promoted, relegation candidates |
| 2 | -£0.5 | Lower mid-table |
| 3 | ±£0.0 | Average mid-table (default) |
| 4 | +£1.0 | Regular top-half |
| 5 | +£2.5 | Elite clubs (City, Real, Bayern …) |

**Starter confidence bonus (player.starter_confidence 1–5):**

| SC | Bonus | Meaning |
|----|-------|---------|
| 1 | -£1.0 | Fringe player |
| 2 | -£0.5 | Rotation |
| 3 | ±£0.0 | Regular starter (default at season start) |
| 4 | +£0.5 | Nailed-on starter |
| 5 | +£1.5 | Star nailed-on starter |

At season start, all players default to `starter_confidence = 3` so initial prices are driven by position + team quality only.

**Example prices:**
- FWD, strength-5 team, SC 3: £6.0 + £2.5 + £0.0 = **£8.5**
- FWD, strength-5 team, SC 5: £6.0 + £2.5 + £1.5 = **£10.0**
- DEF, strength-1 team, SC 2: £4.5 - £1.0 - £0.5 = **£3.5** (at min)
- MID, strength-3 team, SC 3: £5.5 + £0.0 + £0.0 = **£5.5**

### Weekly price update model

Run after each gameweek is scored. Price moves by **±£0.1** based on form.

```
form_score = weighted_avg(fantasy_points[-5 GWs], weights=[5,4,3,2,1])
form_delta = player.form_score - avg_form_score_for_position

form_delta ≥ +1.5 → price rises by £0.1
form_delta ≤ -1.5 → price drops by £0.1
in between         → no change
```

**Rules:**
- Max movement per GW: **±£0.2** (hard cap)
- Min appearances in form window for price change: **2** (sparse data protection)
- Prices stay within PRICE_MIN / PRICE_MAX bounds at all times
- `form_score` and `starter_confidence` are updated on every player every GW (even when no price change occurs)

### Sparse / incomplete data handling

| Situation | Behaviour |
|-----------|-----------|
| Player has < 2 appearances in form window | No price change; form_score written as 0.0 |
| Player has no `player_match_stats` rows at all | No price change; form_score = 0.0 |
| `fantasy_points` is 0 (scoring not yet run) | All players get form_score=0; no price changes → stable season-start state |
| New player added mid-season | Gets initial price from `init-prices`; 0.0 form_score until match data arrives |

### Recalculation timing (MVP)

**Manual via CLI** — run after each gameweek is FINISHED/SCORING.
No background workers in MVP. Scoring job (Step X) triggers this as part of its GW finalization.

### Generating initial prices locally

```bash
# From apps/api/

# Preview without writing
python scripts/pricing.py init-prices --season 2024-25 --preview

# Apply initial prices
python scripts/pricing.py init-prices --season 2024-25
```

### Running weekly price updates

```bash
# From apps/api/

# Preview GW 5 price changes without writing
python scripts/pricing.py update-prices --season 2024-25 --gameweek 5 --preview

# Apply GW 5 price changes
python scripts/pricing.py update-prices --season 2024-25 --gameweek 5
```

### Pricing service structure

```
services/pricing/
  __init__.py
  constants.py    ← all tunable numbers (bases, bonuses, thresholds, step sizes)
  utils.py        ← round_to_half, clamp_price, weighted_average
  signals.py      ← compute_form_score, compute_starter_confidence (DB reads)
  initial.py      ← compute_initial_price (pure), apply_initial_prices (DB write)
  weekly.py       ← compute_price_delta (pure), apply_weekly_updates (DB write)
  history.py      ← record_price_change (upsert to price_history)
```

### What is intentionally simplified in MVP

- **No ownership-based market movement** — price is purely performance-driven.
- **No fixture difficulty modifier** — would require a more complex rating system.
- **No transfer momentum** — real FPL prices can rise just from being widely transferred in; we skip this.
- **Manual recalculation** — background workers and auto-triggers come later.
- **`team.strength` is set manually** at season start (1–5 per club). Admin can update it.

---

## Step 8 — Top5 Fantasy Gameweeks

### What is a Top5 Fantasy Gameweek?

A Top5 Fantasy Gameweek is an **app-defined 7-day window** — not tied to any single league's official matchday. One GW covers matches across all five leagues (PL, La Liga, Bundesliga, Serie A, Ligue 1) that kick off within that window.

**Window shape:** Friday 06:00 UTC → Thursday 23:59:59 UTC

This captures:
- The main weekend round (Fri/Sat/Sun fixtures)
- Any midweek round in that same week (Mon–Thu fixtures)

Users get one lock deadline, one captain choice, and one scoring window per week.

### Lock Deadline

`deadline_at` = earliest fixture kickoff in the GW **minus 60 minutes**.

Before fixtures are assigned, `deadline_at` defaults to `start_at - 1 hour`.
After `python scripts/gameweeks.py assign` runs, it is updated to reflect the actual first kickoff.

**Rule users see:** "Lock is 1 hour before the first game."

### Gameweek Status Lifecycle

```
UPCOMING → LOCKED → ACTIVE → SCORING → FINISHED
```

| Status | Meaning | Triggered when |
|--------|---------|----------------|
| `UPCOMING` | Not yet locked | now < deadline_at |
| `LOCKED` | Transfers/lineups frozen | now >= deadline_at |
| `ACTIVE` | Matches in progress | now >= start_at |
| `SCORING` | All matches done, awaiting points | now >= end_at + 3h |
| `FINISHED` | Points computed and final | Set by scoring job (Step X) |

### How Gameweeks Are Generated

1. The CLI script creates one GW record per calendar week for the season.
2. Windows are fixed (Fri 06:00 → Thu 23:59:59 UTC) regardless of whether fixtures fall in them.
3. Fixture assignment fills in actual kickoff times and updates the deadline.

### How Fixtures Are Assigned

- `assign_fixtures_to_gameweeks` matches each fixture's `kickoff_at` to the GW window it falls in.
- Postponed or cancelled fixtures are cleared to `gameweek_id = NULL`.
- Safe to rerun — handles reschedules automatically.
- Fixtures with no matching window (pre-season, internationals, etc.) remain unassigned.

### Postponed / Rescheduled Fixtures

- When a fixture is postponed, `FixtureStatus` becomes `POSTPONED` and `gameweek_id` is cleared.
- When rescheduled, football-data.org returns a new `kickoff_at`.
- Re-running `assign` picks it up and places it in the correct GW automatically.
- No special handling needed — idempotent assignment does the right thing.

### Midweek Fixtures

Midweek rounds (Tue/Wed/Thu) fall in the **same GW window** as the preceding weekend round.
Users lock on Friday. They see midweek results scored in the same GW. This is intentional —
it mirrors how FPL works and keeps the weekly loop simple.

### Generating Gameweeks Locally

```bash
# From apps/api/

# Step 1: ingest fixtures from football-data.org
python scripts/sync.py fixtures

# Step 2: generate gameweek windows for the season
python scripts/gameweeks.py generate --season 2024-25

# Step 3: assign ingested fixtures to gameweeks
python scripts/gameweeks.py assign --season 2024-25

# Step 4: set statuses and is_current flag
python scripts/gameweeks.py refresh --season 2024-25

# Re-run assign + refresh any time after a re-sync (handles reschedules)
python scripts/gameweeks.py assign --season 2024-25
python scripts/gameweeks.py refresh --season 2024-25
```

### Gameweek API Routes

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/gameweeks` | List all GWs for active season |
| `GET` | `/api/v1/gameweeks/current` | Current GW (is_current=True) |
| `GET` | `/api/v1/gameweeks/{id}` | GW detail |
| `GET` | `/api/v1/gameweeks/{id}/fixtures` | Fixtures assigned to a GW |

### What Is Intentionally Deferred

- **Scoring computation** — Step X. `SCORING → FINISHED` transition is left for the scoring job.
- **Automatic status refresh** — no background worker yet. Run `python scripts/gameweeks.py refresh` manually or via a cron job.
- **Double gameweeks** — treated as one GW window. No special handling in MVP.
- **International breaks** — GW windows still exist but will have zero fixtures assigned. Fine for MVP.

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
