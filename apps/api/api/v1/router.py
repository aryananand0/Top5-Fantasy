"""
API v1 router.

Register all v1 route modules here. Each module exposes an APIRouter
that is included with a prefix and tag set.

Plug in future routes by adding:
    from api.v1.routes import auth, players, squads, ...
    router.include_router(auth.router, prefix="/auth", tags=["auth"])
"""

from fastapi import APIRouter

from api.v1.routes import auth, health

router = APIRouter()

# System routes — no auth required
router.include_router(health.router)

# Auth
router.include_router(auth.router, prefix="/auth", tags=["auth"])

# --- Future routes (plug in as each step is implemented) ---

# from api.v1.routes import users
# router.include_router(users.router, prefix="/users", tags=["users"])

# from api.v1.routes import players
# router.include_router(players.router, prefix="/players", tags=["players"])

# from api.v1.routes import fixtures
# router.include_router(fixtures.router, prefix="/fixtures", tags=["fixtures"])

# from api.v1.routes import gameweeks
# router.include_router(gameweeks.router, prefix="/gameweeks", tags=["gameweeks"])

# from api.v1.routes import squads
# router.include_router(squads.router, prefix="/squads", tags=["squads"])

# from api.v1.routes import transfers
# router.include_router(transfers.router, prefix="/transfers", tags=["transfers"])

# from api.v1.routes import leagues
# router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
