"""
Top5 Fantasy pricing constants.

All tunable numbers live here. Change a threshold once and every service
that imports it picks it up automatically — no hunting through logic files.

PRICING FORMULA (initial):
    raw = POSITION_BASE[pos] + STRENGTH_BONUS[team.strength] + SC_BONUS[starter_confidence]
    price = round_half(raw)                  # nearest 0.5
    price = clamp(price, PRICE_MIN[pos], PRICE_MAX[pos])

WEEKLY UPDATE FORMULA:
    form_delta = player.form_score - avg_form_score_for_position
    if form_delta >= RISE_THRESHOLD  → +PRICE_STEP
    if form_delta <= DROP_THRESHOLD  → -PRICE_STEP
    else                             → 0.0
    Max cumulative change per GW: ±MAX_WEEKLY_MOVE
"""

from models.enums import Position

# ---------------------------------------------------------------------------
# Price bounds by position (in fantasy credits, 0.5 granularity)
# ---------------------------------------------------------------------------
# GKs and defenders top out lower — they score fewer attacking points.
# Mids and FWDs can reach premium territory for star players.

PRICE_MIN: dict[Position, float] = {
    Position.GK:  3.5,
    Position.DEF: 3.5,
    Position.MID: 4.0,
    Position.FWD: 4.5,
}

PRICE_MAX: dict[Position, float] = {
    Position.GK:   6.5,
    Position.DEF:  8.0,
    Position.MID: 11.0,
    Position.FWD: 12.0,
}

# ---------------------------------------------------------------------------
# Initial price: base by position
# ---------------------------------------------------------------------------
# Represents a "neutral" player — average team, regular starter.
# Adjusted up/down by team strength and starter confidence.

POSITION_BASE: dict[Position, float] = {
    Position.GK:  4.5,
    Position.DEF: 4.5,
    Position.MID: 5.5,
    Position.FWD: 6.0,
}

# ---------------------------------------------------------------------------
# Team strength bonus (team.strength is 1–5)
# ---------------------------------------------------------------------------
# A top-5 team's players are worth significantly more.
# A bottom-5 team's players are priced down — even good individual players
# score fewer clean-sheet and assist points on weak teams.

STRENGTH_BONUS: dict[int, float] = {
    1: -1.0,   # weakest league teams
    2: -0.5,
    3:  0.0,   # average mid-table
    4: +1.0,
    5: +2.5,   # elite clubs (Man City, Real, Bayern, etc.)
}

# ---------------------------------------------------------------------------
# Starter confidence bonus (player.starter_confidence is 1–5)
# ---------------------------------------------------------------------------
# Applied on top of base+strength. At season start all players default to 3
# (neutral) so initial prices are driven by position + team only.
# Once match data flows in, SC is updated and this modifier becomes meaningful
# for mid-season repricing.

SC_BONUS: dict[int, float] = {
    1: -1.0,   # fringe / rarely plays
    2: -0.5,   # rotation option
    3:  0.0,   # regular starter (default)
    4: +0.5,   # nailed-on starter
    5: +1.5,   # star nailed-on starter
}

# ---------------------------------------------------------------------------
# Weekly price update rules
# ---------------------------------------------------------------------------

# Number of completed gameweeks to look back for form calculation
FORM_WINDOW_GWS: int = 5

# Weights for fantasy points per GW — index 0 = most recent GW
# More recent = higher weight. Must have FORM_WINDOW_GWS entries.
FORM_WEIGHTS: list[int] = [5, 4, 3, 2, 1]

# Minimum fixtures a player must have appeared in within the form window
# to be eligible for a price change. Prevents overreacting to tiny samples.
MIN_APPEARANCES_FOR_UPDATE: int = 2

# form_delta thresholds that trigger a price movement
RISE_THRESHOLD: float = 1.5   # form_delta >= this → price rises
DROP_THRESHOLD: float = -1.5  # form_delta <= this → price drops

# Size of one price step (always 0.1 for clarity and stability)
PRICE_STEP: float = 0.1

# Hard ceiling on total price movement per gameweek (safety cap)
# Currently 0.1 because we only apply one signal per GW.
# Raise to 0.2 if multi-factor updates are added later.
MAX_WEEKLY_MOVE: float = 0.2

# ---------------------------------------------------------------------------
# Starter confidence update thresholds (from recent appearances)
# ---------------------------------------------------------------------------
# After each GW batch, starter_confidence is recalculated from recent stats.

SC_THRESHOLDS: list[tuple[float, int]] = [
    # (min_start_rate_in_window, sc_value)
    # start_rate = starts / fixtures_in_window
    (0.85, 5),   # 85%+ start rate → SC 5 (nailed-on star)
    (0.65, 4),   # 65–84% → SC 4 (regular starter)
    (0.35, 3),   # 35–64% → SC 3 (mostly starting)
    (0.10, 2),   # 10–34% → SC 2 (rotation)
    (0.00, 1),   # below 10% → SC 1 (fringe)
]

# Minimum fixtures in window before we trust SC calculation
MIN_FIXTURES_FOR_SC: int = 2
