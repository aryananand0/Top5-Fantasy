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

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+

### Running the frontend

```bash
cd apps/web
npm install
npm run dev
# Runs on http://localhost:3000
```

### Running the backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# Runs on http://localhost:8000
```

### Environment variables

Copy `.env.example` to `.env` in the project root and fill in your values. See `.env.example` for required variables.

The frontend reads from `apps/web/.env.local` and the backend reads from `apps/api/.env`.

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
