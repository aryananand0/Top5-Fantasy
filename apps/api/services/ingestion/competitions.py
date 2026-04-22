"""
Sync competitions from local constants — no API call needed.

The Top 5 leagues are stable; seeding from constants avoids spending an API
request just to populate 5 rows. If external_id is needed later, it can be
backfilled via a one-off script.
"""

import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from models.competition import Competition
from services.ingestion.constants import SUPPORTED_COMPETITIONS

log = logging.getLogger(__name__)


def sync_competitions(db: Session) -> int:
    """Upsert the 5 supported competitions and return the count written."""
    rows = [
        {
            "code": c["code"],
            "name": c["name"],
            "country": c["country"],
        }
        for c in SUPPORTED_COMPETITIONS
    ]

    stmt = pg_insert(Competition).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["code"],
        set_={
            "name": stmt.excluded.name,
            "country": stmt.excluded.country,
        },
    )
    db.execute(stmt)
    db.commit()

    log.info("Synced %d competitions", len(rows))
    return len(rows)
