#!/usr/bin/env python
"""
CLI script for scoring fixtures, gameweeks, and users.

Commands:
    score-fixture   <fixture_id>              Score all PlayerMatchStats for one fixture
    score-gameweek  <gameweek_id>             Score all fixtures + lineups for a gameweek
    finalize-ranks  <gameweek_id>             Assign rank_global after all scores are in
    recompute-user  <gameweek_id> <user_id>   Recompute one user's lineup score for a GW

Usage (from apps/api/):
    python scripts/score.py score-fixture 42
    python scripts/score.py score-gameweek 5
    python scripts/score.py finalize-ranks 5
    python scripts/score.py recompute-user 5 12

Typical post-match workflow:
    1. python scripts/sync.py fixtures          # Pull latest fixture results + player stats
    2. python scripts/score.py score-gameweek 5 # Score everything in GW 5
    3. python scripts/score.py finalize-ranks 5 # Assign global rankings

Re-running any command is safe — all operations are idempotent.
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os  # noqa: E402
os.environ.setdefault("DATABASE_URL", "")

from db.session import get_db  # noqa: E402
from services.scoring import (  # noqa: E402
    compute_fixture_player_points,
    compute_and_save_lineup_points,
    finalize_gameweek_ranks,
    score_gameweek,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("score")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_score_fixture(args: argparse.Namespace) -> None:
    fixture_id: int = args.fixture_id
    log.info("Scoring fixture %d …", fixture_id)
    db_gen = get_db()
    db = next(db_gen)
    try:
        result = compute_fixture_player_points(db, fixture_id)
        log.info(
            "Done. Fixture %d: %d players scored (mode=%s)",
            result.fixture_id, result.players_scored, result.scoring_mode,
        )
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


def cmd_score_gameweek(args: argparse.Namespace) -> None:
    gameweek_id: int = args.gameweek_id
    log.info("Scoring gameweek %d …", gameweek_id)
    db_gen = get_db()
    db = next(db_gen)
    try:
        report = score_gameweek(db, gameweek_id)
        log.info(
            "Done. GW %d: %d fixtures, %d lineups scored. %d fixtures skipped, %d lineups skipped.",
            report.gameweek_id,
            report.fixtures_scored,
            report.lineups_scored,
            report.fixtures_skipped,
            report.lineups_skipped,
        )
        if report.user_scores:
            log.info("User scores:")
            for s in sorted(report.user_scores, key=lambda x: x.final_points, reverse=True):
                log.info(
                    "  user_id=%-6d | raw=%-3d | hit=%-2d | final=%-3d | cap_bonus=%d",
                    s.user_id, s.raw_points, s.transfer_cost, s.final_points, s.captain_bonus,
                )
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


def cmd_finalize_ranks(args: argparse.Namespace) -> None:
    gameweek_id: int = args.gameweek_id
    log.info("Finalizing ranks for gameweek %d …", gameweek_id)
    db_gen = get_db()
    db = next(db_gen)
    try:
        count = finalize_gameweek_ranks(db, gameweek_id)
        log.info("Done. Ranked %d users for gameweek %d.", count, gameweek_id)
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


def cmd_recompute_user(args: argparse.Namespace) -> None:
    """
    Recompute one user's lineup score for a specific gameweek.

    Useful when:
      - A fixture's PlayerMatchStats were updated after initial scoring
      - A specific user's score looks wrong and needs a fresh pass
    """
    gameweek_id: int = args.gameweek_id
    user_id: int = args.user_id
    log.info("Recomputing score for user %d in gameweek %d …", user_id, gameweek_id)

    from sqlalchemy import select
    from models.lineup import GameweekLineup
    from models.squad import Squad

    db_gen = get_db()
    db = next(db_gen)
    try:
        # Find the user's squad
        squad = db.execute(
            select(Squad).where(Squad.user_id == user_id)
        ).scalar_one_or_none()
        if squad is None:
            log.error("No squad found for user %d", user_id)
            sys.exit(1)

        # Find their locked lineup for this GW
        lineup = db.execute(
            select(GameweekLineup).where(
                GameweekLineup.squad_id == squad.id,
                GameweekLineup.gameweek_id == gameweek_id,
            )
        ).scalar_one_or_none()
        if lineup is None:
            log.error(
                "No lineup found for user %d in gameweek %d", user_id, gameweek_id
            )
            sys.exit(1)

        if not lineup.is_locked:
            log.warning(
                "Lineup %d is not locked. Scoring pre-lock lineups is unusual.",
                lineup.id,
            )

        result = compute_and_save_lineup_points(db, lineup.id)

        # Also upsert the UserGameweekScore
        from services.scoring.aggregate_gameweek_scores import _upsert_user_gw_score
        transfer_cost = lineup.transfer_cost_applied
        final = result.total_points - transfer_cost
        _upsert_user_gw_score(
            db,
            user_id=user_id,
            squad_id=squad.id,
            gameweek_id=gameweek_id,
            lineup_id=lineup.id,
            raw_points=result.total_points,
            transfer_cost=transfer_cost,
            captain_bonus=result.captain_bonus,
            final_points=final,
        )
        log.info(
            "Done. User %d | GW %d | raw=%d | hit=%d | final=%d | cap_bonus=%d",
            user_id, gameweek_id, result.total_points, transfer_cost, final, result.captain_bonus,
        )
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="score.py",
        description="Top5 Fantasy scoring commands",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_fixture = sub.add_parser("score-fixture", help="Score one fixture's player stats")
    p_fixture.add_argument("fixture_id", type=int)

    p_gw = sub.add_parser("score-gameweek", help="Score all fixtures + lineups in a gameweek")
    p_gw.add_argument("gameweek_id", type=int)

    p_ranks = sub.add_parser("finalize-ranks", help="Assign rank_global for a gameweek")
    p_ranks.add_argument("gameweek_id", type=int)

    p_user = sub.add_parser("recompute-user", help="Recompute one user's GW score")
    p_user.add_argument("gameweek_id", type=int)
    p_user.add_argument("user_id", type=int)

    return parser


COMMANDS = {
    "score-fixture": cmd_score_fixture,
    "score-gameweek": cmd_score_gameweek,
    "finalize-ranks": cmd_finalize_ranks,
    "recompute-user": cmd_recompute_user,
}


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)
