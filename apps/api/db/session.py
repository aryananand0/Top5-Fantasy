from collections.abc import Generator
from typing import Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Engine and session factory are initialized lazily on first use.
# This avoids importing settings at module load time, which would
# break test imports before environment variables are configured.
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        from core.config import get_settings
        s = get_settings()
        _engine = create_engine(
            s.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=s.DEBUG,
        )
    return _engine


def _get_session_factory() -> sessionmaker:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=_get_engine(),
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a request-scoped database session.

    Usage in route handlers via core.dependencies:
        from core.dependencies import DBSession

        @router.get("/example")
        def example(db: DBSession):
            ...
    """
    db = _get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Returns True if the database is reachable. Used by the health route."""
    try:
        with _get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
