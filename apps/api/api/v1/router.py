"""
API v1 router.

Register all v1 route modules here. Each module exposes an APIRouter
that is included with a prefix and tag set.

Plug in future routes by adding:
    from api.v1.routes import auth, players, squads, ...
    router.include_router(auth.router, prefix="/auth", tags=["auth"])
"""

from fastapi import APIRouter

from api.v1.routes import auth, dashboard, fixtures, gameweeks, health, lineup, players, scoring, squad, transfer

router = APIRouter()

# System routes — no auth required
router.include_router(health.router)

# Auth
router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Gameweeks (Step 8)
router.include_router(gameweeks.router, prefix="/gameweeks", tags=["gameweeks"])

# Players browser (Step 10)
router.include_router(players.router, prefix="/players", tags=["players"])

# Squad management (Step 10)
router.include_router(squad.router, prefix="/squad", tags=["squad"])

# Gameweek lineup / captain selection (Step 12)
router.include_router(lineup.router, prefix="/lineups", tags=["lineups"])

# Transfer system (Step 13)
router.include_router(transfer.router, prefix="/transfers", tags=["transfers"])

# Scoring read endpoints (Step 14)
router.include_router(scoring.router, prefix="/gameweeks", tags=["scoring"])

# Dashboard aggregation (Step 15)
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Fixtures
router.include_router(fixtures.router, prefix="/fixtures", tags=["fixtures"])

# --- Future routes ---

# from api.v1.routes import leagues
# router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
