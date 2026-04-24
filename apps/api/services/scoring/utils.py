"""Utility helpers for the scoring pipeline."""

from models.enums import DataQuality, ScoringMode
from models.fixture import Fixture, PlayerMatchStats
from services.scoring.rules import CLEAN_SHEET_POSITIONS, LONG_PLAY_THRESHOLD


def resolve_scoring_mode(gw_mode: ScoringMode, fixture: Fixture) -> ScoringMode:
    """
    Determine the scoring mode for a specific fixture.

    The gameweek-level mode is the default. If the fixture's data quality is
    ESTIMATED (e.g. detailed stats were unavailable from the API), fall back
    to FALLBACK regardless of the GW setting.
    """
    if fixture.data_quality_status == DataQuality.ESTIMATED:
        return ScoringMode.FALLBACK
    return gw_mode


def resolve_clean_sheet(
    stats: PlayerMatchStats,
    fixture: Fixture,
    scoring_mode: ScoringMode,
) -> bool:
    """
    Return True if this player earned a clean sheet point for this fixture.

    Eligibility rules:
    - Position must be DEF or GK.
    - Fixture must have a known final score (home_score / away_score not None).
    - The player's team must have conceded 0 goals.
    - RICH mode:     player must have minutes_played >= LONG_PLAY_THRESHOLD (60).
    - FALLBACK mode: player must have appeared=True (minutes data not reliable).
    """
    if stats.position_snapshot not in CLEAN_SHEET_POSITIONS:
        return False

    if fixture.home_score is None or fixture.away_score is None:
        return False  # Score not yet confirmed; skip clean sheet

    # Goals conceded by the player's team
    if stats.team_id == fixture.home_team_id:
        conceded = fixture.away_score
    else:
        conceded = fixture.home_score

    if conceded != 0:
        return False

    if scoring_mode == ScoringMode.RICH:
        return stats.minutes_played >= LONG_PLAY_THRESHOLD
    else:
        return stats.appeared
