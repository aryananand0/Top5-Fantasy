"""
Lineup validation — pure functions, no DB access.

Keeps the same pattern as services/squads/validation.py:
reusable, testable without fixtures, no side effects.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LineupError:
    code: str
    message: str

    def __str__(self) -> str:
        return self.message


def validate_captain_selection(
    captain_player_id: int,
    vice_captain_player_id: int,
    lineup_player_ids: set[int],
) -> list[LineupError]:
    """
    Validate captain and vice-captain IDs against the set of players in the lineup.

    Rules:
    - Both must be in the lineup
    - They must be different players
    """
    errors: list[LineupError] = []

    if captain_player_id == vice_captain_player_id:
        errors.append(LineupError(
            "same_player",
            "Captain and vice-captain must be different players.",
        ))
        # No point checking further if they're the same
        return errors

    if captain_player_id not in lineup_player_ids:
        errors.append(LineupError(
            "captain_not_in_lineup",
            "Captain must be one of your 11 lineup players.",
        ))

    if vice_captain_player_id not in lineup_player_ids:
        errors.append(LineupError(
            "vc_not_in_lineup",
            "Vice-captain must be one of your 11 lineup players.",
        ))

    return errors
