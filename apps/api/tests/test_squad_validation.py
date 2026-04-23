"""
Squad validation unit tests — pure, no database.

Tests exercise validate_player_ids() and validate_squad() directly using
lightweight stub objects that satisfy the PlayerLike / TeamLike protocols.
"""

from types import SimpleNamespace

import pytest

from models.enums import Position
from services.squads.constants import (
    BUDGET_CAP,
    MAX_PER_CLUB,
    POSITION_REQUIREMENTS,
    SQUAD_SIZE,
)
from services.squads.validation import (
    SquadError,
    validate_player_ids,
    validate_squad,
)


# ---------------------------------------------------------------------------
# Stub builders
# ---------------------------------------------------------------------------

def make_player(
    pid: int,
    position: Position,
    team_id: int,
    price: float = 5.0,
    available: bool = True,
    name: str = "",
) -> SimpleNamespace:
    return SimpleNamespace(
        id=pid,
        position=position,
        team_id=team_id,
        current_price=price,
        is_available=available,
        name=name or f"Player {pid}",
    )


def make_team(team_id: int, name: str = "") -> SimpleNamespace:
    return SimpleNamespace(id=team_id, name=name or f"Team {team_id}")


def _valid_players() -> list[SimpleNamespace]:
    """
    Build a valid 11-player squad:
      1 GK  (team 1) @ £4.5  → £4.5
      3 DEF (teams 1,2,3) @ £4.5 → £13.5
      4 MID (teams 4,5,6,7) @ £5.5 → £22.0
      3 FWD (teams 8,9,10) @ £6.0 → £18.0
      Total: £4.5 + £13.5 + £22.0 + £18.0 = £58.0  (well under £100)
    """
    return [
        make_player(1,  Position.GK,  team_id=1, price=4.5),
        make_player(2,  Position.DEF, team_id=1, price=4.5),
        make_player(3,  Position.DEF, team_id=2, price=4.5),
        make_player(4,  Position.DEF, team_id=3, price=4.5),
        make_player(5,  Position.MID, team_id=4, price=5.5),
        make_player(6,  Position.MID, team_id=5, price=5.5),
        make_player(7,  Position.MID, team_id=6, price=5.5),
        make_player(8,  Position.MID, team_id=7, price=5.5),
        make_player(9,  Position.FWD, team_id=8, price=6.0),
        make_player(10, Position.FWD, team_id=9, price=6.0),
        make_player(11, Position.FWD, team_id=10, price=6.0),
    ]


def _valid_teams() -> dict[int, SimpleNamespace]:
    return {i: make_team(i) for i in range(1, 11)}


# ---------------------------------------------------------------------------
# validate_player_ids — pre-DB checks
# ---------------------------------------------------------------------------

class TestValidatePlayerIds:
    def test_valid_ids(self):
        ids = list(range(1, SQUAD_SIZE + 1))
        assert validate_player_ids(ids) == []

    def test_too_few_players(self):
        errors = validate_player_ids([1, 2, 3])
        assert any(e.code == "wrong_squad_size" for e in errors)

    def test_too_many_players(self):
        errors = validate_player_ids(list(range(1, SQUAD_SIZE + 3)))
        assert any(e.code == "wrong_squad_size" for e in errors)

    def test_duplicate_ids(self):
        ids = list(range(1, SQUAD_SIZE)) + [1]  # last ID is a duplicate of first
        errors = validate_player_ids(ids)
        assert any(e.code == "duplicate_players" for e in errors)

    def test_exact_squad_size_no_duplicates_is_valid(self):
        ids = list(range(100, 100 + SQUAD_SIZE))
        assert validate_player_ids(ids) == []


# ---------------------------------------------------------------------------
# validate_squad — business rules
# ---------------------------------------------------------------------------

class TestValidateSquadValid:
    def test_valid_squad_has_no_errors(self):
        players = _valid_players()
        teams = _valid_teams()
        errors = validate_squad(players, teams)
        assert errors == [], f"Unexpected errors: {errors}"


class TestPositionRequirements:
    def test_missing_gk(self):
        players = _valid_players()
        # Replace GK with an extra FWD
        players[0] = make_player(1, Position.FWD, team_id=1, price=4.5)
        errors = validate_squad(players, _valid_teams())
        codes = [e.code for e in errors]
        assert "wrong_position_count" in codes

    def test_extra_defender(self):
        players = _valid_players()
        # Replace one MID with a DEF → 4 DEF, 3 MID
        players[4] = make_player(5, Position.DEF, team_id=11, price=5.5)
        teams = {**_valid_teams(), 11: make_team(11)}
        errors = validate_squad(players, teams)
        codes = [e.code for e in errors]
        assert "wrong_position_count" in codes

    def test_all_wrong_positions_reports_each(self):
        # All 11 as MID — should report errors for GK, DEF, FWD (wrong count each)
        players = [make_player(i, Position.MID, team_id=i, price=5.5) for i in range(1, 12)]
        teams = {i: make_team(i) for i in range(1, 12)}
        errors = validate_squad(players, teams)
        codes = {e.code for e in errors}
        assert "wrong_position_count" in codes
        # Must flag GK, DEF, FWD short AND MID over
        assert len([e for e in errors if e.code == "wrong_position_count"]) >= 3


