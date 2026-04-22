"""
Smoke tests for ingestion constants.

These check that the static data is internally consistent — useful as a guard
against accidental typos when someone edits constants.py.
"""

import pytest

from models.enums import FixtureStatus, Position
from services.ingestion.constants import (
    DEFAULT_PRICES,
    FIXTURE_STATUS_MAP,
    POSITION_MAP,
    SUPPORTED_COMPETITIONS,
)


class TestSupportedCompetitions:
    def test_five_competitions(self) -> None:
        assert len(SUPPORTED_COMPETITIONS) == 5

    def test_required_keys(self) -> None:
        for comp in SUPPORTED_COMPETITIONS:
            assert "code" in comp
            assert "name" in comp
            assert "country" in comp

    def test_codes_are_unique(self) -> None:
        codes = [c["code"] for c in SUPPORTED_COMPETITIONS]
        assert len(codes) == len(set(codes))

    def test_known_codes_present(self) -> None:
        codes = {c["code"] for c in SUPPORTED_COMPETITIONS}
        assert codes == {"PL", "PD", "BL1", "SA", "FL1"}


class TestPositionMap:
    def test_all_positions_covered(self) -> None:
        mapped = set(POSITION_MAP.values())
        assert mapped == set(Position)

    def test_goalkeeper_maps_correctly(self) -> None:
        assert POSITION_MAP["Goalkeeper"] == Position.GK

    def test_attacker_maps_to_fwd(self) -> None:
        assert POSITION_MAP["Attacker"] == Position.FWD


class TestFixtureStatusMap:
    def test_live_variants(self) -> None:
        assert FIXTURE_STATUS_MAP["IN_PLAY"] == FixtureStatus.LIVE
        assert FIXTURE_STATUS_MAP["PAUSED"] == FixtureStatus.LIVE

    def test_finished_variants(self) -> None:
        assert FIXTURE_STATUS_MAP["FINISHED"] == FixtureStatus.FINISHED
        assert FIXTURE_STATUS_MAP["AWARDED"] == FixtureStatus.FINISHED

    def test_timed_maps_to_scheduled(self) -> None:
        assert FIXTURE_STATUS_MAP["TIMED"] == FixtureStatus.SCHEDULED


class TestDefaultPrices:
    def test_all_positions_have_price(self) -> None:
        for pos in Position:
            assert pos in DEFAULT_PRICES
            assert DEFAULT_PRICES[pos] > 0
