"""
Shared Pydantic response types used across multiple route modules.

Keep domain-specific schemas (player, squad, auth, etc.) in their own files:
  schemas/auth.py     — Step 6
  schemas/player.py   — Step 7
  schemas/squad.py    — Step 8
  ...
"""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Generic success response for operations that don't return a resource."""
    message: str


class ErrorResponse(BaseModel):
    """Matches FastAPI's default HTTPException response shape."""
    detail: str
