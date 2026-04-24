"""
Sync fixtures for all supported competitions.

One API request per competition: GET /competitions/{code}/matches
Upserts on external_id (football-data.org match ID).

home_team_id / away_team_id are resolved by looking up teams by external_id.
Fixtures referencing unknown teams are skipped with a warning.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from models.enums import DataQuality
from models.fixture import Fixture
from models.team import Team
from services.ingestion.client import FootballDataClient
from services.ingestion.constants import SUPPORTED_COMPETITIONS
from services.ingestion.utils import (
    get_competition_by_code,
    normalize_fixture_status,
)

log = logging.getLogger(__name__)


def _parse_kickoff(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_fixture_row(
    raw: dict,
    competition_id: int,
    team_lookup: dict[int, int],
) -> Optional[dict]:
    """Return a dict suitable for Fixture upsert, or None if teams can't be resolved."""
    external_id = raw.get("id")
    if not external_id:
        return None

    home_ext = (raw.get("homeTeam") or {}).get("id")
    away_ext = (raw.get("awayTeam") or {}).get("id")
    home_team_id = team_lookup.get(home_ext)
    away_team_id = team_lookup.get(away_ext)

    if home_team_id is None or away_team_id is None:
        log.debug("Skipping fixture %s — unknown team(s): home=%s away=%s", external_id, home_ext, away_ext)
        return None

    score = raw.get("score", {})
    full_time = score.get("fullTime") or {}
    home_score = full_time.get("home")
    away_score = full_time.get("away")

    status = normalize_fixture_status(raw.get("status"))
    kickoff_at = _parse_kickoff(raw.get("utcDate"))

    return {
        "external_id": external_id,
        "competition_id": competition_id,
        "home_team_id": home_team_id,
        "away_team_id": away_team_id,
        "kickoff_at": kickoff_at,
        "status": status,
        "home_score": home_score,
        "away_score": away_score,
        "data_quality_status": DataQuality.FULL.value,
        "fetched_at": datetime.now(tz=timezone.utc),
    }


def sync_fixtures(db: Session, client: FootballDataClient) -> int:
    """Fetch and upsert fixtures for all supported competitions. Returns total rows written."""
    # Build external_id → internal id lookup once
    team_lookup: dict[int, int] = {
        ext_id: internal_id
        for ext_id, internal_id in db.query(Team.external_id, Team.id)
        .filter(Team.external_id.isnot(None))
        .all()
    }

    total = 0

    for comp_cfg in SUPPORTED_COMPETITIONS:
        code = comp_cfg["code"]
        competition = get_competition_by_code(db, code)
        if competition is None:
            log.warning("Competition %s not found — run sync competitions first", code)
            continue

        log.info("Fetching fixtures for %s (%s)…", comp_cfg["name"], code)
        data = client.get(f"/competitions/{code}/matches")
        raw_matches = data.get("matches", [])

        rows = []
        for raw in raw_matches:
            row = _parse_fixture_row(raw, competition.id, team_lookup)
            if row:
                rows.append(row)

        if not rows:
            log.info("No fixtures returned for %s", code)
            continue

        stmt = pg_insert(Fixture).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_fixture_external_id",
            set_={
                "status": stmt.excluded.status,
                "home_score": stmt.excluded.home_score,
                "away_score": stmt.excluded.away_score,
                "kickoff_at": stmt.excluded.kickoff_at,
                "data_quality_status": stmt.excluded.data_quality_status,
                "fetched_at": stmt.excluded.fetched_at,
            },
        )
        db.execute(stmt)
        db.commit()

        log.info("Synced %d fixtures for %s", len(rows), code)
        total += len(rows)

    return total
