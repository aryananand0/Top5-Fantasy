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

## Step 10 — Squad Builder Backend

### How squad creation works

Users build one 11-player squad per season from the cross-league player pool.
The initial pick is free. After the season locks (first GW reaches LOCKED status),
the squad can only be changed via the transfer system (Step 13).

### Squad rules (MVP)

| Rule | Value |
|------|-------|
| Squad size | 11 players |
| Budget cap | £100.0 |
| Formation | 1 GK · 3 DEF · 4 MID · 3 FWD (fixed) |
| Max per club | 2 players |
| Squads per user | 1 per season |
| Bench | None in MVP |

### How prices are used

- Each player's `current_price` at the moment of squad creation is stored as `purchase_price` on `squad_players`.
- `budget_remaining = £100.0 − sum(purchase_prices)`.
- Re-syncing player prices does NOT retroactively change a user's `purchase_price` — that's locked at acquisition time.

### Squad API routes

All routes require authentication (`Authorization: Bearer <token>`).

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/squad` | Get my current squad |
| `POST` | `/api/v1/squad` | Create my squad (once per season) |
| `PUT` | `/api/v1/squad` | Replace my squad (before season locks) |
| `GET` | `/api/v1/players` | Browse available players |

### Example API usage

**Create a squad:**
```http
POST /api/v1/squad
Authorization: Bearer <token>
Content-Type: application/json

{
  "player_ids": [101, 202, 303, 404, 505, 606, 707, 808, 909, 1010, 1111],
  "name": "The Invincibles"
}
```

**Response (201):**
```json
{
  "id": 42,
  "name": "The Invincibles",
  "budget_remaining": 3.5,
  "total_cost": 96.5,
  "total_points": 0,
  "overall_rank": null,
  "free_transfers_banked": 1,
  "players": [
    {
      "player_id": 101,
      "name": "Alisson Becker",
      "position": "GK",
      "team_name": "Liverpool",
      "purchase_price": 5.5,
      "current_price": 5.5,
      ...
    },
    ...
  ]
}
```

**Validation error (400):**
```json
{
  "detail": {
    "errors": [
      "Squad costs £105.5 — £5.5 over the £100.0 budget.",
      "Need exactly 1 GK (you have 0).",
      "Maximum 2 players per club (Manchester City has 3)."
    ]
  }
}
```

**Browse players:**
```http
GET /api/v1/players?position=FWD&page=1&per_page=20
Authorization: Bearer <token>
```

### Validation rules (centralized in `services/squads/validation.py`)

The same `validate_squad()` function is used by squad creation, squad replacement,
and will be reused for transfer previews (Step 13) without modification.

Checks run in order:
1. **Pre-DB**: exact count (11), no duplicate IDs
2. **Player lookup**: all IDs must exist in the active season
3. **Position counts**: 1 GK, 3 DEF, 4 MID, 3 FWD exactly
4. **Budget**: `sum(current_price) ≤ £100.0`
5. **Club limit**: max 2 players per real-world club
6. **Availability**: no players with `is_available=False`

All violations are collected and returned together — users see every error at once.

### Create vs. Replace behavior

- `POST /squad` — creates the squad; returns `409` if one already exists.
- `PUT /squad` — replaces all active players (soft-deletes old rows, inserts new ones). Returns `403` if any GW is LOCKED or beyond. The soft-delete preserves history for future transfer audit.
- After the season locks, only the transfer system (Step 13) can change the squad.

### Squad service structure

```
services/squads/
  __init__.py
  constants.py    ← BUDGET_CAP, SQUAD_SIZE, POSITION_REQUIREMENTS, MAX_PER_CLUB
  validation.py   ← validate_player_ids(), validate_squad() — pure, no DB
  service.py      ← create_squad(), replace_squad(), get_squad_detail(), list_players()
