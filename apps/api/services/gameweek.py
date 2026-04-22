"""
Top5 Fantasy gameweek service.

A gameweek covers a 7-day window: Friday 06:00 UTC through Thursday 23:59:59 UTC.
This window captures the main weekend round (Fri/Sat/Sun) plus any midweek fixtures
(Mon–Thu) as a single fantasy unit — one lock, one captain choice, one scoring window.

Lock deadline = earliest fixture kickoff in the GW minus 60 minutes.
Before fixtures are assigned, deadline defaults to the window open minus 60 minutes.

Status lifecycle:
    UPCOMING  → LOCKED   when now >= deadline_at
    LOCKED    → ACTIVE   when now >= start_at (first fixture kicks off)
    ACTIVE    → SCORING  when now >= end_at + 3h (all matches should be done)
    SCORING   → FINISHED set by the scoring job (Step X — not built yet)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import FixtureStatus, GameweekStatus
from models.fixture import Fixture
from models.gameweek import Gameweek
from models.season import Season

UTC = timezone.utc
LOCK_BUFFER = timedelta(hours=1)       # deadline = earliest kickoff - this
SCORING_BUFFER = timedelta(hours=3)    # transition to SCORING this long after end_at
GW_WINDOW_DAYS = 7                     # each GW is exactly one calendar week
GW_START_HOUR = 6                      # windows open Friday at 06:00 UTC
GW_START_WEEKDAY = 4                   # Friday (Mon=0 … Sun=6)


# ---------------------------------------------------------------------------
# Season helpers
# ---------------------------------------------------------------------------

def get_active_season(db: Session) -> Optional[Season]:
    return db.execute(
        select(Season).where(Season.is_active.is_(True))
    ).scalar_one_or_none()


# ---------------------------------------------------------------------------
# Gameweek queries
# ---------------------------------------------------------------------------

def get_gameweek_by_id(db: Session, gw_id: int) -> Optional[Gameweek]:
    return db.get(Gameweek, gw_id)


def get_current_gameweek(db: Session, season_id: int) -> Optional[Gameweek]:
    """Returns the single GW flagged is_current=True for this season."""
    return db.execute(
        select(Gameweek).where(
            Gameweek.season_id == season_id,
            Gameweek.is_current.is_(True),
        )
    ).scalar_one_or_none()


def list_gameweeks(db: Session, season_id: int) -> list[Gameweek]:
    return list(
        db.execute(
            select(Gameweek)
            .where(Gameweek.season_id == season_id)
            .order_by(Gameweek.number)
        ).scalars()
    )


def get_gameweek_fixtures(db: Session, gw_id: int) -> list[Fixture]:
    return list(
        db.execute(
            select(Fixture)
            .where(Fixture.gameweek_id == gw_id)
            .order_by(Fixture.kickoff_at)
        ).scalars()
    )


# ---------------------------------------------------------------------------
# Window math — pure functions, no DB access, easy to unit-test
# ---------------------------------------------------------------------------

def compute_deadline(reference: datetime) -> datetime:
    """Lock deadline = reference time minus LOCK_BUFFER (default 1 hour)."""
    return reference - LOCK_BUFFER


def first_friday_on_or_before(dt: datetime) -> datetime:
    """
    Return the Friday at GW_START_HOUR UTC on or before dt.
    If dt is already a Friday at or after 06:00 UTC, returns dt's Friday.
    If dt is a Friday before 06:00 UTC, rolls back one week.
    """
    dt_utc = dt.astimezone(UTC).replace(
        hour=GW_START_HOUR, minute=0, second=0, microsecond=0
    )
    days_back = (dt_utc.weekday() - GW_START_WEEKDAY) % GW_WINDOW_DAYS
    return dt_utc - timedelta(days=days_back)


def generate_weekly_windows(
    season_start: datetime,
    num_weeks: int,
) -> list[tuple[datetime, datetime]]:
    """
    Returns num_weeks (window_start, window_end) tuples in UTC.

    Each window: Friday 06:00 UTC → Thursday 23:59:59 UTC (exactly 7 days).
    First window starts on the Friday on or before season_start.
    """
    anchor = first_friday_on_or_before(season_start)
    windows: list[tuple[datetime, datetime]] = []
    for i in range(num_weeks):
        w_start = anchor + timedelta(weeks=i)
        # Thu = Fri + 6 days; 06:00 + 17h59m59s = 23:59:59
        w_end = w_start + timedelta(days=6, hours=17, minutes=59, seconds=59)
        windows.append((w_start, w_end))
    return windows


def find_gw_for_kickoff(
    kickoff_at: datetime,
    gw_windows: list[tuple[int, datetime, datetime]],
) -> Optional[int]:
    """
    Returns the GW id whose window contains kickoff_at, or None.
    gw_windows: list of (gw_id, start_at, end_at) in UTC.
    """
    ko = kickoff_at.astimezone(UTC)
    for gw_id, start, end in gw_windows:
        if start <= ko <= end:
            return gw_id
    return None


# ---------------------------------------------------------------------------
# Gameweek creation
# ---------------------------------------------------------------------------

def create_gameweek(
    db: Session,
    *,
    season_id: int,
    number: int,
    start_at: datetime,
    end_at: datetime,
) -> Gameweek:
    """
    Insert a single gameweek. Idempotent — if season+number already exists,
    returns the existing row unchanged.
    """
    existing = db.execute(
        select(Gameweek).where(
            Gameweek.season_id == season_id,
            Gameweek.number == number,
        )
    ).scalar_one_or_none()

    if existing:
        return existing

    gw = Gameweek(
        season_id=season_id,
        number=number,
        name=f"Gameweek {number}",
        start_at=start_at,
        end_at=end_at,
        deadline_at=compute_deadline(start_at),
        status=GameweekStatus.UPCOMING,
        is_current=False,
    )
    db.add(gw)
    db.commit()
    db.refresh(gw)
    return gw


def generate_gameweeks_for_season(
    db: Session,
    *,
    season_id: int,
    season_start: datetime,
    num_weeks: int,
) -> list[Gameweek]:
    """
    Generate num_weeks gameweeks for a season starting from the Friday on or
    before season_start. Existing GWs are returned unchanged (idempotent).

    Typical use: run once at the start of a season, or rerun safely if needed.
    """
    windows = generate_weekly_windows(season_start, num_weeks)
    result: list[Gameweek] = []
    for i, (w_start, w_end) in enumerate(windows, start=1):
        gw = create_gameweek(
            db,
            season_id=season_id,
            number=i,
            start_at=w_start,
            end_at=w_end,
        )
        result.append(gw)
    return result


# ---------------------------------------------------------------------------
# Fixture assignment
# ---------------------------------------------------------------------------

def assign_fixtures_to_gameweeks(db: Session, season_id: int) -> int:
    """
    Assign (or reassign) fixtures to gameweeks by matching kickoff_at to GW windows.

    Rules:
    - Fixtures without a kickoff_at are skipped (stays unassigned)
    - POSTPONED and CANCELLED fixtures are cleared to gameweek_id=None
    - A fixture maps to the GW whose window contains its kickoff_at
    - Fixtures with no matching window get gameweek_id=None (out-of-season)
    - Safe to rerun: handles reschedules automatically

    Returns count of fixtures that now have a gameweek assigned.
    """
    gws = list_gameweeks(db, season_id)
    if not gws:
        return 0

    gw_windows = [(gw.id, gw.start_at.astimezone(UTC), gw.end_at.astimezone(UTC)) for gw in gws]

    # Load all fixtures; GW window date ranges implicitly scope to this season
    fixtures = list(
        db.execute(select(Fixture).where(Fixture.kickoff_at.is_not(None))).scalars()
    )

    assigned = 0
    for fixture in fixtures:
        # Clear postponed/cancelled fixtures from any GW
        if fixture.status in (FixtureStatus.POSTPONED, FixtureStatus.CANCELLED):
            fixture.gameweek_id = None
            continue

        new_gw_id = find_gw_for_kickoff(fixture.kickoff_at, gw_windows)
        fixture.gameweek_id = new_gw_id
        if new_gw_id is not None:
            assigned += 1

    # Update each GW's deadline to reflect the earliest actual kickoff
    _refresh_gw_deadlines(db, gws)

    db.commit()
    return assigned


def _refresh_gw_deadlines(db: Session, gws: list[Gameweek]) -> None:
    """
    Set each GW's deadline_at = earliest fixture kickoff in that GW minus LOCK_BUFFER.
    Falls back to window start_at minus LOCK_BUFFER if no fixtures are assigned yet.
    """
    for gw in gws:
        earliest: Optional[datetime] = db.execute(
            select(Fixture.kickoff_at)
            .where(Fixture.gameweek_id == gw.id)
            .order_by(Fixture.kickoff_at)
            .limit(1)
        ).scalar_one_or_none()

        new_deadline = compute_deadline(earliest if earliest else gw.start_at)
        if gw.deadline_at != new_deadline:
            gw.deadline_at = new_deadline


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

def compute_gw_status(gw: Gameweek, now: datetime) -> GameweekStatus:
    """
    Pure function: return the correct status for gw at a given time.
    Does not write to DB — easy to unit-test.

    FINISHED and SCORING are sticky: FINISHED never moves, SCORING only
    advances to FINISHED via the scoring job (not here).
    """
    if gw.status == GameweekStatus.FINISHED:
        return GameweekStatus.FINISHED

    if gw.status == GameweekStatus.SCORING:
        return GameweekStatus.SCORING

    now_utc = now.astimezone(UTC)

    if now_utc >= gw.end_at.astimezone(UTC) + SCORING_BUFFER:
        return GameweekStatus.SCORING

    if now_utc >= gw.start_at.astimezone(UTC):
        return GameweekStatus.ACTIVE

    if now_utc >= gw.deadline_at.astimezone(UTC):
        return GameweekStatus.LOCKED

    return GameweekStatus.UPCOMING


def refresh_gameweek_statuses(
    db: Session,
    season_id: int,
    now_utc: Optional[datetime] = None,
) -> list[Gameweek]:
    """
    Advance gameweek statuses based on current UTC time. Updates is_current flag.
    Returns the list of GWs whose status changed.

    Run this periodically (e.g. hourly via cron) or manually via the CLI script.
    """
    if now_utc is None:
        now_utc = datetime.now(UTC)

    gws = list_gameweeks(db, season_id)
    changed: list[Gameweek] = []

    for gw in gws:
        new_status = compute_gw_status(gw, now_utc)
        if new_status != gw.status:
            gw.status = new_status
            changed.append(gw)

    _set_current_gameweek(gws)
    db.commit()
    return changed


def _set_current_gameweek(gws: list[Gameweek]) -> None:
    """
    Mark exactly one GW as is_current=True.

    Priority order:
    1. An ACTIVE gameweek (matches are happening right now)
    2. A LOCKED gameweek (deadline passed, waiting for kickoff)
    3. The lowest-numbered UPCOMING gameweek (between GWs, looking ahead)

    All others get is_current=False.
    """
    target: Optional[Gameweek] = None

    # Prefer ACTIVE first, then LOCKED
    for gw in sorted(gws, key=lambda g: g.number):
        if gw.status == GameweekStatus.ACTIVE:
            target = gw
            break

    if target is None:
        for gw in sorted(gws, key=lambda g: g.number):
            if gw.status == GameweekStatus.LOCKED:
                target = gw
                break

    if target is None:
        for gw in sorted(gws, key=lambda g: g.number):
            if gw.status == GameweekStatus.UPCOMING:
                target = gw
                break

    for gw in gws:
        gw.is_current = target is not None and gw.id == target.id
