# Top5 Fantasy — Non-Goals

This document is as important as the scope document. Every item below is intentionally excluded from the MVP. Building any of these without explicit decision to promote them to scope is a mistake.

If you are tempted to build something on this list, stop and ask: does the core game work without it?

---

## Data & Scoring

| Feature | Why Excluded |
|---|---|
| Live / real-time in-game scoring | Requires websockets, complex state, and rapid API polling. Free tier rate limits make this impractical. Scores update after matches complete. |
| Scraping-based data enrichment | Brittle, legally grey, and not needed given football-data.org coverage |
| Automated price movements based on transfer activity | Requires tracking ownership changes in real-time and applying market logic. Post-MVP. |
| Injury and availability alerts | Not available reliably on the free API tier |
| Player news feeds | Not available from football-data.org; would require scraping or a paid source |
| Detailed xG / advanced stats | Not in football-data.org free tier |
| Historical season data beyond current season | Not needed for MVP game loop |

---

## Game Mechanics

| Feature | Why Excluded |
|---|---|
| Bench boost chip | Adds complexity to scoring logic without changing the core game |
| Triple captain chip | Same — post-MVP chip mechanics |
| Free hit chip | Same |
| Wildcard chip | Included in Tier 2 (post-MVP), not MVP |
| Auto-substitutions | Requires ordering bench players and checking minutes — adds scoring complexity |
| Draft mode | Entirely different game mode; separate product concept |
| Head-to-head leagues | Requires pairing logic, scheduling, separate standings view |
| Cup competitions within leagues | Additional game mode, not core |
| Fixture difficulty ratings (FDR) | Useful feature but not required for the game to be playable |
| Bonus point system | Would require goal contribution data beyond what free API reliably provides |

---

## Social & Communication

| Feature | Why Excluded |
|---|---|
| In-league chat or comments | Requires moderation, content policy, and significant backend complexity |
| Global social feed or activity stream | Social network territory; not a fantasy game feature |
| Push notifications | Requires a notification service (FCM, APNs), mobile app, or web push setup — post-MVP |
| Email notifications | Tier 2 feature; not MVP |
| Social media share images (OG cards) | Nice to have, not game-critical |
| Following other users | Social graph — post-MVP |
| Public user profiles | Privacy and complexity reasons; post-MVP |

---

## Infrastructure & Engineering

| Feature | Why Excluded |
|---|---|
| WebSockets | Not needed without live scoring |
| Redis / external cache | Not needed at MVP scale |
| Celery / distributed task queue | APScheduler in-process is sufficient |
| Microservices or service splitting | One developer, one codebase |
| GraphQL API | REST is sufficient and simpler |
| Admin panel UI | Manage via direct database access or scripts during MVP |
| CI/CD pipeline (automated deploy) | Good to have, but not a game feature |
| Kubernetes or complex orchestration | Massively premature |
| Docker for production (initially) | Local dev Docker Compose is fine; production hosting is a separate decision |
| Multi-region deployment | Not remotely necessary at MVP scale |
| Observability / tracing stack | Structured logging is sufficient for MVP |
| Rate limiting middleware | Intentional: the MVP user base is small; not a security surface yet |

---

## Auth & Identity

| Feature | Why Excluded |
|---|---|
| OAuth / social login (Google, Apple, etc.) | Email/password is sufficient for MVP; OAuth adds complexity and third-party dependency |
| Two-factor authentication | Post-MVP security hardening |
| Account deletion / GDPR tools | Necessary before scaling; not MVP-blocking for early testing |
| Password reset via email | Should be built early post-MVP; manual reset acceptable during MVP testing |

---

## Monetization

| Feature | Why Excluded |
|---|---|
| Stripe or any payment integration | Not a paid product in MVP |
| Premium leagues or features | Monetization is a post-product-market-fit decision |
| Real-money mechanics of any kind | Permanently out of scope — this is not a betting platform |

---

## Native Mobile App

| Feature | Why Excluded |
|---|---|
| iOS app | Backend is designed for it, but the mobile app itself is post-MVP |
| Android app | Same — mobile web first |
| React Native or Flutter codebase | Post-MVP; the web app ships first |
| App Store submission | Post-MVP |

---

## Summary

The MVP is: sign up → build squad → score points → compete in leagues → make transfers → see standings.

Everything else is a distraction until those five things work well and feel good on mobile.