```

### What is intentionally deferred

- **Captain / vice-captain** — Step 12. Fields exist on `gameweek_lineups` already.
- **Transfer system** — Step 13. `SquadPlayer.left_gameweek_id` and `transfers` table are ready.
- **Bench / auto-subs** — not in MVP scope.
- **Free transfers banking** — Step 13. `free_transfers_banked` field exists, logic not yet applied.
- **Squad points / ranking** — Step X (scoring). `total_points` and `overall_rank` fields exist.

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

## Step 14 — Scoring Engine

### How the scoring engine works

After match data is ingested, the scoring engine computes fantasy points in three stages:

1. **Per-fixture player scoring** (`compute_fixture_player_points`)
   Reads each `PlayerMatchStats` row, resolves clean sheet eligibility, runs the rules engine,
   and writes `fantasy_points` back to the row.

2. **Lineup aggregation** (`compute_and_save_lineup_points`)
   For each locked gameweek lineup, sums each player's `fantasy_points` across all FINISHED
   fixtures in the gameweek, applies the captain 2× multiplier (or VC fallback), and writes
   `GameweekLineupPlayer.points_scored` and `GameweekLineup.points_scored`.

3. **User gameweek score** (`_upsert_user_gw_score`)
   Subtracts the transfer hit from the lineup total and upserts a `UserGameweekScore` row.
   This is the record that powers leaderboards and the dashboard.

### Target scoring model

| Event | Points |
|-------|--------|
| Starting appearance | +1 |
| 60+ minutes played | +1 (RICH mode only) |
| Goal by FWD | +4 |
| Goal by MID | +5 |
| Goal by DEF / GK | +6 |
| Assist | +3 |
| Clean sheet (DEF / GK) | +4 |
| Yellow card | -1 |
| Red card | -3 |
| Own goal | -2 |
| Captain | 2× total |

### Scoring modes (RICH vs FALLBACK)

The scoring engine has two modes, set at the gameweek level (`Gameweek.scoring_mode`):

| Mode | When | Differences |
|------|------|-------------|
| `RICH` | Default when full data is available | All rules applied (60+ bonus, clean sheets with 60+ requirement) |
| `FALLBACK` | When data is estimated/incomplete | 60+ bonus skipped; clean sheet requires only `appeared=True` |

A fixture can also override to FALLBACK via `Fixture.data_quality_status = ESTIMATED`,
regardless of the GW setting. This means a GW can be RICH overall but score one incomplete
fixture in FALLBACK mode automatically.

### Captain and vice-captain rules

- **Captain** gets 2× their total GW fantasy points.
- **Vice-captain** gets 2× **only if** the captain did not appear in any fixture in the GW.
  "Did not appear" = no `PlayerMatchStats` row with `appeared=True` for any GW fixture.
- If neither captain nor VC appeared, no 2× is applied (edge case).

### Clean sheet rule

| Mode | Eligibility |
|------|-------------|
| RICH | Position must be DEF/GK + `minutes_played >= 60` + team conceded 0 |
| FALLBACK | Position must be DEF/GK + `appeared=True` + team conceded 0 |

Clean sheets are always derived from the fixture result (`home_score`/`away_score`).
If the score is not yet confirmed (NULL), no clean sheet is awarded for that fixture.

### Transfer hit deduction

Extra transfers above the free allowance are deducted from the user's GW score:
`final_points = lineup_points - transfer_cost_applied`

The `transfer_cost_applied` field is set by the transfer service at apply time.
The scoring engine reads it directly from `GameweekLineup.transfer_cost_applied`.

### Persistence

| Table | Written by | What |
|-------|-----------|------|
| `player_match_stats.fantasy_points` | `compute_fixture_player_points` | Per player per fixture |
| `player_match_stats.clean_sheet` | `compute_fixture_player_points` | Resolved clean sheet flag |
| `gameweek_lineup_players.points_scored` | `compute_and_save_lineup_points` | Per player GW total (with 2×) |
| `gameweek_lineups.points_scored` | `compute_and_save_lineup_points` | Lineup total before transfer hit |
| `user_gameweek_scores` | `_upsert_user_gw_score` | Final score, transfer cost, captain bonus, rank |

### Recompute / re-run behaviour

All scoring operations are **idempotent**: re-running with updated data overwrites prior values.
Safe to re-run any time after new fixture data arrives.

Recommended re-run order:
1. `python scripts/sync.py fixtures` — pull latest match results + player stats
2. `python scripts/score.py score-gameweek <id>` — recompute everything
3. `python scripts/score.py finalize-ranks <id>` — reassign ranks

### Running scoring commands

```bash
# From apps/api/

# Score all players in one finished fixture
python scripts/score.py score-fixture 42

# Full gameweek scoring pass (fixtures → lineups → user scores)
python scripts/score.py score-gameweek 5

# Assign rank_global to all users after all GW scores are in
python scripts/score.py finalize-ranks 5

