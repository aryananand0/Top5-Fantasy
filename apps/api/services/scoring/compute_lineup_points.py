"""
Lineup point aggregation.

For a locked gameweek lineup, sums each player's PlayerMatchStats.fantasy_points
across all FINISHED fixtures in the gameweek, applies captain 2× or vice-captain
fallback, and persists results to GameweekLineupPlayer.points_scored and
GameweekLineup.points_scored.

Run after compute_fixture_player_points has scored all fixtures in the GW.
Safe to re-run — later runs overwrite earlier values.

Captain / vice-captain rules:
  - Captain gets 2× their total GW points.
  - Vice-captain gets 2× only if the captain did not appear in ANY fixture this GW.
  - "Did not appear" = no PlayerMatchStats row with appeared=True across all GW fixtures.
  - If neither captain nor VC appeared, neither gets 2× (unusual edge case).
"""

import logging
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import FixtureStatus
from models.fixture import Fixture, PlayerMatchStats
from models.gameweek import Gameweek
from models.lineup import GameweekLineup, GameweekLineupPlayer
from services.scoring.rules import CAPTAIN_MULTIPLIER

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class PlayerLineupScore:
    player_id: int
    base_points: int    # Sum of fixture fantasy_points for the GW
    final_points: int   # After 2× multiplier if applicable
    is_captain: bool
    is_vice_captain: bool
    multiplier_applied: bool  # True if this player's 2× actually fired


@dataclass
class LineupScoreResult:
    lineup_id: int
    total_points: int
    captain_bonus: int       # Extra points from doubling (doubled player's base × 1)
    captain_appeared: bool
    vc_stepped_up: bool
    player_scores: list[PlayerLineupScore] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_finished_fixture_ids(db: Session, gameweek_id: int) -> list[int]:
    return list(
        db.execute(
            select(Fixture.id).where(
                Fixture.gameweek_id == gameweek_id,
                Fixture.status == FixtureStatus.FINISHED,
            )
        ).scalars().all()
    )


def _player_appeared_in_gameweek(
    db: Session,
    player_id: int,
    fixture_ids: list[int],
) -> bool:
    """Return True if the player has appeared=True in any of the given fixtures."""
    if not fixture_ids:
        return False
    result = db.execute(
        select(PlayerMatchStats.id).where(
            PlayerMatchStats.player_id == player_id,
            PlayerMatchStats.fixture_id.in_(fixture_ids),
            PlayerMatchStats.appeared.is_(True),
        ).limit(1)
    ).scalar_one_or_none()
    return result is not None


def _sum_player_points(
    db: Session,
    player_id: int,
    fixture_ids: list[int],
) -> int:
    """Sum fantasy_points for a player across the given fixtures."""
    if not fixture_ids:
        return 0
    rows = db.execute(
        select(PlayerMatchStats.fantasy_points).where(
            PlayerMatchStats.player_id == player_id,
            PlayerMatchStats.fixture_id.in_(fixture_ids),
        )
    ).scalars().all()
    return sum(rows)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def compute_and_save_lineup_points(
    db: Session,
    lineup_id: int,
) -> LineupScoreResult:
    """
    Aggregate player fixture points into a full lineup score and persist.

    Steps:
      1. Load the lineup and its 11 GameweekLineupPlayer rows.
      2. Get all FINISHED fixture IDs for the gameweek.
      3. For each player, sum their PlayerMatchStats.fantasy_points.
      4. Determine captain appearance; if captain did not appear, VC gets 2×.
      5. Apply the 2× multiplier to the right player.
      6. Persist to GameweekLineupPlayer.points_scored and GameweekLineup.points_scored.

    Idempotent: re-running overwrites prior values.
    """
    lineup = db.get(GameweekLineup, lineup_id)
    if lineup is None:
        raise ValueError(f"GameweekLineup {lineup_id} not found")

    fixture_ids = _get_finished_fixture_ids(db, lineup.gameweek_id)

    lineup_player_rows: list[GameweekLineupPlayer] = list(
        db.execute(
            select(GameweekLineupPlayer).where(
                GameweekLineupPlayer.lineup_id == lineup_id
            )
        ).scalars().all()
    )

    captain_id = lineup.captain_player_id
    vc_id = lineup.vice_captain_player_id

    captain_appeared = (
        _player_appeared_in_gameweek(db, captain_id, fixture_ids)
        if captain_id else False
    )
    vc_steps_up = not captain_appeared

    player_scores: list[PlayerLineupScore] = []
    for lp in lineup_player_rows:
        base = _sum_player_points(db, lp.player_id, fixture_ids)
        is_cap = lp.player_id == captain_id
        is_vc = lp.player_id == vc_id

        multiplier_fires = (is_cap and captain_appeared) or (is_vc and vc_steps_up)
        final = base * CAPTAIN_MULTIPLIER if multiplier_fires else base

        lp.points_scored = final
        player_scores.append(PlayerLineupScore(
            player_id=lp.player_id,
            base_points=base,
            final_points=final,
            is_captain=is_cap,
            is_vice_captain=is_vc,
            multiplier_applied=multiplier_fires,
        ))

    total = sum(ps.final_points for ps in player_scores)
    doubled_player = next((ps for ps in player_scores if ps.multiplier_applied), None)
    captain_bonus = doubled_player.base_points if doubled_player else 0

    lineup.points_scored = total
    db.commit()

    log.info(
        "Lineup %d | %d pts | captain_appeared=%s | vc_stepped_up=%s",
        lineup_id, total, captain_appeared, vc_steps_up,
    )
    return LineupScoreResult(
        lineup_id=lineup_id,
        total_points=total,
        captain_bonus=captain_bonus,
        captain_appeared=captain_appeared,
        vc_stepped_up=vc_steps_up,
        player_scores=player_scores,
    )
