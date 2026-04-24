"""
Scoring read routes.

GET /gameweeks/current/score   — authenticated user's score for the current gameweek
GET /gameweeks/{gw_id}/score   — authenticated user's score for a specific gameweek

These routes return computed scores. Scores are written by the scoring job
(scripts/score.py), not computed on-the-fly here. If the job hasn't run yet,
a 202 Accepted is returned so the frontend can show a "scoring in progress" state.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.dependencies import CurrentUser, DBSession
from models.gameweek import Gameweek
from models.lineup import GameweekLineup, GameweekLineupPlayer
from models.player import Player
from models.scoring import UserGameweekScore
from models.team import Team
from models.user import User
from schemas.scoring import GameweekScoreNotReady, GameweekScoreResponse, PlayerGWScore

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_current_gameweek(db: Session) -> Gameweek | None:
    return db.execute(
        select(Gameweek).where(Gameweek.is_current.is_(True))
    ).scalar_one_or_none()


def _build_score_response(
    db: Session,
    gw: Gameweek,
    score: UserGameweekScore,
) -> GameweekScoreResponse:
    """Assemble the full score response including per-player breakdown."""
    lineup = db.get(GameweekLineup, score.lineup_id)

    captain_id = lineup.captain_player_id if lineup else None
    vc_id = lineup.vice_captain_player_id if lineup else None

    lineup_player_rows: list[GameweekLineupPlayer] = []
    if lineup:
        lineup_player_rows = list(
            db.execute(
                select(GameweekLineupPlayer).where(
                    GameweekLineupPlayer.lineup_id == lineup.id
                )
            ).scalars().all()
        )

    players_out: list[PlayerGWScore] = []
    for lp in lineup_player_rows:
        player = db.get(Player, lp.player_id)
        team = db.get(Team, player.team_id) if player else None
        if not player or not team:
            continue

        is_cap = lp.player_id == captain_id
        is_vc = lp.player_id == vc_id
        # points_scored already includes the 2× multiplier for whoever earned it.
        # base_points == final_points here — the multiplier is baked into points_scored
        # and surfaced separately in UserGameweekScore.captain_points.
        final = lp.points_scored or 0

        players_out.append(PlayerGWScore(
            player_id=player.id,
            name=player.name,
            display_name=player.display_name,
            position=player.position,
            team_name=team.name,
            is_captain=is_cap,
            is_vice_captain=is_vc,
            base_points=final,
            final_points=final,
            points_scored=lp.points_scored,
        ))

    return GameweekScoreResponse(
        gameweek_id=gw.id,
        gameweek_number=gw.number,
        gameweek_name=gw.name,
        points=score.points,
        transfer_cost=score.transfer_cost,
        captain_bonus=score.captain_points,
        rank_global=score.rank_global,
        players=players_out,
        updated_at=score.updated_at,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "/current/score",
    response_model=GameweekScoreResponse,
    responses={202: {"model": GameweekScoreNotReady}},
    summary="Get current user's score for the current gameweek",
)
def get_current_gameweek_score(
    db: DBSession,
    current_user: CurrentUser,
):
    gw = _get_current_gameweek(db)
    if gw is None:
        raise HTTPException(status_code=404, detail="No active gameweek found.")

    return _get_score_for_gameweek(db, current_user, gw)


@router.get(
    "/{gw_id}/score",
    response_model=GameweekScoreResponse,
    responses={202: {"model": GameweekScoreNotReady}},
    summary="Get current user's score for a specific gameweek",
)
def get_gameweek_score(
    gw_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    gw = db.get(Gameweek, gw_id)
    if gw is None:
        raise HTTPException(status_code=404, detail="Gameweek not found.")

    return _get_score_for_gameweek(db, current_user, gw)


def _get_score_for_gameweek(
    db: Session,
    user: User,
    gw: Gameweek,
):
    score = db.execute(
        select(UserGameweekScore).where(
            UserGameweekScore.user_id == user.id,
            UserGameweekScore.gameweek_id == gw.id,
        )
    ).scalar_one_or_none()

    if score is None:
        # Scoring job hasn't run yet for this user / GW
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=202,
            content=GameweekScoreNotReady(
                gameweek_id=gw.id,
                gameweek_number=gw.number,
                gameweek_name=gw.name,
            ).model_dump(),
        )

    return _build_score_response(db, gw, score)
