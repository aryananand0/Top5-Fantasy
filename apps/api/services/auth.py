"""
Auth service: user creation, lookup, and credential verification.

All database access lives here — routes never touch the ORM directly.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import hash_password, verify_password
from models.user import User
from schemas.auth import SignupRequest


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.execute(
        select(User).where(User.email == email.lower().strip())
    ).scalar_one_or_none()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.execute(
        select(User).where(User.username == username.lower().strip())
    ).scalar_one_or_none()


def create_user(db: Session, data: SignupRequest) -> User:
    user = User(
        email=data.email.lower().strip(),
        username=data.username.lower().strip(),
        password_hash=hash_password(data.password),
        display_name=data.display_name.strip() if data.display_name else data.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, login: str, password: str) -> Optional[User]:
    """
    Verify credentials and return the User, or None.

    Accepts either email or username in the `login` field.
    Returns None for any failure — never reveals whether the account exists.
    """
    login = login.strip()
    user = (
        get_user_by_email(db, login)
        if "@" in login
        else get_user_by_username(db, login)
    )
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
