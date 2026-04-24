"""
Full gameweek scoring job.

Orchestrates:
  1. Score all FINISHED fixtures in the GW  (compute_fixture_player_points)
  2. Score all locked lineups               (compute_and_save_lineup_points)
  3. Upsert UserGameweekScore for each user's lineup

Also provides finalize_gameweek_ranks() to assign rank_global once all
scores are settled.

Both functions are idempotent: safe to re-run after new fixture data arrives.
"""

import logging
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import FixtureStatus
from models.fixture import Fixture
from models.gameweek import Gameweek
from models.lineup import GameweekLineup
from models.scoring import UserGameweekScore
from models.squad import Squad
from services.scoring.compute_player_points import compute_fixture_player_points
from services.scoring.compute_lineup_points import compute_and_save_lineup_points

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class UserGWScoreSummary:
    user_id: int
    squad_id: int
    lineup_id: int
    raw_points: int      # before transfer hit
    transfer_cost: int
    final_points: int
    captain_bonus: int


@dataclass
class GameweekScoringReport:
    gameweek_id: int
    fixtures_scored: int
    fixtures_skipped: int
    lineups_scored: int
    lineups_skipped: int
    user_scores: list[UserGWScoreSummary] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Main scoring job
# ---------------------------------------------------------------------------

def score_gameweek(db: Session, gameweek_id: int) -> GameweekScoringReport:
    """
    Full gameweek scoring pass.

    Safe to re-run — overwrites prior computed values with the latest data.
    Errors in individual fixtures or lineups are logged and skipped so one
    bad row cannot block the rest of the job.
    """
    gw = db.get(Gameweek, gameweek_id)
    if gw is None:
        raise ValueError(f"Gameweek {gameweek_id} not found")

    # --- Step 1: Score finished fixtures ---
    finished_fixtures: list[Fixture] = list(
        db.execute(
            select(Fixture).where(
                Fixture.gameweek_id == gameweek_id,
                Fixture.status == FixtureStatus.FINISHED,
            )
        ).scalars().all()
    )

    fixtures_scored = 0
    fixtures_skipped = 0
    for fixture in finished_fixtures:
        try:
            compute_fixture_player_points(db, fixture.id)
            fixtures_scored += 1
        except Exception:
            log.exception("Failed to score fixture %d — skipping", fixture.id)
            fixtures_skipped += 1

    log.info(
        "GW %d: scored %d/%d fixtures",
        gameweek_id, fixtures_scored, len(finished_fixtures),
    )

    # --- Step 2: Score locked lineups ---
    locked_lineups: list[GameweekLineup] = list(
        db.execute(
            select(GameweekLineup).where(
                GameweekLineup.gameweek_id == gameweek_id,
                GameweekLineup.is_locked.is_(True),
            )
        ).scalars().all()
    )

    report = GameweekScoringReport(
        gameweek_id=gameweek_id,
        fixtures_scored=fixtures_scored,
        fixtures_skipped=fixtures_skipped,
        lineups_scored=0,
        lineups_skipped=0,
    )

    for lineup in locked_lineups:
        try:
            lineup_result = compute_and_save_lineup_points(db, lineup.id)

            squad = db.get(Squad, lineup.squad_id)
            if squad is None:
                log.warning(
                    "Squad %d not found for lineup %d — skipping score persist",
                    lineup.squad_id, lineup.id,
                )
                report.lineups_skipped += 1
                continue

            transfer_cost = lineup.transfer_cost_applied
            raw_points = lineup_result.total_points
            final_points = raw_points - transfer_cost

            _upsert_user_gw_score(
                db,
                user_id=squad.user_id,
                squad_id=squad.id,
                gameweek_id=gameweek_id,
                lineup_id=lineup.id,
                raw_points=raw_points,
                transfer_cost=transfer_cost,
                captain_bonus=lineup_result.captain_bonus,
                final_points=final_points,
            )
            report.lineups_scored += 1
            report.user_scores.append(UserGWScoreSummary(
                user_id=squad.user_id,
                squad_id=squad.id,
                lineup_id=lineup.id,
                raw_points=raw_points,
                transfer_cost=transfer_cost,
                final_points=final_points,
                captain_bonus=lineup_result.captain_bonus,
            ))
        except Exception:
            log.exception("Failed to score lineup %d — skipping", lineup.id)
            report.lineups_skipped += 1

    log.info(
        "GW %d scoring complete: %d fixtures, %d lineups (%d skipped)",
        gameweek_id, fixtures_scored, report.lineups_scored, report.lineups_skipped,
    )
    return report


# ---------------------------------------------------------------------------
# Rank assignment
# ---------------------------------------------------------------------------

def finalize_gameweek_ranks(db: Session, gameweek_id: int) -> int:
    """
    Assign rank_global to every UserGameweekScore for this gameweek.
    Ordered by points DESC. Ties share the same rank (standard competition ranking).

    Call this after score_gameweek() once you're confident all fixtures are scored.
    Returns the count of rows ranked.
    """
    scores: list[UserGameweekScore] = list(
        db.execute(
            select(UserGameweekScore)
            .where(UserGameweekScore.gameweek_id == gameweek_id)
            .order_by(UserGameweekScore.points.desc())
        ).scalars().all()
    )

    if not scores:
        log.info("No scores to rank for gameweek %d", gameweek_id)
        return 0

    rank = 1
    prev_points: int | None = None
    for i, score in enumerate(scores):
        if prev_points is not None and score.points < prev_points:
            rank = i + 1
        score.rank_global = rank
        prev_points = score.points

    db.commit()
    log.info("Ranked %d scores for gameweek %d", len(scores), gameweek_id)
    return len(scores)


# ---------------------------------------------------------------------------
# Internal upsert
# ---------------------------------------------------------------------------

def _upsert_user_gw_score(
    db: Session,
    *,
    user_id: int,
    squad_id: int,
    gameweek_id: int,
    lineup_id: int,
    raw_points: int,
    transfer_cost: int,
    captain_bonus: int,
    final_points: int,
) -> UserGameweekScore:
    existing = db.execute(
        select(UserGameweekScore).where(
            UserGameweekScore.user_id == user_id,
            UserGameweekScore.gameweek_id == gameweek_id,
        )
    ).scalar_one_or_none()

    if existing:
        existing.squad_id = squad_id
        existing.lineup_id = lineup_id
        existing.points = final_points
        existing.transfer_cost = transfer_cost
        existing.captain_points = captain_bonus
    else:
        existing = UserGameweekScore(
            user_id=user_id,
            squad_id=squad_id,
            gameweek_id=gameweek_id,
            lineup_id=lineup_id,
            points=final_points,
            transfer_cost=transfer_cost,
            captain_points=captain_bonus,
        )
        db.add(existing)

    db.commit()
    return existing
