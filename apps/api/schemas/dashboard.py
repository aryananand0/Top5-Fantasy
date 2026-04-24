"""
Dashboard API response schemas.

One aggregated payload for the authenticated user's dashboard.
Designed to be consumed in a single GET /api/v1/dashboard call.
"""

from typing import Optional

from pydantic import BaseModel


class CaptainInfo(BaseModel):
    player_id: int
    name: str
    display_name: Optional[str]
    position: str               # GK / DEF / MID / FWD
    team_name: str
    gw_points: Optional[int]    # GameweekLineupPlayer.points_scored (includes 2×); None before scoring

    model_config = {"from_attributes": False}


class FixtureInfo(BaseModel):
    fixture_id: int
    home_team: str
    home_team_short: str
    away_team: str
    away_team_short: str
    home_score: Optional[int]
    away_score: Optional[int]
    kickoff_at: Optional[str]   # ISO 8601 string
    status: str                 # SCHEDULED / LIVE / FINISHED / POSTPONED / CANCELLED
    has_squad_players: bool     # True if user has squad players in either team

    model_config = {"from_attributes": False}


class DashboardSummary(BaseModel):
    """
    Complete dashboard payload for one authenticated user.

    All fields have safe defaults so the frontend can render a meaningful
    state even when the season hasn't started or the user has no squad.

    Null semantics:
      gameweek_id=None      → no active gameweek (season not started)
      gw_points=None        → GW not scored yet
      gw_rank=None          → ranks not assigned yet for this GW
      captain=None          → no lineup set yet
    """

    # ── Gameweek ─────────────────────────────────────────────────────────────
    gameweek_id: Optional[int]
    gameweek_number: Optional[int]
    gameweek_name: Optional[str]
    gameweek_status: Optional[str]   # UPCOMING / LOCKED / ACTIVE / SCORING / FINISHED
    deadline_at: Optional[str]       # ISO 8601

    # ── Score (this GW) ───────────────────────────────────────────────────────
    gw_points: Optional[int]         # final points (after transfer hit). None = not scored
    gw_raw_points: Optional[int]     # gw_points + gw_transfer_cost (before hit)
    gw_transfer_cost: int            # point penalty applied this GW
    gw_captain_bonus: int            # extra points contributed by captain 2×
    gw_rank: Optional[int]           # None until finalize_gameweek_ranks() runs
    score_is_final: bool             # True only when GW status is FINISHED

    # ── Season ────────────────────────────────────────────────────────────────
    season_points: int               # sum of all GW final points for this user

    # ── Captain / VC ─────────────────────────────────────────────────────────
    captain: Optional[CaptainInfo]
    vice_captain: Optional[CaptainInfo]

    # ── State flags ───────────────────────────────────────────────────────────
    has_squad: bool
    has_lineup: bool
    is_editable: bool    # True if captain / lineup can still be changed
    can_transfer: bool   # True if transfer window is open

    # ── Transfers ─────────────────────────────────────────────────────────────
    free_transfers: int
    transfers_made: int
    transfer_hit: int        # total points hit from extra transfers this GW
    budget_remaining: float  # in millions (e.g. 4.5)

    # ── Upcoming fixtures ─────────────────────────────────────────────────────
    fixtures: list[FixtureInfo]      # up to 5, ordered by kickoff_at

    model_config = {"from_attributes": False}
