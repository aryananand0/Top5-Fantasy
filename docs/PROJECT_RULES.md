# Top5 Fantasy — Project Rules

These rules govern every decision made in this project. Future prompts, contributors, and code agents must read and respect these rules. When in doubt, defer to this document.

---

## 1. Product Identity

- **Name:** Top5 Fantasy
- **Type:** Season-long fantasy football manager game
- **Hook:** Build one squad from players across all five top European leagues (Premier League, La Liga, Bundesliga, Serie A, Ligue 1)
- **Tone:** Playful, social, and competitive — not a data dashboard, not a betting tool
- **NOT a betting app.** No odds, no wagering, no real-money mechanics. Ever.
- **NOT daily fantasy.** All gameplay is season-long with weekly transfers.

---

## 2. Design Principles

### Visual Identity
- **Aesthetic:** Hand-drawn, sketch-like, sticker-feel. Think a well-designed notebook, not a fintech dashboard.
- **Background:** Off-white or lightly textured — never pure white, never dark mode as default
- **Cards:** Rounded corners, thick outlines, prominent whitespace
- **Typography:** Bold and chunky for scores and numbers; clean and readable for body text
- **Icons:** Simple doodle-style — not icon library defaults, not photorealistic
- **Color:** Club-color accents used sparingly for identity, not decoration. Palette should remain light and airy.
- **Labels:** Sticker-style badges for positions, leagues, and statuses

### What to Avoid Visually
- Glossy gradients
- Glassmorphism
- Fake 3D or heavy drop shadows
- Betting-app aesthetics (dark, neon, urgency-driven)
- Overly polished / AI-generated feel
- Dense data grids without breathing room
- Heavy animation that slows the page

### UX Principles
- Mobile-first layout. Every screen must work well on a 390px viewport before being stretched to desktop.
- No wall-of-text onboarding. Use progressive disclosure — show what the user needs now.
- Actions should feel fast and forgiving. Confirmation dialogs only where stakes are genuinely high (e.g., chip usage).
- Social hooks are first-class: leagues, standings, and rivalry are part of the UX, not buried settings.

---

## 3. Data Source Rules

### Primary: football-data.org
- **All core game logic must rely exclusively on football-data.org.**
- This includes: fixtures, results, scorers, assists, cards, minutes played, and clean sheets.
- Design every feature assuming **free tier only**: rate limits apply, response volume is constrained.
- Never block a user-facing request on a live football-data.org call. Always use cached data.
- If football-data.org is unavailable, the app should degrade gracefully (show last known data, not crash).

### Secondary: TheSportsDB
- **Use TheSportsDB only for non-critical, presentational enrichment:** club badges, player photos, league logos.
- Never make core scoring, standings, or game logic depend on TheSportsDB.
- TheSportsDB failures must be silent — fall back to placeholder assets, never errors.

### Scraping: Forbidden for Core Gameplay
- Web scraping must not be part of the core game engine.
- Scraping is not a backup for missing API data. Design the game around what the free API provides.
- Scraping may only be considered for one-off, offline tooling (e.g., a setup script) — never in the live app path.

---

## 4. Performance Rules

- All external API data must be cached. No live fan-out to external APIs during user requests.
- Background jobs handle data sync. User requests hit the database only.
- Page loads must feel snappy on mobile on a 4G connection.
- No blocking synchronous calls to external services in the API request path.
- Images (player photos, badges) must be lazy-loaded and sized appropriately.
- The frontend must not make direct calls to external APIs. All data flows through the backend.

---

## 5. Lightweight Rules

- This project is built by a single student developer. Complexity is the enemy.
- No microservices. One backend service (FastAPI), one database (PostgreSQL).
- No message queues, no Redis (unless caching becomes clearly necessary and is discussed first).
- No Kubernetes, Docker Compose is fine for development.
- No GraphQL. REST only.
- No event sourcing, CQRS, or DDD patterns unless the problem genuinely demands them.
- Dependencies must earn their place. Before adding a library, ask: is there a simpler built-in way?
- Keep the GitHub repo clean: no generated build artifacts committed, no large binary assets, no secrets in version control.

---

## 6. Backend Principles

- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy or similar — keep models readable
- Endpoints should be clean and RESTful. No deeply nested resource paths.
- Authentication: JWT-based, stateless. Keep it simple.
- Background jobs: APScheduler or a simple cron-triggered task. No Celery unless needed.
- Validation: Pydantic models at every API boundary.
- The backend must be designed so a mobile app could consume the same API in the future with no changes.
- Never expose raw database IDs where a slug or opaque ID is more appropriate.

---

## 7. Frontend Principles

- **Framework:** Next.js (React)
- Use server-side rendering or static generation for pages that don't need live interactivity.
- Components should be reusable and focused. One purpose per component.
- No component should fetch its own data independently if a parent or a server-side fetch can do it.
- Tailwind CSS for styling (utility-first is compatible with the sketch aesthetic when customized well).
- No heavy animation libraries. CSS transitions and minimal keyframe animations only.
- State management: React Context or lightweight Zustand — no Redux unless complexity demands it.
- Mobile breakpoints must be the starting point for layout, not an afterthought.

---

## 8. What to Avoid (Always)

- Over-engineering: do not build for hypothetical future scale
- Premature abstraction: three similar lines of code are better than a wrong abstraction
- Fake data layers that outlive their usefulness
- Magic configuration: if a value matters, name it clearly
- Silent failures: log errors, surface them where appropriate
- Features that weren't asked for
- Betting, gambling, or real-money mechanics of any kind
- Live websocket scoring in MVP
- Anything that makes the project hard to push to GitHub, clone, or run locally
