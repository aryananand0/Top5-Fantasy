"""
Lineup validation unit tests — pure, no database.

Tests exercise validate_captain_selection() directly.
"""

import pytest

from services.lineups.validation import LineupError, validate_captain_selection


PLAYER_IDS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}


class TestValidateCaptainSelection:
    def test_valid_selection(self):
        errors = validate_captain_selection(1, 2, PLAYER_IDS)
        assert errors == []

    def test_same_player_rejected(self):
        errors = validate_captain_selection(5, 5, PLAYER_IDS)
        assert len(errors) == 1
        assert errors[0].code == "same_player"

    def test_captain_not_in_lineup(self):
        errors = validate_captain_selection(99, 2, PLAYER_IDS)
        codes = [e.code for e in errors]
        assert "captain_not_in_lineup" in codes

    def test_vc_not_in_lineup(self):
        errors = validate_captain_selection(1, 99, PLAYER_IDS)
        codes = [e.code for e in errors]
        assert "vc_not_in_lineup" in codes

    def test_both_not_in_lineup(self):
        errors = validate_captain_selection(98, 99, PLAYER_IDS)
        codes = {e.code for e in errors}
        assert "captain_not_in_lineup" in codes
        assert "vc_not_in_lineup" in codes

    def test_same_player_returns_single_error_only(self):
        # When same player, we stop early — don't also check membership
        errors = validate_captain_selection(99, 99, PLAYER_IDS)
        assert len(errors) == 1
        assert errors[0].code == "same_player"

    def test_error_is_frozen(self):
        err = LineupError(code="test", message="msg")
        with pytest.raises((AttributeError, TypeError)):
            err.code = "changed"  # type: ignore

    def test_error_str_returns_message(self):
        err = LineupError(code="test", message="Test message")
        assert str(err) == "Test message"
