"""
Shared FastAPI dependencies.

Use these Annotated types in route signatures:

    from core.dependencies import DBSession, AppSettings, CurrentUser

    @router.get("/protected")
    def protected_route(db: DBSession, current_user: CurrentUser):
        ...

Adding a new shared dependency: define it here, then import in route files.
Never import db/ or core/ internals directly inside route handlers.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.config import Settings, get_settings
from core.security import decode_access_token
from db.session import get_db
from models.user import User

# --- Core dependencies ---

DBSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]

# --- Auth ---

_bearer = HTTPBearer()


def _get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> User:
    """
    Decodes the Bearer token and returns the authenticated User.

    Raises 401 if the token is missing, invalid, or expired.
    Raises 401 if the user no longer exists or is inactive.

    Override this in tests via app.dependency_overrides[_get_current_user].
    """
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Deferred import to avoid a circular dependency:
    # services.auth → models.user → (fine)
    # core.dependencies → services.auth → core.security → core.config (fine)
    from services.auth import get_user_by_id
    user = get_user_by_id(db, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(_get_current_user)]
