from fastapi import APIRouter

from db.session import check_db_connection

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    tags=["system"],
)
def health_check() -> dict:
    """
    Returns the operational status of the API and its database connection.
    Used by load balancers, monitoring, and the frontend to detect outages.
    """
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "unreachable",
        "version": "0.1.0",
    }


@router.get(
    "/info",
    summary="API info",
    tags=["system"],
)
def api_info() -> dict:
    """Basic API metadata. Safe to call without authentication."""
    return {
        "name": "Top5 Fantasy API",
        "version": "0.1.0",
        "description": "Season-long fantasy soccer across the top 5 European leagues.",
    }
