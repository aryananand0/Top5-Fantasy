# Top5 Fantasy — Database Schema Design
**Date:** 2026-04-22  
**Phase:** B — Step 4  
**Status:** Approved and implemented

---

## 1. Summary

PostgreSQL relational schema for the Top5 Fantasy MVP. Uses SQLAlchemy 2.0 ORM models with Alembic migrations. Designed to support:

- A season-long fantasy game with players from 5 European leagues
- App-defined gameweeks spanning all competitions
- Custom player pricing engine (not reliant on external price data)
- Gameweek-based scoring from football-data.org free tier
- Rich and fallback scoring modes based on data availability
- Private mini-leagues with invite codes
- Global and per-league leaderboards

17 tables in MVP. 5 entities deferred to a later phase.

---

## 2. Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Primary keys | Integer (BigInteger for users) | Monolith, no distributed writes, simpler joins |
| User profiles | Folded into `users` | Profile is lightweight in MVP; split later if needed |
| Events vs stats | `player_match_stats` aggregate table | football-data.org free tier gives aggregates, not event timelines |
| Teams | No season duplication | Teams are stable club identities; season lives on players/fixtures |
| League membership | Keyed on `user_id` | User is the social identity; squad is derived from user + season |
| Scoring flexibility | `scoring_mode` on gameweeks, `data_quality_status` on fixtures | Explicit fallback mode for when free-tier data is incomplete |
| Transfer profit | Sell at current market price (no profit split) | Simpler; custom pricing engine controls values |
| Leaderboard table | `user_gameweek_scores` kept separate from `gameweek_lineups` | Clean leaderboard queries without lineup joins |
| Player GW point cache | Deferred (`player_gameweek_points`) | Computable from `player_match_stats`; materialise later if needed |

---

## 3. MVP Table List (17 tables)

| Table | File | Purpose |
|---|---|---|
| `users` | `user.py` | Auth + lightweight profile |
| `seasons` | `season.py` | Season label, dates, active flag |
| `competitions` | `competition.py` | The 5 leagues (PL, PD, BL1, SA, FL1) |
| `teams` | `team.py` | Clubs with competition association |
| `players` | `player.py` | Player roster with position + custom pricing |
| `price_history` | `player.py` | Weekly price snapshots per player |
| `gameweeks` | `gameweek.py` | App-defined GW windows with deadline + scoring mode |
| `fixtures` | `fixture.py` | Matches with status, scores, data quality |
| `player_match_stats` | `fixture.py` | Aggregate scoring inputs per player per fixture |
| `squads` | `squad.py` | User's season squad with budget + transfer bank |
| `squad_players` | `squad.py` | Players in a squad (with active/sold tracking) |
| `gameweek_lineups` | `lineup.py` | Locked 11-player selection with captain/vc |
| `gameweek_lineup_players` | `lineup.py` | The 11 players in a lineup with individual points |
| `transfers` | `transfer.py` | Transfer records (in/out, price, cost) |
| `mini_leagues` | `league.py` | Private leagues with invite codes |
| `league_members` | `league.py` | User-to-league membership |
| `user_gameweek_scores` | `scoring.py` | Final GW score per user (for leaderboards) |

---

## 4. Deferred Tables

| Table | Reason |
|---|---|
| `notifications` | No delivery mechanism in MVP |
| `watchlists` | Can live frontend-only initially |
| `activity_feed` | Complex to maintain; not core gameplay |
| `lineup_lock_history` | Useful for debugging but not required for game logic |
| `player_gameweek_points` | Derivable from `player_match_stats`; materialise if perf requires |

---

## 5. Table-by-Table Notes

### `users`
Auth plus lightweight profile in one table. `favorite_club` and `favorite_league` are optional personalisation fields used for the onboarding experience. `is_active` allows soft-disable without deletion.

### `seasons`
One row per app season (e.g., "2024-25"). The `is_active` flag controls which season the game engine is operating on. Only one should be active at a time.

### `competitions`
Stable across seasons — no season FK. Stores the football-data.org competition code (PL, PD, BL1, SA, FL1) and an optional TheSportsDB logo URL for enrichment.

### `teams`
Stable club identity — not duplicated per season. `competition_id` reflects current league membership. If a team is promoted/relegated, update `competition_id`. `strength` (1–5) is a manual or computed input to the pricing engine.

### `players`
Season-specific. Each player row belongs to one team and one season. `base_price` is set at season start; `current_price` is updated by the pricing job. `starter_confidence` (1–5) and `form_score` are pricing engine inputs updated by background jobs.

### `price_history`
One row per player per gameweek. Records the before/after price and a signed `change_amount`. `reason_summary` is a short human-readable string for display on the player page (e.g., "3 goals in 2 GWs").

### `gameweeks`
App-defined windows spanning multiple leagues. `deadline_at` is when transfers lock. `scoring_mode` is set per GW based on observed data availability from football-data.org — not assumed upfront.

