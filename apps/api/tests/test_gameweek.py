"""
Gameweek service unit tests.

All tests are pure — no database, no mocks. They exercise the service
functions that contain logic: window math, fixture assignment, and status
transitions.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from models.enums import GameweekStatus
from services.gameweek import (
    LOCK_BUFFER,
    SCORING_BUFFER,
    compute_deadline,
    compute_gw_status,
    find_gw_for_kickoff,
    first_friday_on_or_before,
    generate_weekly_windows,
    _set_current_gameweek,
)

UTC = timezone.utc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_gw(
    *,
    gw_id: int = 1,
    number: int = 1,
    status: GameweekStatus = GameweekStatus.UPCOMING,
    is_current: bool = False,
    deadline_offset_hours: int = -1,   # relative to start_at
    start_offset_hours: int = 0,       # relative to anchor
    end_offset_hours: int = 167,       # +167h = end of week window
    anchor: datetime | None = None,
) -> MagicMock:
    """Build a lightweight MagicMock shaped like a Gameweek ORM object."""
    anchor = anchor or datetime(2025, 8, 15, 6, 0, 0, tzinfo=UTC)  # a Friday
    start_at = anchor + timedelta(hours=start_offset_hours)
    end_at = anchor + timedelta(hours=end_offset_hours)
    deadline_at = start_at + timedelta(hours=deadline_offset_hours)

    gw = MagicMock()
    gw.id = gw_id
    gw.number = number
    gw.status = status
    gw.is_current = is_current
    gw.start_at = start_at
    gw.end_at = end_at
    gw.deadline_at = deadline_at
    return gw


# ---------------------------------------------------------------------------
# Window math
# ---------------------------------------------------------------------------

class TestFirstFridayOnOrBefore:
    def test_input_is_friday(self):
        # Friday Aug 15 2025
        dt = datetime(2025, 8, 15, 12, 0, tzinfo=UTC)
        result = first_friday_on_or_before(dt)
        assert result.weekday() == 4  # Friday
        assert result.date() == dt.date()
        assert result.hour == 6
        assert result.minute == 0

    def test_input_is_saturday(self):
        dt = datetime(2025, 8, 16, 12, 0, tzinfo=UTC)  # Saturday
        result = first_friday_on_or_before(dt)
        assert result.weekday() == 4
        assert result.day == 15  # back to Friday the 15th

    def test_input_is_monday(self):
        dt = datetime(2025, 8, 18, 12, 0, tzinfo=UTC)  # Monday
        result = first_friday_on_or_before(dt)
        assert result.weekday() == 4
        assert result.day == 15  # back to Friday the 15th

    def test_input_is_thursday(self):
        dt = datetime(2025, 8, 21, 12, 0, tzinfo=UTC)  # Thursday
        result = first_friday_on_or_before(dt)
        assert result.weekday() == 4
        assert result.day == 15  # previous Friday

    def test_always_at_06_utc(self):
        for day_offset in range(7):
            dt = datetime(2025, 8, 15, tzinfo=UTC) + timedelta(days=day_offset)
            result = first_friday_on_or_before(dt)
            assert result.hour == 6
            assert result.minute == 0
            assert result.second == 0


class TestGenerateWeeklyWindows:
    def test_produces_correct_count(self):
        start = datetime(2025, 8, 15, tzinfo=UTC)
        windows = generate_weekly_windows(start, num_weeks=5)
        assert len(windows) == 5

    def test_first_window_starts_on_friday(self):
        start = datetime(2025, 8, 15, tzinfo=UTC)  # already a Friday
        windows = generate_weekly_windows(start, num_weeks=1)
        w_start, _ = windows[0]
        assert w_start.weekday() == 4  # Friday
        assert w_start.hour == 6

    def test_window_end_is_thursday(self):
        start = datetime(2025, 8, 15, tzinfo=UTC)
        windows = generate_weekly_windows(start, num_weeks=1)
        _, w_end = windows[0]
        assert w_end.weekday() == 3  # Thursday
        assert w_end.hour == 23
        assert w_end.minute == 59
        assert w_end.second == 59

    def test_windows_do_not_overlap(self):
        start = datetime(2025, 8, 15, tzinfo=UTC)
        windows = generate_weekly_windows(start, num_weeks=4)
        for i in range(len(windows) - 1):
            this_end = windows[i][1]
            next_start = windows[i + 1][0]
            # Next window must start strictly after the current one ends
            assert next_start > this_end

    def test_each_window_is_seven_days(self):
        start = datetime(2025, 8, 15, tzinfo=UTC)
        windows = generate_weekly_windows(start, num_weeks=4)
        for w_start, w_end in windows:
            duration = w_end - w_start
            # Fri 06:00 → Thu 23:59:59 = 6d 17h 59m 59s = 6*86400 + 17*3600 + 59*60 + 59 seconds
            expected = timedelta(days=6, hours=17, minutes=59, seconds=59)
            assert duration == expected

    def test_first_window_contains_season_start_even_if_midweek(self):
        # Season starts on a Wednesday — first window should be the preceding Friday
        start = datetime(2025, 8, 20, tzinfo=UTC)  # Wednesday
        windows = generate_weekly_windows(start, num_weeks=1)
        w_start, w_end = windows[0]
        assert w_start.weekday() == 4  # Friday Aug 15
        assert w_start.day == 15


class TestComputeDeadline:
    def test_deadline_is_one_hour_before(self):
        ref = datetime(2025, 8, 15, 14, 0, 0, tzinfo=UTC)
        deadline = compute_deadline(ref)
        assert deadline == ref - LOCK_BUFFER
        assert deadline.hour == 13

    def test_lock_buffer_constant(self):
        assert LOCK_BUFFER == timedelta(hours=1)


# ---------------------------------------------------------------------------
# Fixture assignment
# ---------------------------------------------------------------------------

class TestFindGwForKickoff:
    def _make_windows(self):
        # GW1: Fri Aug 15 06:00 → Thu Aug 21 23:59:59 UTC
        # GW2: Fri Aug 22 06:00 → Thu Aug 28 23:59:59 UTC
        start1 = datetime(2025, 8, 15, 6, 0, 0, tzinfo=UTC)
        end1   = datetime(2025, 8, 21, 23, 59, 59, tzinfo=UTC)
        start2 = datetime(2025, 8, 22, 6, 0, 0, tzinfo=UTC)
        end2   = datetime(2025, 8, 28, 23, 59, 59, tzinfo=UTC)
        return [(1, start1, end1), (2, start2, end2)]

    def test_saturday_kickoff_maps_to_gw1(self):
        windows = self._make_windows()
        ko = datetime(2025, 8, 16, 15, 0, 0, tzinfo=UTC)  # Saturday 3pm
        assert find_gw_for_kickoff(ko, windows) == 1

    def test_tuesday_kickoff_maps_to_gw1(self):
        windows = self._make_windows()
        ko = datetime(2025, 8, 19, 20, 0, 0, tzinfo=UTC)  # Tuesday 8pm
        assert find_gw_for_kickoff(ko, windows) == 1

    def test_next_friday_kickoff_maps_to_gw2(self):
        windows = self._make_windows()
        ko = datetime(2025, 8, 22, 20, 0, 0, tzinfo=UTC)  # Next Friday
        assert find_gw_for_kickoff(ko, windows) == 2

    def test_before_any_window_returns_none(self):
        windows = self._make_windows()
        ko = datetime(2025, 8, 1, 15, 0, 0, tzinfo=UTC)  # Way before GW1
        assert find_gw_for_kickoff(ko, windows) is None

    def test_after_all_windows_returns_none(self):
        windows = self._make_windows()
        ko = datetime(2025, 9, 1, 15, 0, 0, tzinfo=UTC)  # After GW2
        assert find_gw_for_kickoff(ko, windows) is None

    def test_exact_window_start_matches(self):
        windows = self._make_windows()
        ko = datetime(2025, 8, 15, 6, 0, 0, tzinfo=UTC)  # exact start
        assert find_gw_for_kickoff(ko, windows) == 1

    def test_exact_window_end_matches(self):
        windows = self._make_windows()
        ko = datetime(2025, 8, 21, 23, 59, 59, tzinfo=UTC)  # exact end
        assert find_gw_for_kickoff(ko, windows) == 1

    def test_empty_windows_returns_none(self):
        assert find_gw_for_kickoff(datetime(2025, 8, 16, tzinfo=UTC), []) is None


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

class TestComputeGwStatus:
    """
    Verify the pure status transition function across all boundary cases.
    anchor = Friday Aug 15 2025 06:00 UTC (start_at)
    deadline = -1h = Thu 05:00 UTC (deadline_at)
    end_at = anchor + 167h = Thu Aug 21 23:00 UTC
    """

    anchor = datetime(2025, 8, 15, 6, 0, 0, tzinfo=UTC)

    def _gw(self, status=GameweekStatus.UPCOMING):
        return make_gw(status=status, anchor=self.anchor)

    def test_before_deadline_is_upcoming(self):
        gw = self._gw()
        now = gw.deadline_at - timedelta(minutes=1)
        assert compute_gw_status(gw, now) == GameweekStatus.UPCOMING

    def test_at_deadline_transitions_to_locked(self):
        gw = self._gw()
        now = gw.deadline_at
        assert compute_gw_status(gw, now) == GameweekStatus.LOCKED

    def test_between_deadline_and_start_is_locked(self):
        gw = self._gw()
        now = gw.deadline_at + timedelta(minutes=30)
        assert compute_gw_status(gw, now) == GameweekStatus.LOCKED

    def test_at_start_transitions_to_active(self):
        gw = self._gw()
        now = gw.start_at
        assert compute_gw_status(gw, now) == GameweekStatus.ACTIVE

    def test_during_window_is_active(self):
        gw = self._gw()
        now = gw.start_at + timedelta(days=3)
        assert compute_gw_status(gw, now) == GameweekStatus.ACTIVE

    def test_past_end_plus_buffer_is_scoring(self):
        gw = self._gw()
        now = gw.end_at + SCORING_BUFFER
        assert compute_gw_status(gw, now) == GameweekStatus.SCORING

    def test_finished_is_sticky(self):
        gw = self._gw(status=GameweekStatus.FINISHED)
        now = datetime.now(UTC)
        assert compute_gw_status(gw, now) == GameweekStatus.FINISHED

    def test_scoring_is_sticky(self):
        gw = self._gw(status=GameweekStatus.SCORING)
        now = datetime.now(UTC)
        assert compute_gw_status(gw, now) == GameweekStatus.SCORING


# ---------------------------------------------------------------------------
# Current gameweek selection
# ---------------------------------------------------------------------------

class TestSetCurrentGameweek:
    def test_active_gw_becomes_current(self):
        gws = [
            make_gw(gw_id=1, number=1, status=GameweekStatus.FINISHED),
            make_gw(gw_id=2, number=2, status=GameweekStatus.ACTIVE),
            make_gw(gw_id=3, number=3, status=GameweekStatus.UPCOMING),
        ]
        _set_current_gameweek(gws)
        assert gws[0].is_current is False
        assert gws[1].is_current is True
        assert gws[2].is_current is False

    def test_locked_gw_becomes_current_if_no_active(self):
        gws = [
            make_gw(gw_id=1, number=1, status=GameweekStatus.FINISHED),
            make_gw(gw_id=2, number=2, status=GameweekStatus.LOCKED),
            make_gw(gw_id=3, number=3, status=GameweekStatus.UPCOMING),
        ]
        _set_current_gameweek(gws)
        assert gws[1].is_current is True
        assert gws[2].is_current is False

    def test_next_upcoming_gw_becomes_current_between_gws(self):
        gws = [
            make_gw(gw_id=1, number=1, status=GameweekStatus.FINISHED),
            make_gw(gw_id=2, number=2, status=GameweekStatus.FINISHED),
            make_gw(gw_id=3, number=3, status=GameweekStatus.UPCOMING),
            make_gw(gw_id=4, number=4, status=GameweekStatus.UPCOMING),
        ]
        _set_current_gameweek(gws)
        assert gws[2].is_current is True   # lowest-numbered upcoming
        assert gws[3].is_current is False

    def test_active_takes_priority_over_locked(self):
        gws = [
            make_gw(gw_id=1, number=1, status=GameweekStatus.LOCKED),
            make_gw(gw_id=2, number=2, status=GameweekStatus.ACTIVE),
        ]
        _set_current_gameweek(gws)
        assert gws[0].is_current is False
        assert gws[1].is_current is True

    def test_all_finished_no_current(self):
        gws = [
            make_gw(gw_id=1, number=1, status=GameweekStatus.FINISHED),
            make_gw(gw_id=2, number=2, status=GameweekStatus.FINISHED),
        ]
        _set_current_gameweek(gws)
        assert gws[0].is_current is False
        assert gws[1].is_current is False

    def test_exactly_one_current_with_many_gws(self):
        gws = [
            make_gw(gw_id=i, number=i, status=GameweekStatus.UPCOMING)
            for i in range(1, 10)
        ]
        _set_current_gameweek(gws)
        current_count = sum(1 for gw in gws if gw.is_current)
        assert current_count == 1