# Recompute one user's GW score (e.g. after manual data fix)
python scripts/score.py recompute-user 5 12
```

### Typical post-match workflow

```bash
# After GW 5 finishes:
python scripts/sync.py fixtures          # 1. Pull latest results from football-data.org
python scripts/score.py score-gameweek 5 # 2. Score everything in GW 5
python scripts/score.py finalize-ranks 5 # 3. Assign global rankings
python scripts/pricing.py update-prices --season 2024-25 --gameweek 5  # 4. Update prices
```

### Scoring API routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/gameweeks/current/score` | Required | Current user's score for current GW |
| `GET` | `/api/v1/gameweeks/{id}/score` | Required | Current user's score for a specific GW |

Returns `202 Accepted` with a `message` field if the scoring job hasn't run yet for that GW.

### Scoring service structure

```
services/scoring/
  __init__.py                   ← public surface: score_gameweek, compute_*, finalize_ranks
  rules.py                      ← pure scoring constants + score_player_fixture() function
  utils.py                      ← resolve_scoring_mode(), resolve_clean_sheet()
  compute_player_points.py      ← compute_fixture_player_points() — scores one fixture
  compute_lineup_points.py      ← compute_and_save_lineup_points() — lineup aggregation
  aggregate_gameweek_scores.py  ← score_gameweek(), finalize_gameweek_ranks()
```

### What is intentionally deferred

- **Global leaderboard surface** — Step 17. `rank_global` is computed here; the UI surfaces it later.
- **Mini-league standings** — Step 16. The `user_gameweek_scores` table powers them; no join logic yet.
- **Automatic scoring triggers** — no cron/worker in MVP. Run `scripts/score.py` manually.
- **Live/in-progress scoring** — no websocket or polling. Scores are written once per GW after all matches.
- **Player form update after scoring** — run `scripts/pricing.py update-prices` after scoring is done.
- **GW status transition to FINISHED** — `score_gameweek` does NOT auto-transition the GW status.
  Run `python scripts/gameweeks.py refresh` after scoring to update statuses.

---

## Step 15 — Dashboard

### Overview

A single aggregated `GET /api/v1/dashboard` endpoint assembles the full dashboard payload
for the authenticated user in one pass. The frontend makes exactly one call on load —
no waterfall requests, no separate score/squad/fixtures calls.

### Response shape

| Field group | Description |
|-------------|-------------|
| `gameweek_*` | Current GW id, number, name, status, deadline |
| `gw_points / gw_raw_points` | Final (after hit) and raw points. `null` until scoring job runs |
| `gw_transfer_cost / gw_captain_bonus` | Deductions and bonus included in the score |
| `gw_rank` | Global rank. `null` until `finalize_gameweek_ranks()` runs |
| `season_points` | Sum of all `UserGameweekScore.points` for this user |
| `captain / vice_captain` | Player name, position, team, GW points (null before scoring) |
| `has_squad / has_lineup / is_editable / can_transfer` | State flags for conditional UI |
| `free_transfers / transfers_made / transfer_hit` | Transfer window summary |
| `budget_remaining` | Squad budget in millions (e.g. `4.5`) |
| `fixtures` | Up to 5 fixtures for the current GW, ordered by kickoff. `has_squad_players=true` when the user has players in either team |

### Response paths

| Condition | Behaviour |
|-----------|-----------|
| No current gameweek | All GW/score fields are `null`; `fixtures=[]` |
| No squad | GW fields populated; squad/lineup/transfer fields are safe defaults |
| Full response | All fields populated from squad, lineup, score, transfer records |

### Editability flags

- `is_editable = gw.status == UPCOMING and (lineup is None or not lineup.is_locked)`
- `can_transfer = gw.status == UPCOMING`

### API route

```
GET /api/v1/dashboard
Authorization: Bearer <token>
→ 200 DashboardSummary
```

### Service structure

```
services/dashboard/
  __init__.py     ← public surface: get_dashboard_summary
  service.py      ← _no_gameweek_response, _no_squad_response, _full_response,
                     _build_captain_info, _get_fixtures
```

### What is intentionally deferred

- **Season team value** — not surfaced (requires summing player prices; deferred to Step 18).
- **Average GW points** — no population-level aggregate on this endpoint.
- **Mini-league standings** — Step 16.
- **Global leaderboard context** — Step 17.

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
