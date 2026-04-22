import enum


class Position(str, enum.Enum):
    GK = "GK"
    DEF = "DEF"
    MID = "MID"
    FWD = "FWD"


class FixtureStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINISHED = "FINISHED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"


class GameweekStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    LOCKED = "LOCKED"    # After deadline, before matches start
    ACTIVE = "ACTIVE"    # Matches in progress
    SCORING = "SCORING"  # All matches done, computing points
    FINISHED = "FINISHED"


class ScoringMode(str, enum.Enum):
    RICH = "rich"        # Full event data: minutes, assists, cards, clean sheets
    FALLBACK = "fallback"  # Basic data only: goals and result


class DataQuality(str, enum.Enum):
    FULL = "full"
    PARTIAL = "partial"
    ESTIMATED = "estimated"
