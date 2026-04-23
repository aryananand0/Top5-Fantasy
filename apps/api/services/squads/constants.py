"""
Top5 Fantasy squad rules.

All squad composition rules live here as constants so they can be referenced
by validation, UI copy, and tests from a single source of truth.

These can be promoted to DB-backed config later if multi-season rule changes
are needed, but constants are the right level for MVP.
"""

from models.enums import Position

# Total fantasy credits available to build a squad
BUDGET_CAP: float = 100.0

# Fixed squad size for MVP (no bench)
SQUAD_SIZE: int = 11

# Maximum players from the same real-world club
MAX_PER_CLUB: int = 2

# Required number of players per position — must sum to SQUAD_SIZE
POSITION_REQUIREMENTS: dict[Position, int] = {
    Position.GK:  1,
    Position.DEF: 3,
    Position.MID: 4,
    Position.FWD: 3,
}

assert sum(POSITION_REQUIREMENTS.values()) == SQUAD_SIZE, (
    "POSITION_REQUIREMENTS must sum to SQUAD_SIZE"
)

# Free transfers banked at squad creation (the initial pick is free,
# then users accumulate 2 per GW up to a max of 3 banked)
INITIAL_FREE_TRANSFERS: int = 1
MAX_FREE_TRANSFERS_BANKED: int = 3
