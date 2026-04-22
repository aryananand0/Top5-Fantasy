from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from core.dependencies import CurrentUser, DBSession
from core.security import create_access_token
from schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from services.auth import authenticate_user, create_user, get_user_by_email, get_user_by_username

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
def signup(data: SignupRequest, db: DBSession):
    # Check uniqueness before attempting insert so we return clear error messages.
    # An IntegrityError fallback handles the race-condition case.
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    if get_user_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken.",
        )
    try:
        return create_user(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account creation failed. Email or username is already in use.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive an access token",
)
def login(data: LoginRequest, db: DBSession):
    user = authenticate_user(db, data.login, data.password)
    if not user:
        # Deliberately vague — do not reveal whether the account exists
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id))


@router.post(
    "/logout",
    summary="Log out",
)
def logout() -> dict:
    """
    JWT is stateless — the server holds no session state to invalidate.
    Logout is completed client-side by discarding the stored token.

    This endpoint exists so:
    1. All clients have a consistent logout call to make.
    2. A token blocklist can be added here later (e.g. for forced logout on
       password change) without any client-side API changes.
    """
    return {"message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the authenticated user's profile",
)
def me(current_user: CurrentUser):
    return current_user
