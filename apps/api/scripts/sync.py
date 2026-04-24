#!/usr/bin/env python3
"""
CLI script for manually triggering data ingestion from football-data.org.

Usage (from apps/api/):
    python scripts/sync.py competitions
    python scripts/sync.py teams
    python scripts/sync.py players
    python scripts/sync.py fixtures
    python scripts/sync.py all
"""

import argparse
import logging
import sys
from pathlib import Path

# Make apps/api/ importable regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import get_settings  # noqa: E402
from db.session import get_db  # noqa: E402
from services.ingestion.client import FootballDataClient  # noqa: E402
from services.ingestion.competitions import sync_competitions  # noqa: E402
from services.ingestion.fixtures import sync_fixtures  # noqa: E402
from services.ingestion.players import sync_players  # noqa: E402
from services.ingestion.teams import sync_teams  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("sync")


def _get_client() -> FootballDataClient:
    settings = get_settings()
    if not settings.FOOTBALL_DATA_API_KEY:
        log.error("FOOTBALL_DATA_API_KEY is not set in .env")
        sys.exit(1)
    return FootballDataClient(api_key=settings.FOOTBALL_DATA_API_KEY)


def run(command: str) -> None:
    db_gen = get_db()
    db = next(db_gen)
    try:
        if command == "competitions":
            n = sync_competitions(db)
            log.info("Done: %d competitions", n)

        elif command == "teams":
            with _get_client() as client:
                n = sync_teams(db, client)
            log.info("Done: %d teams", n)

        elif command == "players":
            with _get_client() as client:
                n = sync_players(db, client)
            log.info("Done: %d players", n)

        elif command == "fixtures":
            with _get_client() as client:
                n = sync_fixtures(db, client)
            log.info("Done: %d fixtures", n)

        elif command == "all":
            log.info("=== competitions ===")
            sync_competitions(db)

            with _get_client() as client:
                log.info("=== teams ===")
                sync_teams(db, client)

                log.info("=== players ===")
                sync_players(db, client)

                log.info("=== fixtures ===")
                sync_fixtures(db, client)

            log.info("Full sync complete.")
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync football data from football-data.org")
    parser.add_argument(
        "command",
        choices=["competitions", "teams", "players", "fixtures", "all"],
        help="Which data to sync",
    )
    args = parser.parse_args()
    run(args.command)


if __name__ == "__main__":
    main()
