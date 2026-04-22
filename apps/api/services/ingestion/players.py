"""
Sync players for all teams.

One API request per team: GET /teams/{external_id}
The squad list is embedded in the team response (no extra call needed).

Upserts on (external_id, season_id) — same player can appear in future seasons
as a new row with fresh pricing.
"""

import logging
from typing import Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from models.player import Player
from models.team import Team
from services.ingestion.client import FootballDataClient
from services.ingestion.utils import (
    get_default_price,
    get_or_create_season,
    normalize_position,
)

log = logging.getLogger(__name__)


def _parse_player_row(raw: dict, team_id: int, season_id: int) -> Optional[dict]:
    """Return a dict suitable for Player upsert, or None if missing required fields."""
    external_id = raw.get("id")
    name = raw.get("name")
    if not external_id or not name:
        return None

    position = normalize_position(raw.get("position"))
    price = get_default_price(position)

    return {
        "external_id": external_id,
        "name": name,
        "position": position,
        "team_id": team_id,
        "season_id": season_id,
        "nationality": raw.get("nationality"),
        "base_price": price,
        "current_price": price,
    }


def sync_players(db: Session, client: FootballDataClient) -> int:
    """Fetch squad lists for every team and upsert players. Returns total rows written."""
    season = get_or_create_season(db)
    teams = db.query(Team).filter(Team.external_id.isnot(None)).all()

    if not teams:
        log.warning("No teams with external_id found — run sync teams first")
        return 0

    total = 0

    for team in teams:
        log.info("Fetching squad for team %s (id=%s)…", team.name, team.external_id)
        data = client.get(f"/teams/{team.external_id}")
        raw_squad = data.get("squad", [])

        rows = []
        for raw in raw_squad:
            row = _parse_player_row(raw, team.id, season.id)
            if row:
                rows.append(row)

        if not rows:
            log.info("No players returned for team %s", team.name)
            continue

        stmt = pg_insert(Player).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_player_external_season",
            set_={
                "name": stmt.excluded.name,
                "position": stmt.excluded.position,
                "team_id": stmt.excluded.team_id,
                "nationality": stmt.excluded.nationality,
                # base_price and current_price intentionally NOT updated —
                # those are owned by the pricing engine after initial seed.
            },
        )
        db.execute(stmt)
        db.commit()

        log.info("Synced %d players for %s", len(rows), team.name)
        total += len(rows)

    return total