class TestBudget:
    def test_exactly_at_budget_is_valid(self):
        players = _valid_players()
        # Force total to exactly £100.0
        # 11 players at £100/11 ≈ £9.09 each — use round prices
        # 8 × £8.0 + 3 × £8.0 = £88 … let's just set specific prices
        # Easiest: set one player to fill budget exactly
        total_others = sum(float(p.current_price) for p in players[1:])
        players[0].current_price = round(BUDGET_CAP - total_others, 1)
        errors = validate_squad(players, _valid_teams())
        assert not any(e.code == "over_budget" for e in errors)

    def test_over_budget_rejected(self):
        players = _valid_players()
        # Inflate one player's price to exceed budget
        players[0].current_price = 99.0  # total now well over 100
        errors = validate_squad(players, _valid_teams())
        assert any(e.code == "over_budget" for e in errors)

    def test_one_penny_over_budget_rejected(self):
        players = _valid_players()
        # Set total to 100.1
        base_total = sum(float(p.current_price) for p in players)
        players[0].current_price = float(players[0].current_price) + (BUDGET_CAP - base_total) + 0.1
        errors = validate_squad(players, _valid_teams())
        assert any(e.code == "over_budget" for e in errors)


class TestClubLimit:
    def test_max_per_club_exactly_ok(self):
        players = _valid_players()
        # Two players from team 1 is the current valid setup — should pass
        assert players[0].team_id == 1
        assert players[1].team_id == 1
        errors = validate_squad(players, _valid_teams())
        assert not any(e.code == "club_limit_exceeded" for e in errors)

    def test_three_from_same_club_rejected(self):
        players = _valid_players()
        # Move a third player to team 1
        players[2].team_id = 1
        errors = validate_squad(players, _valid_teams())
        assert any(e.code == "club_limit_exceeded" for e in errors)

    def test_error_names_the_club(self):
        players = _valid_players()
        players[2].team_id = 1
        teams = _valid_teams()
        teams[1] = make_team(1, "Arsenal")
        errors = validate_squad(players, teams)
        club_errors = [e for e in errors if e.code == "club_limit_exceeded"]
        assert any("Arsenal" in e.message for e in club_errors)


class TestAvailability:
    def test_unavailable_player_rejected(self):
        players = _valid_players()
        players[0].is_available = False
        players[0].name = "Injured Player"
        errors = validate_squad(players, _valid_teams())
        assert any(e.code == "player_unavailable" for e in errors)

    def test_unavailable_player_error_names_player(self):
        players = _valid_players()
        players[3].is_available = False
        players[3].name = "Suspended Star"
        errors = validate_squad(players, _valid_teams())
        unavail = [e for e in errors if e.code == "player_unavailable"]
        assert any("Suspended Star" in e.message for e in unavail)

    def test_all_available_no_error(self):
        players = _valid_players()
        errors = validate_squad(players, _valid_teams())
        assert not any(e.code == "player_unavailable" for e in errors)


class TestMultipleErrors:
    def test_over_budget_and_wrong_positions_both_reported(self):
        # Build a squad that's both over budget and has wrong positions
        players = [make_player(i, Position.MID, team_id=i, price=12.0) for i in range(1, 12)]
        teams = {i: make_team(i) for i in range(1, 12)}
        errors = validate_squad(players, teams)
        codes = {e.code for e in errors}
        assert "over_budget" in codes
        assert "wrong_position_count" in codes

    def test_club_limit_and_unavailable_both_reported(self):
        players = _valid_players()
        players[2].team_id = 1           # 3 from team 1 → club limit
        players[4].is_available = False  # unavailable
        errors = validate_squad(players, _valid_teams())
        codes = {e.code for e in errors}
        assert "club_limit_exceeded" in codes
        assert "player_unavailable" in codes


class TestSquadErrorType:
    def test_error_has_code_and_message(self):
        err = SquadError(code="test_code", message="Test message")
        assert err.code == "test_code"
        assert err.message == "Test message"
        assert str(err) == "Test message"

    def test_error_is_frozen(self):
        err = SquadError(code="x", message="y")
        with pytest.raises((AttributeError, TypeError)):
            err.code = "changed"  # type: ignore
