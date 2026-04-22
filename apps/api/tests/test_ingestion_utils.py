"""
Unit tests for ingestion utility functions.

All tests are pure — no database required.
"""

import pytest

from models.enums import FixtureStatus, Position
from services.ingestion.utils import (
    normalize_fixture_status,
    normalize_position,
    get_default_price,
)


class TestNormalizePosition:
    def test_goalkeeper(self) -> None:
        assert normalize_position("Goalkeeper") == Position.GK

    def test_defender(self) -> None:
        assert normalize_position("Defender") == Position.DEF

    def test_midfielder(self) -> None:
        assert normalize_position("Midfielder") == Position.MID

    def test_forward(self) -> None:
        assert normalize_position("Forward") == Position.FWD

    def test_attacker_maps_to_fwd(self) -> None:
        assert normalize_position("Attacker") == Position.FWD

    def test_none_defaults_to_mid(self) -> None:
        assert normalize_position(None) == Position.MID

    def test_unknown_string_defaults_to_mid(self) -> None:
        assert normalize_position("CoachPlayer") == Position.MID

    def test_empty_string_defaults_to_mid(self) -> None:
        assert normalize_position("") == Position.MID


class TestNormalizeFixtureStatus:
    def test_scheduled(self) -> None:
        assert normalize_fixture_status("SCHEDULED") == FixtureStatus.SCHEDULED

    def test_timed_maps_to_scheduled(self) -> None:
        assert normalize_fixture_status("TIMED") == FixtureStatus.SCHEDULED

    def test_in_play_maps_to_live(self) -> None:
        assert normalize_fixture_status("IN_PLAY") == FixtureStatus.LIVE

    def test_finished(self) -> None:
        assert normalize_fixture_status("FINISHED") == FixtureStatus.FINISHED

    def test_postponed(self) -> None:
        assert normalize_fixture_status("POSTPONED") == FixtureStatus.POSTPONED

    def test_suspended_maps_to_postponed(self) -> None:
        assert normalize_fixture_status("SUSPENDED") == FixtureStatus.POSTPONED

    def test_cancelled(self) -> None:
        assert normalize_fixture_status("CANCELLED") == FixtureStatus.CANCELLED

    def test_none_defaults_to_scheduled(self) -> None:
        assert normalize_fixture_status(None) == FixtureStatus.SCHEDULED

    def test_unknown_defaults_to_scheduled(self) -> None:
        assert normalize_fixture_status("MYSTERY") == FixtureStatus.SCHEDULED


class TestGetDefaultPrice:
    def test_gk_price(self) -> None:
        assert get_default_price(Position.GK) == 4.5

    def test_def_price(self) -> None:
        assert get_default_price(Position.DEF) == 4.5

    def test_mid_price(self) -> None:
        assert get_default_price(Position.MID) == 5.0

    def test_fwd_price(self) -> None:
        assert get_default_price(Position.FWD) == 5.5
