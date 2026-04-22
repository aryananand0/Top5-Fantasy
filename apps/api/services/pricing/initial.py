"""
Initial player pricing.

Computes a starting price for every player in a season using:
    price = POSITION_BASE[pos] + STRENGTH_BONUS[team.strength] + SC_BONUS[starter_confidence]

Rounded to nearest 0.5 and clamped to position min/max.

At season start, all players have starter_confidence=3 (neutral) so the
effective formula is: POSITION_BASE + STRENGTH_BONUS. Prices differentiate
meaningfully by position and club quality right away.

Run once per season with: python scripts/pricing.py init-prices --season 2024-25
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import Position
from models.player import Player
from models.team import Team
from services.pricing.constants import (
    POSITION_BASE,
    SC_BONUS,
    STRENGTH_BONUS,
)
from services.pricing.utils import clamp_price, round_to_half


@dataclass
class InitialPriceResult:
    player_id: int
    player_name: str
    position: Position
    team_name: str
    team_strength: int
    starter_confidence: int
    old_price: float
    new_price: float
    changed: bool


def compute_initial_price(position: Position, team_strength: int, starter_confidence: int = 3) -> float:
    """
    Pure function — compute initial price from the three available inputs.

    Rounded to nearest 0.5 and clamped to position bounds.
    Safe to call without DB access (useful for tests and previews).
    """
    raw = (
        POSITION_BASE[position]
        + STRENGTH_BONUS.get(team_strength, 0.0)
        + SC_BONUS.get(starter_confidence, 0.0)
    )
    return round_to_half(clamp_price(raw, position))


def apply_initial_prices(
    db: Session,
    season_id: int,
    *,
    preview: bool = False,
) -> list[InitialPriceResult]:
    """
    Compute and optionally apply initial prices for all players in a season.

    - preview=True: computes prices but does NOT write to DB. Use for dry-runs.
    - preview=False: writes base_price and current_price to every player row.

    Idempotent: safe to rerun. base_price is always reset to the computed value.
    current_price is also reset (price history is not written here — that's
    done by weekly.py for in-season updates).

    Returns a list of results for logging/display.
    """
    players = list(
        db.execute(
            select(Player, Team)
            .join(Team, Team.id == Player.team_id)
            .where(Player.season_id == season_id)
            .order_by(Player.position, Team.name, Player.name)
        ).all()
    )

    results: list[InitialPriceResult] = []

    for player, team in players:
        new_price = compute_initial_price(
            player.position,
            team.strength,
            player.starter_confidence,
        )
        changed = player.current_price != new_price or player.base_price != new_price

        results.append(
            InitialPriceResult(
                player_id=player.id,
                player_name=player.name,
                position=player.position,
                team_name=team.name,
                team_strength=team.strength,
                starter_confidence=player.starter_confidence,
                old_price=float(player.current_price),
                new_price=new_price,
                changed=changed,
            )
        )

        if not preview:
            player.base_price = new_price
            player.current_price = new_price

    if not preview:
        db.commit()

    return results
