"""
Squad validation — pure business rule checks.

validate_squad() is the single entry point. It takes pre-fetched ORM objects
(no DB access inside) so it:
  - is easy to unit-test without a database
  - can be reused for transfer previews (Step 13) without change
  - stays deterministic and independent of request state

Call order in the service:
  1. validate_player_ids(player_ids)   — fast, pre-DB checks
  2. fetch players + teams from DB
  3. validate_squad(players, teams)    — business rules

Any non-empty errors list → reject the request.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Protocol

from services.squads.constants import (
    BUDGET_CAP,
    MAX_PER_CLUB,
    POSITION_REQUIREMENTS,
    SQUAD_SIZE,
)


# ---------------------------------------------------------------------------
# Protocols — let validation work with any object that has the right attrs,
# without importing ORM models (avoids circular imports, easier to test).
# ---------------------------------------------------------------------------

class PlayerLike(Protocol):
    id: int
    position: object          # models.enums.Position
    team_id: int
    current_price: float
    is_available: bool
    name: str


class TeamLike(Protocol):
    id: int
    name: str


# ---------------------------------------------------------------------------
# Error type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SquadError:
    code: str
    message: str

    def __str__(self) -> str:
        return self.message


# ---------------------------------------------------------------------------
# Pre-DB checks (on raw player_ids before any DB fetch)
# ---------------------------------------------------------------------------

def validate_player_ids(player_ids: list[int]) -> list[SquadError]:
    """
    Cheap checks on the submitted list of player IDs before any DB queries.
    Returns early errors that save a round trip.
    """
    errors: list[SquadError] = []

    if len(player_ids) != SQUAD_SIZE:
        errors.append(SquadError(
            "wrong_squad_size",
            f"A squad must contain exactly {SQUAD_SIZE} players "
            f"(you submitted {len(player_ids)}).",
        ))

    if len(player_ids) != len(set(player_ids)):
        errors.append(SquadError(
            "duplicate_players",
            "Duplicate player IDs in the submission.",
        ))

    return errors


# ---------------------------------------------------------------------------
# Full business rule validation (post DB fetch)
# ---------------------------------------------------------------------------

def validate_squad(
    players: list[PlayerLike],
    teams: dict[int, TeamLike],
) -> list[SquadError]:
    """
    Validate a proposed squad against all business rules.

    Parameters:
        players:  the Player ORM objects (or compatible) for the submitted IDs
        teams:    mapping of team_id → Team (or compatible), used for club names in errors

    Returns a list of SquadErrors — empty means the squad is valid.
    """
    errors: list[SquadError] = []

    errors.extend(_check_position_requirements(players))
    errors.extend(_check_budget(players))
    errors.extend(_check_club_limit(players, teams))
    errors.extend(_check_availability(players))

    return errors


def _check_position_requirements(players: list[PlayerLike]) -> list[SquadError]:
    errors: list[SquadError] = []
    counts: Counter = Counter(p.position for p in players)

    for position, required in POSITION_REQUIREMENTS.items():
        actual = counts.get(position, 0)
        if actual != required:
            errors.append(SquadError(
                "wrong_position_count",
                f"Need exactly {required} {position.value} "
                f"(you have {actual}).",
            ))

    return errors


def _check_budget(players: list[PlayerLike]) -> list[SquadError]:
    total = round(sum(float(p.current_price) for p in players), 1)
    if total > BUDGET_CAP:
        over = round(total - BUDGET_CAP, 1)
        return [SquadError(
            "over_budget",
            f"Squad costs £{total} — £{over} over the £{BUDGET_CAP} budget.",
        )]
    return []


def _check_club_limit(
    players: list[PlayerLike],
    teams: dict[int, TeamLike],
) -> list[SquadError]:
    errors: list[SquadError] = []
    counts: Counter = Counter(p.team_id for p in players)

    for team_id, count in counts.items():
        if count > MAX_PER_CLUB:
            team_name = teams[team_id].name if team_id in teams else f"club #{team_id}"
            errors.append(SquadError(
                "club_limit_exceeded",
                f"Maximum {MAX_PER_CLUB} players per club "
                f"({team_name} has {count}).",
            ))

    return errors


def _check_availability(players: list[PlayerLike]) -> list[SquadError]:
    errors: list[SquadError] = []
    for p in players:
        if not p.is_available:
            errors.append(SquadError(
                "player_unavailable",
                f"{p.name} is currently unavailable for selection.",
            ))
    return errors
