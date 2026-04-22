"""
Pricing signal computation.

Reads from player_match_stats to derive form_score and starter_confidence.
Both signals feed into the weekly price update — they are NOT written here;
writing is done by weekly.py which decides when to commit.

These functions return neutral defaults when data is sparse (not yet scored
GWs, players with no recent appearances, etc.). The pricing engine never
crashes on missing data — it degrades gracefully.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import GameweekStatus
from models.fixture import Fixture, PlayerMatchStats
from models.gameweek import Gameweek
from services.pricing.constants import (
    FORM_WEIGHTS,
    FORM_WINDOW_GWS,
    MIN_FIXTURES_FOR_SC,
    SC_THRESHOLDS,
)
from services.pricing.utils import weighted_average


def compute_form_score(db: Session, player_id: int, season_id: int) -> float:
    """
    Weighted average of fantasy_points per game over the last FORM_WINDOW_GWS
    completed gameweeks.

    Most recent GW has the highest weight. Only counts games where the player
    appeared (appeared=True). Returns 0.0 if the player has no recent data.

    Note: fantasy_points is populated by the scoring job (Step X). Before that
    job runs, all players will have form_score=0.0 — correct behaviour.
    """
    rows = _fetch_recent_stats(db, player_id, season_id, FORM_WINDOW_GWS)
    if not rows:
        return 0.0

    # rows are ordered most-recent-first; extract fantasy_points per appearance
    points = [r.fantasy_points for r in rows if r.appeared]
    if not points:
        return 0.0

    return round(weighted_average(points, FORM_WEIGHTS), 2)


def compute_starter_confidence(db: Session, player_id: int, season_id: int) -> int:
    """
    Derive a 1–5 starter confidence score from recent appearances.

    start_rate = (fixtures where player started) / (total fixtures in window)

    Falls back to 3 (neutral) when not enough data is available.
    """
    rows = _fetch_recent_stats(db, player_id, season_id, FORM_WINDOW_GWS)

    if len(rows) < MIN_FIXTURES_FOR_SC:
        return 3  # neutral — not enough data

    total = len(rows)
    starts = sum(1 for r in rows if r.started)
    start_rate = starts / total

    for threshold, sc_value in SC_THRESHOLDS:
        if start_rate >= threshold:
            return sc_value

    return 1  # safety fallback


def _fetch_recent_stats(
    db: Session,
    player_id: int,
    season_id: int,
    limit: int,
) -> list[PlayerMatchStats]:
    """
    Return up to `limit` PlayerMatchStats rows for a player, ordered most-recent-first.
    Only includes stats from FINISHED or SCORING gameweeks (completed data only).
    """
    stmt = (
        select(PlayerMatchStats)
        .join(Fixture, Fixture.id == PlayerMatchStats.fixture_id)
        .join(Gameweek, Gameweek.id == Fixture.gameweek_id)
        .where(
            PlayerMatchStats.player_id == player_id,
            Gameweek.season_id == season_id,
            Gameweek.status.in_([GameweekStatus.FINISHED, GameweekStatus.SCORING]),
        )
        .order_by(Gameweek.number.desc(), Fixture.kickoff_at.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars())


def compute_position_avg_form(
    player_form_map: dict[int, float],
    player_positions: dict[int, str],
) -> dict[str, float]:
    """
    Given a dict of {player_id: form_score} and {player_id: position},
    return {position: avg_form_score} for all positions.

    Pure function — no DB access. Call after bulk-fetching form scores.
    """
    from collections import defaultdict
    buckets: dict[str, list[float]] = defaultdict(list)
    for pid, form in player_form_map.items():
        pos = player_positions.get(pid)
        if pos:
            buckets[pos].append(form)

    return {
        pos: (sum(scores) / len(scores)) if scores else 0.0
        for pos, scores in buckets.items()
    }
