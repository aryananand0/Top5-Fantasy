"""
Price history recording.

One row in price_history per player per gameweek, written whenever a player's
price actually changes. Idempotent via upsert on (player_id, gameweek_id).
"""

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from models.player import PriceHistory


def record_price_change(
    db: Session,
    *,
    player_id: int,
    gameweek_id: int,
    old_price: float,
    new_price: float,
    reason: str = "",
) -> None:
    """
    Upsert one price_history row for a player + gameweek.

    If called twice for the same (player_id, gameweek_id) — e.g. because the
    update script was rerun — the row is updated in place.

    Does NOT commit — caller is responsible for the transaction.
    """
    change_amount = round(new_price - old_price, 1)
    stmt = pg_insert(PriceHistory).values(
        player_id=player_id,
        gameweek_id=gameweek_id,
        old_price=old_price,
        new_price=new_price,
        change_amount=change_amount,
        reason_summary=reason[:200] if reason else None,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_price_history_player_gw",
        set_={
            "old_price": stmt.excluded.old_price,
            "new_price": stmt.excluded.new_price,
            "change_amount": stmt.excluded.change_amount,
            "reason_summary": stmt.excluded.reason_summary,
        },
    )
    db.execute(stmt)