### `fixtures`
One row per match. `gameweek_id` is nullable because fixtures are ingested before they're always assigned to a GW. A background job assigns them. `data_quality_status` is set after data sync and used by the scoring job to choose RICH vs FALLBACK scoring.

### `player_match_stats`
The single most important table for the fantasy engine. One row per player per fixture. The scoring job reads this table and sets `fantasy_points`. The `raw_data` JSONB column stores the full API response for audit and recomputation. `clean_sheet` is a computed boolean set by the scoring job (not derived on the fly during scoring to avoid repeated fixture joins).

### `squads`
One per user per season. `budget_remaining` is the live budget after all transfers. `free_transfers_banked` is updated at the start of each GW (add 2, cap at 3). `total_points` and `overall_rank` are updated after each GW finalises.

### `squad_players`
Tracks every player a user has ever owned this season. `is_active=True` = currently in squad. `is_active=False` = sold. This allows transfer history display without separate audit tables.

### `gameweek_lineups`
The locked 11 for a GW. `captain_player_id` and `vice_captain_player_id` both reference players in the lineup. The scoring job applies 2× to captain's `fantasy_points` (or vice-captain's if captain appeared for 0 minutes). `transfer_cost_applied` stores the penalty points deducted, separate from `points_scored` so both are visible to users.

### `gameweek_lineup_players`
The 11 players in a lineup with their individual `points_scored` (post-multiplier). Kept separate from `gameweek_lineups` for clean normalisation and easy per-player breakdowns in the UI.

### `transfers`
One row per transfer (one in, one out). `price_in` and `price_out` are snapshots at time of transfer. `is_free` and `point_cost` are stored explicitly to avoid recalculation.

### `mini_leagues`
Private leagues with a short invite `code`. `owner_user_id` is the admin. `is_public` is a hook for a future public league directory — defaulted to False in MVP.

### `league_members`
User-to-league mapping. No squad FK — to get standings, join to `squads` via `user_id + season_id`. This keeps invite logic, admin management, and member listing clean.

### `user_gameweek_scores`
Written by the scoring job after all GW matches and scoring are complete. Enables clean leaderboard queries with a single indexed table rather than joining through lineups. `captain_points` is the bonus contribution from the captain multiplier, stored for "top captain pick" stats.

---

## 6. ER Diagram (text)

```
seasons
├── gameweeks (season_id)
├── players (season_id)
└── mini_leagues (season_id)

competitions
└── teams (competition_id)

teams
├── players (team_id)
├── fixtures [home_team_id]
└── fixtures [away_team_id]

gameweeks
├── fixtures (gameweek_id)
├── gameweek_lineups (gameweek_id)
├── transfers (gameweek_id)
├── user_gameweek_scores (gameweek_id)
├── squad_players [joined_gameweek_id, left_gameweek_id]
└── price_history (gameweek_id)

fixtures
└── player_match_stats (fixture_id)

users
├── squads (user_id) ─── one per season
│   ├── squad_players (squad_id)
│   ├── gameweek_lineups (squad_id)
│   │   └── gameweek_lineup_players (lineup_id)
│   └── transfers (squad_id)
├── mini_leagues (owner_user_id)
├── league_members (user_id)
└── user_gameweek_scores (user_id)

players
├── squad_players (player_id)
├── player_match_stats (player_id)
├── gameweek_lineup_players (player_id)
├── gameweek_lineups [captain_player_id, vice_captain_player_id]
├── transfers [player_in_id, player_out_id]
└── price_history (player_id)

mini_leagues
└── league_members (league_id)
    └── users (user_id)
```

---

## 7. Recommended Indexes

| Table | Index | Purpose |
|---|---|---|
| `users` | `email`, `username` | Login and profile lookups |
| `players` | `(team_id, season_id)`, `position`, `current_price` | Player browser filters |
| `players` | `(external_id, season_id)` UNIQUE | Upsert from API |
| `teams` | `external_id` UNIQUE | Upsert from API |
| `fixtures` | `gameweek_id`, `kickoff_at`, `status` | GW fixture listing |
| `fixtures` | `external_id` UNIQUE | Upsert from API |
| `player_match_stats` | `fixture_id`, `player_id` | Scoring computation |
| `player_match_stats` | `(player_id, fixture_id)` UNIQUE | Prevent duplicate stat rows |
| `gameweeks` | `(season_id, status)`, `is_current` | Current GW lookups |
| `squads` | `(user_id, season_id)` UNIQUE | One squad per user per season |
| `squad_players` | `(squad_id, is_active)` | Active player list |
| `gameweek_lineups` | `(squad_id, gameweek_id)` UNIQUE | One lineup per squad per GW |
| `gameweek_lineups` | `gameweek_id` | GW-wide lineup queries |
| `transfers` | `(squad_id, gameweek_id)` | Transfer history per GW |
| `league_members` | `(league_id, user_id)` UNIQUE, `league_id`, `user_id` | League standings |
| `user_gameweek_scores` | `(user_id, gameweek_id)` UNIQUE | Prevent duplicate score rows |
| `user_gameweek_scores` | `(gameweek_id, points)` | Leaderboard ORDER BY |
| `price_history` | `(player_id, gameweek_id)` UNIQUE, `player_id` | Price trend display |

