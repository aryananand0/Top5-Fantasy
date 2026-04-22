# Top5 Fantasy — Architecture Overview

This document describes the intended system architecture for the MVP. The design is intentionally simple. Every decision here prioritizes buildability over sophistication.

---

## Guiding Principle

> One developer. One database. One backend service. One frontend. No microservices.

The architecture exists to support the game, not to demonstrate engineering complexity. If a simpler approach works, use it.

---

## System Diagram (Conceptual)

```
[ Browser / Mobile Web ]
        |
        | HTTPS
        v
[ Next.js Frontend ]  ← serves pages, calls backend API
        |
        | REST (JSON)
        v
[ FastAPI Backend ]
        |          |
        |          └── [ football-data.org API ]  ← scheduled sync only
        |          └── [ TheSportsDB API ]         ← scheduled sync only (non-critical)
        v
[ PostgreSQL Database ]
        ^
        |
[ Background Scheduler ]  ← fetches data, calculates scores, updates DB
```

---

## Component Breakdown

### Frontend — Next.js

- **Role:** Render the UI, handle user interactions, communicate with the backend.
- **Rendering strategy:** Use server-side rendering (SSR) for personalized pages (squad, standings). Use static generation for informational pages (rules, about).
- **API communication:** All data fetches go to the FastAPI backend. The frontend never calls football-data.org or TheSportsDB directly.
- **Styling:** Tailwind CSS with custom design tokens for the sketch aesthetic (custom colors, rounded corners, border widths, font choices).
- **Auth:** JWT stored in an HTTP-only cookie. The frontend sends the cookie with every request; the backend validates it.
- **Mobile readiness:** Built mobile-first from day one. The same Next.js app will serve mobile web users. A future React Native app would consume the same backend API without frontend changes.

### Backend — FastAPI (Python)

- **Role:** Handle all business logic, expose REST endpoints, validate data, orchestrate database reads/writes, run background jobs.
- **Auth:** Stateless JWT authentication. No server-side session storage.
- **Validation:** Pydantic schemas for every request and response body.
- **Data access:** SQLAlchemy ORM with PostgreSQL. No raw SQL unless performance demands it.
- **Background jobs:** APScheduler (or a simple Python cron wrapper) runs data sync and scoring jobs on a schedule. Jobs run in the same process as the API for MVP simplicity. If the API ever scales, jobs can be extracted, but do not over-engineer this now.
- **Rate limit handling:** All external API calls are rate-limited at the application layer. The scheduler respects football-data.org's free tier limits (10 requests/minute).

### Database — PostgreSQL

Core tables at a conceptual level (not a full schema — see data model doc when created):

| Table | Purpose |
|---|---|
| users | Account credentials and display info |
| squads | User squad for a season |
| squad_players | Junction: which players are in a squad, starting/bench, captain flags |
| players | Cached player records from football-data.org |
| teams | Cached club records |
| competitions | The five supported leagues |
| fixtures | Match schedule and results |
| gameweeks | Gameweek periods with deadlines |
| player_stats | Per-player, per-fixture stats used for scoring |
| gameweek_scores | Computed points per user per gameweek |
| transfers | Log of all transfer actions |
| leagues | Private mini-leagues |
| league_memberships | Users ↔ leagues |

### Background Scheduler

The scheduler is the bridge between external APIs and the database. User-facing endpoints never call external APIs — they only read from the database.

**Sync jobs:**

| Job | Frequency | Source | Purpose |
|---|---|---|---|
| Fixture sync | Daily | football-data.org | Pull upcoming and completed fixtures |
| Result sync | Every 3–6 hours on match days | football-data.org | Pull match results and stats |
| Score calculation | After result sync | Internal | Calculate gameweek points for all users |
| Player/team enrichment | Weekly | TheSportsDB | Fetch badges and photos (non-critical) |
| Gameweek deadline management | Daily | Internal | Open/close gameweek transfer windows |

**Key design decisions:**
- Scoring is computed and stored, not calculated on the fly during requests.
- If the football-data.org API returns no new data, the sync job is a no-op — no errors surface to users.
- TheSportsDB sync runs last and is wrapped in try/except — failures are logged, not raised.

### External APIs

#### football-data.org (Free Tier)
- Rate limit: 10 requests/minute
- Data available: fixtures, results, scorers, assists, yellow/red cards, minutes played
- Clean sheet data: must be derived from match result + goals conceded (API does not always provide explicitly)
- The scheduler must queue and pace requests to stay within the rate limit.
- All responses are cached to the database before use.

#### TheSportsDB
- Used for: club badge URLs, player photo URLs, league logo URLs
- Stored in the database as URL strings — the frontend fetches images directly from TheSportsDB CDN
- If a badge or photo URL is missing, show a generic placeholder — never error

---

## Caching Strategy

| Layer | What is Cached | TTL / Refresh |
|---|---|---|
| PostgreSQL | All football-data.org responses | Until next scheduled sync |
| PostgreSQL | TheSportsDB image URLs | Weekly |
| Next.js (server) | Leaderboard and standings pages | Short (5–15 min via revalidate) |
| Browser | Static assets, fonts | Standard HTTP cache headers |

**No Redis in MVP.** PostgreSQL query performance is more than sufficient for the expected user scale of an MVP. If query latency becomes an issue, optimize queries and add indexes before introducing a caching layer.

---

## Authentication Flow

1. User submits email + password
2. Backend verifies credentials against the database (bcrypt hashed passwords)
3. Backend issues a signed JWT with user ID and expiry (7-day TTL)
4. JWT is stored in an HTTP-only, Secure, SameSite=Strict cookie
5. Every subsequent API request includes the cookie automatically
6. Backend middleware validates the JWT on protected routes

---

## Gameweek Scoring Flow

1. Scheduler detects completed fixtures for the current gameweek
2. Scheduler fetches match statistics from football-data.org
3. Stats are stored in `player_stats` table
4. Scoring job iterates over all active squads
5. For each squad: calculate points for each starting player based on stats + scoring rules
6. Captain's points are doubled; vice-captain doubles if captain has 0 minutes
7. Results written to `gameweek_scores` table
8. Leaderboards and standings are derived from `gameweek_scores` — no calculation at query time

---

## Mobile Readiness

The backend is a clean REST API. A future React Native or Flutter mobile app requires:
- No changes to the backend
- Same JWT auth mechanism (store token in secure storage instead of cookie)
- Same endpoints, same response contracts

The frontend (Next.js) will serve mobile web users from day one via responsive design. The mobile app is a Tier 2 / post-MVP concern.

---

## Why This Architecture Is Simple on Purpose

| Decision | Why |
|---|---|
| One backend service | Avoids inter-service networking, deployment complexity, and observability overhead |
| PostgreSQL only | Relational data fits naturally; one database to back up, one to query |
| No Redis | Adds ops burden; not needed at MVP scale |
| No Celery | APScheduler in-process is sufficient; Celery adds broker dependency |
| REST not GraphQL | Simpler to build, debug, and document; overkill avoided |
| No microservices | Single developer; the coordination cost exceeds the benefit |
| Scheduler in same process | One deployment unit; extract later if needed |

The architecture is designed to be extracted and scaled if the app grows. Each component has a clear responsibility. Nothing is entangled by design.
