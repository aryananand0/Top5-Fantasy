#!/usr/bin/env python
"""
CLI for managing Top5 Fantasy player pricing.

Commands:
    init-prices   --season LABEL [--preview]
        Compute initial prices for all players in a season.
        Uses position base + team strength + starter confidence.

    update-prices --season LABEL --gameweek N [--preview]
        Run the weekly price update for a completed gameweek.
        Uses form_score vs position average to apply +0.1 / -0.1 moves.

Usage (from apps/api/):
    python scripts/pricing.py init-prices --season 2024-25
    python scripts/pricing.py init-prices --season 2024-25 --preview

    python scripts/pricing.py update-prices --season 2024-25 --gameweek 5
    python scripts/pricing.py update-prices --season 2024-25 --gameweek 5 --preview

Typical workflow:
    Season start:
        1. python scripts/sync.py all              # ingest teams + players
        2. python scripts/pricing.py init-prices --season 2024-25 --preview
        3. python scripts/pricing.py init-prices --season 2024-25

    After each scored gameweek:
        4. python scripts/pricing.py update-prices --season 2024-25 --gameweek N --preview
        5. python scripts/pricing.py update-prices --season 2024-25 --gameweek N
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
from models.gameweek import Gameweek  # noqa: E402
from models.season import Season  # noqa: E402
from services.pricing.initial import apply_initial_prices  # noqa: E402
from services.pricing.weekly import apply_weekly_updates  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pricing")


def _get_season(db, label: str) -> Season:
    season = db.execute(
        select(Season).where(Season.label == label)
    ).scalar_one_or_none()
    if not season:
        log.error("Season '%s' not found. Create it in the database first.", label)
        sys.exit(1)
    return season


def _get_gameweek(db, season_id: int, number: int) -> Gameweek:
    gw = db.execute(
        select(Gameweek).where(
            Gameweek.season_id == season_id,
            Gameweek.number == number,
        )
    ).scalar_one_or_none()
    if not gw:
        log.error("Gameweek %d not found for this season. Run gameweeks generate first.", number)
        sys.exit(1)
    return gw


def cmd_init_prices(db, args) -> None:
    season = _get_season(db, args.season)
    mode = "[PREVIEW] " if args.preview else ""
    log.info("%sGenerating initial prices for season '%s' ...", mode, season.label)

    results = apply_initial_prices(db, season.id, preview=args.preview)

    changed = [r for r in results if r.changed]
    unchanged = [r for r in results if not r.changed]

    log.info("%d players total — %d price changes, %d unchanged.", len(results), len(changed), len(unchanged))

    # Show sample of biggest changes and extreme prices
    if changed:
        log.info("Sample price changes (first 10):")
        for r in changed[:10]:
            log.info(
                "  %-30s [%s] team-str=%d  £%.1f → £%.1f",
                r.player_name[:30],
                r.position.value,
                r.team_strength,
                r.old_price,
                r.new_price,
            )

    # Show price distribution summary
    by_pos: dict[str, list[float]] = {}
    for r in results:
        by_pos.setdefault(r.position.value, []).append(r.new_price)
    log.info("Price distribution:")
    for pos, prices in sorted(by_pos.items()):
        log.info(
            "  %s: min=£%.1f  max=£%.1f  avg=£%.1f",
            pos,
            min(prices),
            max(prices),
            sum(prices) / len(prices),
        )

    if args.preview:
        log.info("[PREVIEW] No changes written to database.")
    else:
        log.info("Done — prices committed.")


def cmd_update_prices(db, args) -> None:
    season = _get_season(db, args.season)
    gw = _get_gameweek(db, season.id, args.gameweek)
    mode = "[PREVIEW] " if args.preview else ""

    log.info(
        "%sRunning weekly price update for season '%s', GW%d ...",
        mode,
        season.label,
        args.gameweek,
    )

    results = apply_weekly_updates(db, season.id, gw.id, preview=args.preview)

    rises = [r for r in results if r.delta > 0]
    drops = [r for r in results if r.delta < 0]
    skipped = [r for r in results if r.skipped]

    log.info(
        "%d players: +%d rises, -%d drops, %d unchanged/skipped.",
        len(results),
        len(rises),
        len(drops),
        len(skipped),
    )

    if rises:
        log.info("Price rises:")
        for r in rises[:10]:
            log.info(
                "  %-30s [%s] £%.1f → £%.1f  (%s)",
                r.player_name[:30],
                r.position.value,
                r.old_price,
                r.new_price,
                r.reason,
            )
        if len(rises) > 10:
            log.info("  ... and %d more.", len(rises) - 10)

    if drops:
        log.info("Price drops:")
        for r in drops[:10]:
            log.info(
                "  %-30s [%s] £%.1f → £%.1f  (%s)",
                r.player_name[:30],
                r.position.value,
                r.old_price,
                r.new_price,
                r.reason,
            )
        if len(drops) > 10:
            log.info("  ... and %d more.", len(drops) - 10)

    if args.preview:
        log.info("[PREVIEW] No changes written to database.")
    else:
        log.info("Done — price changes committed and price_history updated.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Top5 Fantasy player pricing")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-prices", help="Generate initial prices for all players")
    p_init.add_argument("--season", required=True, help="Season label, e.g. 2024-25")
    p_init.add_argument("--preview", action="store_true", help="Show proposed changes without writing")

    p_update = sub.add_parser("update-prices", help="Run weekly price update after a scored gameweek")
    p_update.add_argument("--season", required=True, help="Season label, e.g. 2024-25")
    p_update.add_argument("--gameweek", type=int, required=True, help="Gameweek number (e.g. 5)")
    p_update.add_argument("--preview", action="store_true", help="Show proposed changes without writing")

    args = parser.parse_args()

    db_gen = get_db()
    db = next(db_gen)
    try:
        if args.command == "init-prices":
            cmd_init_prices(db, args)
        elif args.command == "update-prices":
            cmd_update_prices(db, args)
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


if __name__ == "__main__":
    main()
