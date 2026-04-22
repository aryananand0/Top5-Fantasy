"""
Weekly price update engine.

Run after each gameweek is scored (SCORING or FINISHED status).
Adjusts current_price up or down by PRICE_STEP based on form_delta:

    form_delta = player.form_score - avg_form_score_for_position

    form_delta >= RISE_THRESHOLD  →  +PRICE_STEP  (good form, price rises)
    form_delta <= DROP_THRESHOLD  →  -PRICE_STEP  (poor form, price drops)
    in between                    →  no change

Price changes are:
    - Clamped to ±MAX_WEEKLY_MOVE per gameweek
    - Bounded by PRICE_MIN/PRICE_MAX for the position
    - Skipped if the player has fewer than MIN_APPEARANCES_FOR_UPDATE appearances
      in the form window (sparse data protection)
    - Written to price_history for audit and display

Usage:
    python scripts/pricing.py update-prices --season 2024-25 --gameweek 5
    python scripts/pricing.py update-prices --season 2024-25 --gameweek 5 --preview
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import Position
from models.fixture import Fixture, PlayerMatchStats
from models.gameweek import Gameweek
from models.player import Player
from models.team import Team
from services.pricing.constants import (
    DROP_THRESHOLD,
    FORM_WINDOW_GWS,
    MAX_WEEKLY_MOVE,
    MIN_APPEARANCES_FOR_UPDATE,
    PRICE_STEP,
    RISE_THRESHOLD,
    SC_BONUS,
)
from services.pricing.history import record_price_change
from services.pricing.signals import (
    compute_form_score,
    compute_position_avg_form,
    compute_starter_confidence,
)
from services.pricing.utils import clamp_price, round_to_half


@dataclass
class PriceUpdateResult:
    player_id: int
    player_name: str
    position: Position
    old_price: float
    new_price: float
    form_score: float
    position_avg_form: float
    form_delta: float
    delta: float           # signed price change (+0.1 / 0.0 / -0.1)
    reason: str
    skipped: bool          # True if no price change (sparse data or within threshold)


def compute_price_delta(
    form_delta: float,
    current_price: float,
    position: Position,
) -> float:
    """
    Pure function: return the signed price change for a player.

    Applies PRICE_STEP in the appropriate direction, then clamps to
    MAX_WEEKLY_MOVE and position bounds.
    """
    if form_delta >= RISE_THRESHOLD:
        raw_delta = PRICE_STEP
    elif form_delta <= DROP_THRESHOLD:
        raw_delta = -PRICE_STEP
    else:
        return 0.0

    # Clamp delta magnitude
    raw_delta = max(-MAX_WEEKLY_MOVE, min(MAX_WEEKLY_MOVE, raw_delta))

    # Verify new price stays in bounds
    new_price = clamp_price(current_price + raw_delta, position)
    return round(new_price - current_price, 1)


def apply_weekly_updates(
    db: Session,
    season_id: int,
    gameweek_id: int,
    *,
    preview: bool = False,
) -> list[PriceUpdateResult]:
    """
    Compute and optionally apply price updates for all players in a season.

    Steps:
    1. Bulk-compute form_score for every player (5-GW weighted average)
    2. Compute average form per position (for delta comparison)
    3. For each player: derive price delta, update SC, write price history
    4. If preview=True, nothing is written to DB

    Returns a list of PriceUpdateResults for logging/display.
    """
    players = list(
        db.execute(
            select(Player)
            .where(Player.season_id == season_id)
            .order_by(Player.position, Player.name)
        ).scalars()
    )

    if not players:
        return []

    # Pass 1: bulk-compute form scores and appearance counts
    form_map: dict[int, float] = {}
    appearance_map: dict[int, int] = {}
    position_map: dict[int, str] = {}

    for player in players:
        form_map[player.id] = compute_form_score(db, player.id, season_id)
        appearance_map[player.id] = _count_recent_appearances(db, player.id, season_id)
        position_map[player.id] = player.position.value

    # Pass 2: position averages (only from players with sufficient data)
    eligible_form_map = {
        pid: form
        for pid, form in form_map.items()
        if appearance_map[pid] >= MIN_APPEARANCES_FOR_UPDATE
    }
    pos_avg = compute_position_avg_form(eligible_form_map, position_map)

    # Pass 3: compute deltas and apply
    results: list[PriceUpdateResult] = []

    for player in players:
        form_score = form_map[player.id]
        appearances = appearance_map[player.id]
        avg_form = pos_avg.get(player.position.value, 0.0)
        old_price = float(player.current_price)

        # Sparse data: skip price change, still update form_score
        if appearances < MIN_APPEARANCES_FOR_UPDATE:
            results.append(
                PriceUpdateResult(
                    player_id=player.id,
                    player_name=player.name,
                    position=player.position,
                    old_price=old_price,
                    new_price=old_price,
                    form_score=form_score,
                    position_avg_form=avg_form,
                    form_delta=0.0,
                    delta=0.0,
                    reason=f"skipped: only {appearances} appearance(s) in form window",
                    skipped=True,
                )
            )
            if not preview:
                player.form_score = form_score
            continue

        form_delta = round(form_score - avg_form, 2)
        delta = compute_price_delta(form_delta, old_price, player.position)
        new_price = old_price + delta

        if delta > 0:
            reason = f"form above avg by {form_delta:+.2f} pts/game"
        elif delta < 0:
            reason = f"form below avg by {form_delta:+.2f} pts/game"
        else:
            reason = f"form within threshold (delta {form_delta:+.2f})"

        results.append(
            PriceUpdateResult(
                player_id=player.id,
                player_name=player.name,
                position=player.position,
                old_price=old_price,
                new_price=new_price,
                form_score=form_score,
                position_avg_form=avg_form,
                form_delta=form_delta,
                delta=delta,
                reason=reason,
                skipped=(delta == 0.0),
            )
        )

        if not preview:
            # Update player fields
            player.form_score = form_score
            player.starter_confidence = compute_starter_confidence(db, player.id, season_id)

            if delta != 0.0:
                player.current_price = new_price
                record_price_change(
                    db,
                    player_id=player.id,
                    gameweek_id=gameweek_id,
                    old_price=old_price,
                    new_price=new_price,
                    reason=reason,
                )

    if not preview:
        db.commit()

    return results


def _count_recent_appearances(db: Session, player_id: int, season_id: int) -> int:
    """
    Count fixtures where this player appeared (appeared=True) in the form window.
    Used to enforce MIN_APPEARANCES_FOR_UPDATE sparse-data protection.
    """
    rows = list(
        db.execute(
            select(PlayerMatchStats.appeared)
            .join(Fixture, Fixture.id == PlayerMatchStats.fixture_id)
            .join(Gameweek, Gameweek.id == Fixture.gameweek_id)
            .where(
                PlayerMatchStats.player_id == player_id,
                Gameweek.season_id == season_id,
                Gameweek.status.in_(["FINISHED", "SCORING"]),
            )
            .order_by(Gameweek.number.desc())
            .limit(FORM_WINDOW_GWS)
        ).scalars()
    )
    return sum(1 for appeared in rows if appeared)
