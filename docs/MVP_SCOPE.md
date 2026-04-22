# Top5 Fantasy — MVP Scope

This document defines what is and is not part of the MVP. It also defines the user flows that must work end-to-end before the product is considered shippable as an MVP.

---

## Scope Tiers

### Tier 1 — Must-Have MVP
These features must be working before launch. The game is not playable without them.

- User account creation (email/password)
- User login and session management (JWT)
- Player database populated from football-data.org (all five leagues)
- Squad builder: pick 15 players within a salary cap
  - Valid formation required (1 GK, 3–5 DEF, 2–5 MID, 1–3 FWD)
  - Starting XI + 4 bench players
  - No more than 3 players from the same club
- Captain and vice-captain selection
- Automated gameweek scoring based on football-data.org match data
- Points awarded per the defined scoring system (see ARCHITECTURE_OVERVIEW.md)
- Gameweek review page: see your squad's points, per-player breakdown
- Weekly free transfers (2 per gameweek, unused transfers do not roll over beyond 1)
- Transfer penalty: -4 points per extra transfer beyond the free allowance
- Global leaderboard: all users ranked by total season points
- Private mini-leagues: create a league with an invite code, join a league via code
- Mini-league standings page
- Background job that pulls match data and calculates gameweek scores
- Basic mobile-responsive layout across all pages

---

### Tier 2 — Should-Have (Post-MVP, Near-Term)
These improve the product but the game functions without them.

- Player profile pages (stats, ownership %, form, upcoming fixtures)
- Fixture difficulty ratings (FDR) per team
- Team of the Week display
- Price changes (simple formula: increase for high-ownership players, decrease for dropped players)
- Email notifications (gameweek locked, scores in, transfers reminder)
- "Wildcard" chip (once per season): swap entire squad without penalty
- Social sharing: share squad or gameweek score as image/link
- Player search with filters (position, league, club, price range)
- Ownership percentages shown on player cards

---

### Tier 3 — Explicitly Excluded from MVP
Do not build these during MVP. They are out of scope by design.

- Live in-game scoring (no websockets, no real-time updates)
- Automated price movements based on transfer market activity
- Bench boost chip
- Triple captain chip
- Free hit chip
- Chat or comments within leagues
- Public chat or global social feed
- Player news feeds or injury alerts
- Admin panel or internal tooling UI
- Mobile native app (iOS/Android)
- OAuth / social login (Google, Apple)
- Stripe or any payment integration
- Push notifications
- Detailed player history graphs
- Draft mode
- Head-to-head leagues
- Cup competitions
- Anything requiring scraping

---

## User Flows

Each flow below must be fully functional in the MVP.

---

### Flow 1: Sign Up

1. User visits the app homepage
2. User clicks "Create Account"
3. User enters: display name, email, password
4. System validates inputs (email format, password length ≥ 8, name length ≥ 2)
5. System creates account and issues a JWT
6. User is redirected to onboarding (Flow 2)

**Error states:** duplicate email, weak password, invalid email — all surface clear inline messages.

---

### Flow 2: Onboarding

1. Shown once after account creation (not on every login)
2. Screen 1: "Welcome to Top5 Fantasy" — brief explanation of the game in 3 bullet points
3. Screen 2: Salary cap explained + position requirements shown visually
4. Screen 3: Prompt to build squad → CTA: "Build My Squad"
5. User proceeds to Flow 3

**Rule:** Onboarding must not require an API call. It is purely static/informational.

---

### Flow 3: Squad Creation

1. User lands on the squad builder page
2. Page shows a pitch layout with 15 empty slots (11 starting, 4 bench)
3. User clicks a slot to open player picker
4. Player picker shows a filterable, paginated list of available players
   - Filters: position, league, club, max price
   - Each player card shows: name, club, position, price, projected/recent points
5. User selects a player → slot is filled → remaining budget updates
6. System enforces: max 3 from one club, budget cap, position limits
7. User fills all 15 slots
8. User is prompted to select captain and vice-captain (Flow 4)
9. User clicks "Save Squad"
10. System saves squad and redirects to dashboard

**Error states:** over budget, invalid formation, club limit exceeded — all shown inline before save is attempted.

---

### Flow 4: Captain Selection

1. Triggered during squad creation (step 8 above) or from the My Squad page at any time before gameweek deadline
2. User sees their starting XI players listed
3. User taps/clicks one player → designated as Captain (C badge, 2x points)
4. User taps/clicks a different player → designated as Vice-Captain (VC badge, 2x points if captain does not play)
5. Selection is saved immediately or on explicit "Confirm" tap
6. Captain and VC badges are shown persistently on the squad view

---

### Flow 5: Transfers

1. User navigates to "Transfers" from the main nav
2. System shows: current squad, free transfers remaining this gameweek, next gameweek deadline
3. User clicks a player to remove them
4. Removed player slot opens the player picker (same as squad creation)
5. User picks a replacement
6. If user has used all free transfers, system warns: "+4 point penalty per additional transfer"
7. User can stage multiple transfers before confirming
8. User clicks "Confirm Transfers" → changes saved, deadline lock prevents further changes after cutoff

**Rules:**
- 2 free transfers per gameweek by default
- 1 unused transfer rolls over (max 2 banked at once)
- No transfers after gameweek deadline
- Transferred-out players earn no points that gameweek

---

### Flow 6: Join or Create a Private Mini-League

#### Create
1. User goes to "Leagues" from the main nav
2. User clicks "Create League"
3. User enters a league name
4. System generates a unique 6-character invite code
5. User sees the league landing page with standings (just themselves) and the invite code to share

#### Join
1. User goes to "Leagues" → "Join a League"
2. User enters the invite code
3. System validates the code and adds the user to the league
4. User is taken to the league standings page

**Rules:**
- A user can be in multiple leagues simultaneously
- League creator is the admin (but admin powers are minimal in MVP: rename only)
- No private league cap in MVP (but soft limit of 50 members is fine)

---

### Flow 7: Gameweek Scoring Review

1. After a gameweek is processed (background job runs), user navigates to "My Team" or receives a notification (Tier 2 feature)
2. Page shows:
   - Total gameweek points (prominent, large number)
   - Each player's points for the week with a breakdown (e.g., "1 goal × 4pts, 60+ min × 1pt")
   - Captain bonus shown clearly
   - Bench players shown with their points (for reference, not counted unless auto-sub — auto-sub is Tier 2)
3. User can navigate to previous gameweeks to review history
4. User can see league standings updated with this week's scores

**Rules:**
- Scores are final once the gameweek background job completes
- No partial/live score updates in MVP
- If a match result is not yet in the API, that player's score shows as pending

---

## MVP Definition of Done

The MVP is considered complete when:

- A new user can sign up, build a valid squad, select captain/VC, and view their dashboard
- A gameweek scoring job can be run manually and produces correct scores for all users
- A user can make transfers before the deadline
- A user can create a private league and another user can join it via invite code
- Global and league standings update after a gameweek is processed
- All flows above work on mobile (390px) and desktop (1280px)
- No core feature depends on TheSportsDB or scraping
