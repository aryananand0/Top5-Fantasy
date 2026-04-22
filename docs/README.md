# Top5 Fantasy — Documentation Index

This folder contains all planning, architectural, and decision documents for the project. Read these before writing code.

---

## Start Here

| Document | Purpose |
|---|---|
| [PROJECT_RULES.md](PROJECT_RULES.md) | Product identity, design principles, data source rules, what to avoid |
| [MVP_SCOPE.md](MVP_SCOPE.md) | What is in scope, what is not, and all required user flows |
| [NON_GOALS.md](NON_GOALS.md) | Explicit list of features excluded from MVP |
| [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) | System architecture, caching strategy, and component breakdown |
| [CODING_CONSTRAINTS.md](CODING_CONSTRAINTS.md) | Practical coding rules that must be followed in all future work |

---

## Document Update Rules

- Update docs when a decision changes, not after the fact.
- If a feature moves from Non-Goals to MVP, update both `NON_GOALS.md` and `MVP_SCOPE.md`.
- Do not use docs as a changelog — that is what git commit messages are for.
- Keep documents concise. Add a section when it adds clarity; do not add sections for completeness.
