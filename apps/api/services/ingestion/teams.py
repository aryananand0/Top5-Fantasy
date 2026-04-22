"""
Sync teams for all supported competitions.

One API request per competition: GET /competitions/{code}/teams
Upserts on external_id (football-data.org team ID).
"""

import logging
from typing import Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from models.team import Team
from services.ingestion.client import FootballDataClient
from services.ingestion.constants import SUPPORTED_COMPETITIONS
from services.ingestion.utils import get_competition_by_code

log = logging.getLogger(__name__)


def _parse_team_row(raw: dict, competition_id: int) -> Optional[dict]:
    """Return a dict suitable for Team upsert, or None if missing required fields."""
    external_id = raw.get("id")
    name = raw.get("name") or raw.get("shortName")
    if not external_id or not name:
        return None
    return {
        "external_id": external_id,
        "name": name,
        "short_name": raw.get("shortName"),
        "tla": raw.get("tla"),
        "competition_id": competition_id,
    }


def sync_teams(db: Session, client: FootballDataClient) -> int:
    """Fetch and upsert teams for all supported competitions. Returns total rows written."""
    total = 0

    for comp_cfg in SUPPORTED_COMPETITIONS:
        code = comp_cfg["code"]
        competition = get_competition_by_code(db, code)
        if competition is None:
            log.warning("Competition %s not found — run sync competitions first", code)
            continue

        log.info("Fetching teams for %s (%s)…", comp_cfg["name"], code)
        data = client.get(f"/competitions/{code}/teams")
        raw_teams = data.get("teams", [])

        rows = []
        for raw in raw_teams:
            row = _parse_team_row(raw, competition.id)
            if row:
                rows.append(row)

        if not rows:
            log.warning("No teams returned for %s", code)
            continue

        stmt = pg_insert(Team).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["external_id"],
            set_={
                "name": stmt.excluded.name,
                "short_name": stmt.excluded.short_name,
                "tla": stmt.excluded.tla,
                "competition_id": stmt.excluded.competition_id,
            },
        )
        db.execute(stmt)
        db.commit()

        log.info("Synced %d teams for %s", len(rows), code)
        total += len(rows)

    return total
