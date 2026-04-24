"""
Dashboard route.

GET /api/v1/dashboard — single aggregated payload for the authenticated user.
All data is assembled in one pass; the frontend makes exactly one call.
"""

from fastapi import APIRouter

from core.dependencies import CurrentUser, DBSession
from schemas.dashboard import DashboardSummary
from services.dashboard import get_dashboard_summary

router = APIRouter()


@router.get(
    "",
    response_model=DashboardSummary,
    summary="Get authenticated user's dashboard summary",
)
def get_dashboard(
    db: DBSession,
    current_user: CurrentUser,
) -> DashboardSummary:
    return get_dashboard_summary(db, current_user)
