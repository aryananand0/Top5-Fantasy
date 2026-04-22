#!/usr/bin/env python
"""
CLI for managing Top5 Fantasy gameweeks.

Commands:
    generate  --season LABEL [--weeks N]   Generate gameweek windows for a season
    assign    --season LABEL               Assign ingested fixtures to gameweeks
    refresh   --season LABEL               Refresh gameweek statuses and is_current flag

Usage (from apps/api/):
    python scripts/gameweeks.py generate --season 2024-25
    python scripts/gameweeks.py generate --season 2024-25 --weeks 38
    python scripts/gameweeks.py assign   --season 2024-25
    python scripts/gameweeks.py refresh  --season 2024-25

Typical workflow at season start:
    1. python scripts/sync.py fixtures          # ingest fixtures from football-data.org
    2. python scripts/gameweeks.py generate --season 2024-25
    3. python scripts/gameweeks.py assign   --season 2024-25
    4. python scripts/gameweeks.py refresh  --season 2024-25

Run assign + refresh again any time fixtures are re-ingested (reschedules, postponements).
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os  # noqa: E402
os.environ.setdefault("DATABASE_URL", "")

from sqlalchemy import select  # noqa: E402

from db.session import get_db  # noqa: E402
from models.season import Season  # noqa: E402
from services.gameweek import (  # noqa: E402
    assign_fixtures_to_gameweeks,
    generate_gameweeks_for_season,
    refresh_gameweek_statuses,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("gameweeks")

DEFAULT_WEEKS = 38


def _get_season(db, label: str) -> Season:
    season = db.execute(
        select(Season).where(Season.label == label)
    ).scalar_one_or_none()
    if not season:
        log.error("Season '%s' not found. Create it in the database first.", label)
        sys.exit(1)
    return season


def cmd_generate(db, args) -> None:
    season = _get_season(db, args.season)
    num_weeks = args.weeks or DEFAULT_WEEKS

    log.info(
        "Generating %d gameweeks for season '%s' starting %s ...",
        num_weeks,
        season.label,
        season.start_date.date(),
    )
    gws = generate_gameweeks_for_season(
        db,
        season_id=season.id,
        season_start=season.start_date,
        num_weeks=num_weeks,
    )
    log.info("Done — %d gameweeks ready (existing ones untouched).", len(gws))
    for gw in gws[:3]:
        log.info(
            "  GW%02d  %s → %s  (deadline %s)",
            gw.number,
            gw.start_at.strftime("%a %d %b %H:%M UTC"),
            gw.end_at.strftime("%a %d %b %H:%M UTC"),
            gw.deadline_at.strftime("%a %d %b %H:%M UTC"),
        )
    if len(gws) > 3:
        log.info("  ... and %d more.", len(gws) - 3)


def cmd_assign(db, args) -> None:
    season = _get_season(db, args.season)
    log.info("Assigning fixtures to gameweeks for season '%s' ...", season.label)
    count = assign_fixtures_to_gameweeks(db, season.id)
    log.info("Done — %d fixtures assigned.", count)


def cmd_refresh(db, args) -> None:
    season = _get_season(db, args.season)
    log.info("Refreshing gameweek statuses for season '%s' ...", season.label)
    changed = refresh_gameweek_statuses(db, season.id)
    if changed:
        for gw in changed:
            log.info("  GW%02d → %s", gw.number, gw.status.value)
    else:
        log.info("  No status changes.")
    log.info("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Top5 Fantasy gameweeks")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate gameweek windows for a season")
    p_gen.add_argument("--season", required=True, help="Season label, e.g. 2024-25")
    p_gen.add_argument("--weeks", type=int, default=DEFAULT_WEEKS, help="Number of gameweeks (default: 38)")

    p_assign = sub.add_parser("assign", help="Assign fixtures to gameweeks")
    p_assign.add_argument("--season", required=True, help="Season label, e.g. 2024-25")

    p_refresh = sub.add_parser("refresh", help="Refresh statuses and is_current flag")
    p_refresh.add_argument("--season", required=True, help="Season label, e.g. 2024-25")

    args = parser.parse_args()

    db_gen = get_db()
    db = next(db_gen)
    try:
        if args.command == "generate":
            cmd_generate(db, args)
        elif args.command == "assign":
            cmd_assign(db, args)
        elif args.command == "refresh":
            cmd_refresh(db, args)
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


if __name__ == "__main__":
    main()
