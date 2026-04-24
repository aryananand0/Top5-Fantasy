"""
Per-fixture player point computation.

Reads all PlayerMatchStats rows for a fixture, resolves clean sheet eligibility,
runs the rules engine, and persists fantasy_points back to the row.

Safe to re-run — later runs overwrite earlier computed values.
"""

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import ScoringMode
from models.fixture import Fixture, PlayerMatchStats
from models.gameweek import Gameweek
from services.scoring.rules import PlayerScoringBreakdown, score_player_fixture
from services.scoring.utils import resolve_clean_sheet, resolve_scoring_mode

log = logging.getLogger(__name__)


@dataclass
class FixtureScoringResult:
    fixture_id: int
    players_scored: int
    scoring_mode: str


def compute_fixture_player_points(
    db: Session,
    fixture_id: int,
    *,
    scoring_mode_override: ScoringMode | None = None,
) -> FixtureScoringResult:
    """
    Compute and persist fantasy_points for every PlayerMatchStats row for this fixture.

    Mode resolution order:
      1. scoring_mode_override if explicitly passed (e.g. from CLI)
      2. fixture.data_quality_status == ESTIMATED → FALLBACK
      3. gameweek.scoring_mode (the gameweek-level default)
      4. RICH as the global fallback if no gameweek is assigned yet

    Idempotent: re-running overwrites the previous fantasy_points values.
    """
    fixture = db.get(Fixture, fixture_id)
    if fixture is None:
        raise ValueError(f"Fixture {fixture_id} not found")

    if scoring_mode_override is not None:
        mode = scoring_mode_override
    elif fixture.gameweek_id is not None:
        gw = db.get(Gameweek, fixture.gameweek_id)
        gw_mode = gw.scoring_mode if gw else ScoringMode.RICH
        mode = resolve_scoring_mode(gw_mode, fixture)
    else:
        mode = resolve_scoring_mode(ScoringMode.RICH, fixture)

    stats_rows: list[PlayerMatchStats] = list(
        db.execute(
            select(PlayerMatchStats).where(PlayerMatchStats.fixture_id == fixture_id)
        ).scalars().all()
    )

    if not stats_rows:
        log.warning("No PlayerMatchStats rows for fixture %d — nothing to score", fixture_id)
        return FixtureScoringResult(fixture_id=fixture_id, players_scored=0, scoring_mode=mode)

    for stats in stats_rows:
        clean_sheet = resolve_clean_sheet(stats, fixture, mode)
        stats.clean_sheet = clean_sheet

        breakdown: PlayerScoringBreakdown = score_player_fixture(
            position=stats.position_snapshot,
            appeared=stats.appeared,
            minutes_played=stats.minutes_played,
            goals=stats.goals,
            assists=stats.assists,
            own_goals=stats.own_goals,
            yellow_cards=stats.yellow_cards,
            red_cards=stats.red_cards,
            clean_sheet=clean_sheet,
            scoring_mode=mode,
        )
        stats.fantasy_points = breakdown.total

        log.debug(
            "Player %d | fixture %d | %d pts (mode=%s)",
            stats.player_id, fixture_id, breakdown.total, mode,
        )

    db.commit()
    log.info(
        "Scored %d players for fixture %d (mode=%s)",
        len(stats_rows), fixture_id, mode,
    )
    return FixtureScoringResult(
        fixture_id=fixture_id,
        players_scored=len(stats_rows),
        scoring_mode=mode,
    )
