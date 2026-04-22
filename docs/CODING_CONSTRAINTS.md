# Top5 Fantasy — Coding Constraints

These rules govern how code is written in this project. Any code agent, contributor, or future Claude prompt working on this codebase must read and respect these constraints. They exist to keep the project maintainable, lightweight, and consistent.

---

## 1. File Discipline

- **Keep files focused.** One file = one clear responsibility. A route file handles routing. A model file defines a model. A component renders one thing.
- **Split before bloating.** If a file grows past ~200 lines, consider whether it should be split. If splitting would require more than one level of new folders, the design may need rethinking.
- **No barrel files for now.** Avoid `index.ts` re-exports that make imports opaque. Import directly from the file that defines the thing.
- **Name files after what they do.** `player_router.py`, `SquadBuilder.tsx`, `useTransfers.ts` — not `helpers.py`, `utils.tsx`, or `misc.ts`.
- **Tests live next to the code they test** in a `__tests__` folder (frontend) or `tests/` mirror structure (backend).

---

## 2. Component Rules (Frontend)

- **One purpose per component.** A component that fetches data, renders a list, and handles pagination is three components.
- **No component should directly call an external API.** All data comes from the FastAPI backend via the Next.js data-fetching layer.
- **Prefer server-side data fetching** (Next.js `getServerSideProps` or React Server Components) for authenticated pages. Client-side fetching for interactive updates only.
- **Props over global state.** Pass data down explicitly where practical. Don't reach into global state for something that could be a prop.
- **No inline styles.** Use Tailwind classes. Custom styles go in the global stylesheet or as Tailwind config extensions — not as `style={}` attributes.
- **Mobile first.** Write Tailwind classes for mobile layout first, then override for `md:` and `lg:` breakpoints.

---

## 3. Backend Rules

- **Route files are thin.** Validation in Pydantic schemas. Logic in service functions. Database access in repository functions. Routes call services; services call repositories.
- **No business logic in database models.** Models define structure, not behavior.
- **No raw SQL** unless a query cannot be expressed cleanly in SQLAlchemy and performance requires it. If raw SQL is used, add a comment explaining why.
- **Every external API call goes through the scheduler.** No route or service should call football-data.org or TheSportsDB during a user request.
- **Wrap external calls in try/except.** Log failures. Never let an external API failure raise an unhandled 500 to the user.
- **Use environment variables for all secrets and configuration.** No hardcoded API keys, database URLs, or JWT secrets. Use a `.env` file locally; document required variables in `.env.example`.
- **Pydantic schemas for every API boundary.** Request bodies, query parameters, and response models all have explicit schemas.

---

## 4. Abstraction Rules

- **Do not abstract until you have three real use cases.** One use case is a function. Two is a coincidence. Three is a pattern worth abstracting.
- **No utility files named `utils`, `helpers`, or `misc`.** If a function is worth keeping, it belongs in a file named after what it does.
- **No premature generalization.** Build the specific thing that is needed. Do not build a generic system to handle a case that only exists once.
- **No design patterns for their own sake.** Factory, Strategy, Observer — use them only when the problem genuinely requires them.

---

## 5. Dependency Rules

- **Every dependency must earn its place.** Before adding a library, ask: is there a built-in way to do this?
- **No heavy UI component libraries** (MUI, Chakra, Ant Design). This project has a custom visual identity. Use Tailwind CSS.
- **Avoid libraries that are wrappers around other libraries** (e.g., `axios-retry` wrapping `axios` wrapping `fetch`). Prefer the base tool.
- **No ORM that hides too much.** SQLAlchemy is fine; avoid ORMs that make it hard to understand what SQL is being generated.
- **Lock dependency versions** in `requirements.txt` (backend) and `package.json` (frontend). Do not use floating versions in production config.

---

## 6. Data Layer Rules

- **No fake/mock data layers once real data exists.** During development it is acceptable to seed the database with real data from football-data.org. Do not build a parallel mock data system that persists beyond setup.
- **Seed scripts are for setup only.** A `seed_players.py` script that runs once is fine. Do not call it from the API.
- **Computed values are stored, not recalculated on request.** Gameweek scores are stored in the database. Do not compute them during an API request.
- **Pagination is always required on list endpoints.** No endpoint that returns a list of players, fixtures, or users should return unbounded results.

---

## 7. Comments

- **Default: no comments.** Well-named functions, variables, and files communicate intent better than comments.
- **When to comment:** The WHY is non-obvious. Examples: a workaround for a known API quirk, a subtle invariant, a constraint that would surprise a future reader.
- **Never comment:** What the code does (the code shows that). What was changed and why (that belongs in the git commit message). Who wrote it or when.
- **No commented-out code** committed to the repository. Delete it; git history preserves it.
- **No TODO comments** committed to main. Either do it now, create an issue, or accept it will not happen.

---

## 8. Error Handling Rules

- **Validate at system boundaries only.** User input and external API responses must be validated. Internal function-to-function calls do not need defensive validation if the data is known to be valid.
- **Return meaningful error messages to the client.** Not stack traces. Not "Internal Server Error" for all failures.
- **HTTP status codes must be accurate.** 404 for not found. 422 for validation failure. 401 for unauthenticated. 403 for unauthorized. 500 only for genuinely unexpected errors.
- **Log errors with context.** Log at `ERROR` level with: what failed, relevant IDs, and enough info to reproduce. Do not log sensitive data (passwords, tokens).

---

## 9. Do Not Build What Was Not Asked For

- **No feature creep.** If a prompt asks for the transfer page, build the transfer page. Do not also add a transfer history chart, an undo button, and a notification badge — unless those were specified.
- **No gold-plating.** Working code that is readable is the goal. Not the most clever or most elegant code.
- **No speculative infrastructure.** Do not create an abstraction "in case we need it later." Build what is needed now; refactor when the need actually arrives.

---

## 10. Mobile Responsiveness

- **Every page must be tested at 390px width** (iPhone 14 size) before it is considered complete.
- **Touch targets must be at least 44×44px** for interactive elements (buttons, links, player cards).
- **No horizontal scroll** on any page at mobile widths.
- **Player cards and tables** must stack or scroll gracefully on small screens — no overflowing tables.
- **Navigation must be mobile-friendly.** Bottom nav bar or hamburger — not a desktop-only top nav with many items.

---

## 11. Security Basics

- **Never commit secrets.** API keys, JWT secrets, database passwords go in `.env` — which is in `.gitignore`.
- **Use bcrypt** for password hashing. No MD5, SHA-1, or plain storage.
- **JWT tokens must have an expiry.** 7 days for standard sessions.
- **HTTP-only cookies** for JWT storage in the browser. Not localStorage.
- **Never trust client-supplied user IDs.** Extract the user ID from the validated JWT on every authenticated request.
- **Validate all user input** on the backend, even if the frontend also validates it.

---

## 12. Git Hygiene

- **Commit messages must be meaningful.** `feat: add captain selection to squad builder` not `update stuff`.
- **One logical change per commit.** Do not mix a bug fix and a new feature in one commit.
- **Never commit directly to main** for non-trivial changes. Use branches.
- **`.gitignore` must cover:** `__pycache__`, `.env`, `node_modules`, `.next`, `*.pyc`, migration autogenerated files.
- **No binary files committed** (images, PDFs, compiled assets). Link to external sources or use a CDN.
