# Top5 Fantasy

A season-long fantasy football manager game built across the top 5 European leagues — Premier League, La Liga, Bundesliga, Serie A, and Ligue 1.

Pick your squad, score points from real matches, and compete in private leagues against your mates.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (React) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Styling | Tailwind CSS |
| Auth | JWT (HTTP-only cookies) |
| Data | football-data.org (free tier) |

---

## Repo Structure

```
top5-fantasy/
├── apps/
│   ├── api/          FastAPI backend — REST API, background sync jobs, scoring logic
│   └── web/          Next.js frontend — all user-facing pages and components
├── docs/             Planning documents and architectural guardrails
├── packages/
│   └── shared/       Shared types and constants (used by both apps when needed)
└── .github/          PR templates and GitHub config
```

---

## Getting Started

### Prerequisites

- Docker (for Postgres) — or a local Postgres 15+ install
- Python 3.11+
- Node.js 20+
- A free [football-data.org](https://www.football-data.org/client/register) API key

### 1 — Install dependencies (once)

```bash
make setup
```

This installs Python packages (`pip install -r requirements.txt`) and Node packages (`npm install`) for both apps.

### 2 — Add your football-data.org API key

Open `apps/api/.env` and paste your key:

```
FOOTBALL_DATA_API_KEY=your_key_here
```

All other values in that file are pre-filled for local Docker Postgres — you do not need to change them.

### 3 — Start Postgres

```bash
make db
```

Starts a Postgres 16 container on `localhost:5432` (db: `top5fantasy`, user: `postgres`, password: `postgres`).
Data persists across restarts in a Docker volume.

### 4 — Run migrations

```bash
make migrate
```

Applies all Alembic migrations and creates the full schema.

### 5 — Pull soccer data

```bash
make sync
```

Fetches competitions, teams, players, and fixtures from football-data.org and loads them into Postgres.
This takes 2–3 minutes on the free tier (rate-limited to 10 req/min).
Re-run any time to pick up updated fixtures and results.

### 6 — Start the servers

In two separate terminals:

```bash
make api   # FastAPI on http://localhost:8000
make web   # Next.js on http://localhost:3000
```

API docs are available at `http://localhost:8000/docs` once the server is running.

### All make targets

| Command | What it does |
|---------|-------------|
| `make setup` | Install all Python + Node dependencies |
| `make db` | Start Postgres via Docker |
| `make db-stop` | Stop the Postgres container |
| `make db-logs` | Tail Postgres logs |
| `make migrate` | Apply Alembic migrations |
| `make sync` | Pull soccer data from football-data.org |
| `make api` | Start FastAPI dev server on :8000 |
| `make web` | Start Next.js dev server on :3000 |

### Environment files

| File | Purpose |
|------|---------|
| `apps/api/.env` | Backend config — pre-filled, just add your API key |
| `apps/api/.env.example` | Template — committed to git, safe to share |
| `apps/web/.env.local` | Frontend config — not needed for local dev (uses defaults) |

The backend reads its config from `apps/api/.env`.
The frontend defaults to `http://localhost:8000` for the API URL — no extra config needed locally.

---

## Documentation

All planning and architectural documents live in [`docs/`](docs/README.md).

Start with [`docs/PROJECT_RULES.md`](docs/PROJECT_RULES.md) for product identity and guiding principles.

---

## Development Workflow

- Branch from `main` for every feature: `git checkout -b feat/squad-builder`
- Commit early and often with meaningful messages: `feat: add captain selection`
- Open a pull request against `main` — use the PR template
- Never commit `.env` files, secrets, or large binary assets
- Keep `main` green — do not merge broken code

### Commit message format

```
feat: short description of what was added
fix: short description of what was fixed
chore: dependency update, config change, cleanup
docs: documentation only change
refactor: code change with no behavior change
```

---

## Future Mobile Path

The web app ships first. The backend is intentionally designed as a clean REST API so a native mobile client can be added later without backend changes.

**Current:** Responsive web app (Next.js) served to all devices including phones.

**Later:** A React Native (Expo) or Flutter mobile app would authenticate and fetch data from the same FastAPI backend using the same JWT-based auth flow. No backend changes required.

The `packages/shared/` directory is reserved for types and constants that could eventually be shared between the web app and a React Native app.

---

## Rules

This project has explicit coding constraints and non-goals. Before building anything new, read:

- [`docs/CODING_CONSTRAINTS.md`](docs/CODING_CONSTRAINTS.md) — how to write code here
- [`docs/NON_GOALS.md`](docs/NON_GOALS.md) — what not to build
- [`docs/MVP_SCOPE.md`](docs/MVP_SCOPE.md) — what is and isn't in scope

---

## License

MIT
