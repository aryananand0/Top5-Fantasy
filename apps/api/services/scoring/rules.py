"""
Top5 Fantasy scoring rules engine.

Pure functions — no DB dependencies. All constants live here so the scoring
model is easy to audit, test, and tweak without touching computation logic.

Scoring model (MVP):
  Starting appearance:     +1
  60+ minutes played:      +1  (RICH mode only)
  Goal by FWD:             +4
  Goal by MID:             +5
  Goal by DEF / GK:        +6
  Assist:                  +3
  Clean sheet (DEF / GK):  +4
  Yellow card:             -1
  Red card:                -3
  Own goal:                -2
  Captain:                  2× total (applied by lineup aggregator, not here)

Scoring modes:
  RICH      Full data: minutes, assists, clean sheets all applied.
  FALLBACK  Goals and appearance only. 60-min bonus and clean sheets skipped
            because minute coverage from the free tier is unreliable.

Clean sheet eligibility:
  RICH mode:     position must be DEF/GK, minutes_played >= 60, team conceded 0.
  FALLBACK mode: position must be DEF/GK, appeared=True, team conceded 0.
                 (60-min threshold dropped because minutes are not trustworthy)
"""

from dataclasses import dataclass

from models.enums import Position, ScoringMode


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APPEARANCE_POINTS: int = 1
LONG_PLAY_BONUS: int = 1
LONG_PLAY_THRESHOLD: int = 60

GOAL_POINTS: dict[Position, int] = {
    Position.FWD: 4,
    Position.MID: 5,
    Position.DEF: 6,
    Position.GK: 6,
}

ASSIST_POINTS: int = 3
CLEAN_SHEET_POINTS: int = 4

YELLOW_CARD_POINTS: int = -1
RED_CARD_POINTS: int = -3
OWN_GOAL_POINTS: int = -2

CAPTAIN_MULTIPLIER: int = 2

CLEAN_SHEET_POSITIONS: frozenset[Position] = frozenset({Position.GK, Position.DEF})


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class PlayerScoringBreakdown:
    """
    Point breakdown for one player in one fixture.
    `total` is the authoritative figure; components support UI display and audit.
    """
    appearance: int = 0
    long_play_bonus: int = 0
    goals: int = 0
    assists: int = 0
    clean_sheet: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    own_goals: int = 0
    mode_used: str = ScoringMode.RICH

    @property
    def total(self) -> int:
        return (
            self.appearance
            + self.long_play_bonus
            + self.goals
            + self.assists
            + self.clean_sheet
            + self.yellow_cards
            + self.red_cards
            + self.own_goals
        )


# ---------------------------------------------------------------------------
# Rule application
# ---------------------------------------------------------------------------

def score_player_fixture(
    *,
    position: Position,
    appeared: bool,
    minutes_played: int,
    goals: int,
    assists: int,
    own_goals: int,
    yellow_cards: int,
    red_cards: int,
    clean_sheet: bool,
    scoring_mode: ScoringMode = ScoringMode.RICH,
) -> PlayerScoringBreakdown:
    """
    Compute fantasy points for one player in one fixture.

    All inputs come from PlayerMatchStats. `clean_sheet` must already be
    resolved by the caller (see utils.resolve_clean_sheet) — this function
    simply applies the point value if the flag is True and the position qualifies.

    Stateless and deterministic: same inputs always produce the same output.
    """
    bd = PlayerScoringBreakdown(mode_used=scoring_mode)

    if not appeared:
        return bd  # Did not play — zero points, nothing more to calculate

    bd.appearance = APPEARANCE_POINTS

    if scoring_mode == ScoringMode.RICH and minutes_played >= LONG_PLAY_THRESHOLD:
        bd.long_play_bonus = LONG_PLAY_BONUS

    bd.goals = goals * GOAL_POINTS[position]
    bd.assists = assists * ASSIST_POINTS

    if clean_sheet and position in CLEAN_SHEET_POSITIONS:
        bd.clean_sheet = CLEAN_SHEET_POINTS

    bd.yellow_cards = yellow_cards * YELLOW_CARD_POINTS
    bd.red_cards = red_cards * RED_CARD_POINTS
    bd.own_goals = own_goals * OWN_GOAL_POINTS

    return bd