---

## 8. Normalisation Notes

**Normalised (separate tables):**
- Player match stats (not embedded in fixtures)
- Lineup players (not JSON column on gameweek_lineups)
- Price history (not an array column on players)
- League members (not array on mini_leagues)

**Stored computed values (intentional denormalisation):**
- `player_match_stats.fantasy_points` — avoids recomputing on every request
- `gameweek_lineup_players.points_scored` — avoids joining through player_match_stats for display
- `gameweek_lineups.points_scored` — avoids summing lineup players on every leaderboard query
- `squads.total_points` and `squads.overall_rank` — avoids season-long aggregation query
- `user_gameweek_scores` — dedicated leaderboard table, avoids multi-table join on every standings request
- `squad_players.is_active` — avoids checking left_gameweek_id IS NULL on every squad query

**Derived on the fly (not stored):**
- Mini-league standings — computed by joining `league_members → users → squads` for `total_points`
- Player selection percentage — computed at read time from `squad_players` counts
- Budget check during transfers — computed from `squads.budget_remaining`

---

## 9. Scoring Pipeline (data flow)

```
football-data.org API
        │
        ▼ (background job: result_sync)
fixtures (status=FINISHED, scores updated)
        │
        ▼ (background job: result_sync continues)
player_match_stats (goals, assists, minutes, cards, clean_sheet, raw_data)
        │
        ▼ (background job: score_calculation)
player_match_stats.fantasy_points (set per row)
        │
        ▼
gameweek_lineup_players.points_scored (per player, with captain 2x applied)
        │
        ▼
gameweek_lineups.points_scored (sum of lineup player points − transfer_cost)
        │
        ▼
user_gameweek_scores (written, rank_global set after all users scored)
        │
        ▼
squads.total_points (incremented), squads.overall_rank (recomputed)
```

---

## 10. Migration Plan

Build the schema in 6 ordered migration batches. Each batch can be run independently without breaking earlier tables.

| Batch | Migration | Tables |
|---|---|---|
| **1: Reference foundation** | `001_seasons_competitions` | seasons, competitions |
| | `002_teams` | teams |
| | `003_players` | players |
| **2: Game structure** | `004_gameweeks` | gameweeks |
| | `005_fixtures` | fixtures |
| **3: Users and squads** | `006_users` | users |
| | `007_squads` | squads, squad_players |
| **4: Lineups and scoring inputs** | `008_lineups` | gameweek_lineups, gameweek_lineup_players |
| | `009_player_match_stats` | player_match_stats |
| **5: Transactions** | `010_transfers` | transfers |
| | `011_scoring` | user_gameweek_scores |
| **6: Social** | `012_leagues` | mini_leagues, league_members |
| | `013_price_history` | price_history |

**Why this order:**
- Batch 1–2: pure reference data with no FKs to user tables. Can be seeded from football-data.org before any user exists.
- Batch 3: users come before squads (FK dependency).
- Batch 4: lineups depend on squads + gameweeks; player_match_stats depends on fixtures + players.
- Batch 5: transfers and scoring depend on squads + lineups + players.
- Batch 6: leagues and price history are independent of the core game loop and can be added last.

---

## 11. Tradeoffs and Future Extension

### What this schema does well
- Leaderboard queries are fast: one indexed table (`user_gameweek_scores`) with no joins required for ordering.
- Scoring recomputation is possible: `raw_data` JSONB + individual stats stored separately means you can re-run the scoring job if the model changes.
- Fallback mode is explicit: `scoring_mode` on gameweeks + `data_quality_status` on fixtures gives the scoring job clear signals.
- Transfer history is clean: `squad_players` with `is_active` flag avoids a separate audit log table.

### What you'll extend later
- **Bench and auto-subs:** Add `is_bench` boolean to `gameweek_lineup_players`. Auto-sub logic goes in the scoring job.
- **Sell price profit split:** Add `sell_price_cap` to `squad_players` when you want FPL-style value locks.
- **Player gameweek cache:** Add `player_gameweek_points` table if double-gameweek aggregation queries become slow.
- **Notifications:** Add `notifications` table when email/push delivery is wired.
- **Public leagues:** `mini_leagues.is_public` is already there — just expose it in the API.
- **Multi-season support:** All season-specific data has `season_id`. Historical seasons stay intact.
- **Mobile app:** No schema changes needed. Same backend, same JWT auth.
