"""
Auth security utilities: password hashing and JWT.

Intentionally kept as pure functions with no FastAPI or SQLAlchemy imports
so they stay easy to unit-test in isolation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt as _bcrypt
from jose import JWTError, jwt

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


# --- Password ---

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


# --- JWT ---

def create_access_token(user_id: int, expires_days: int = ACCESS_TOKEN_EXPIRE_DAYS) -> str:
    """Creates a signed JWT with the user ID as the subject."""
    from core.config import get_settings  # deferred to avoid module-load side effects
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=expires_days),
    }
    return jwt.encode(payload, get_settings().SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    """
    Validates a JWT and returns the user ID (int).
    Returns None for any invalid or expired token — never raises.
    """
    try:
        from core.config import get_settings
        payload = jwt.decode(token, get_settings().SECRET_KEY, algorithms=[ALGORITHM])
        sub: Optional[str] = payload.get("sub")
        if sub is None:
            return None
        return int(sub)
    except (JWTError, ValueError):
        return None
