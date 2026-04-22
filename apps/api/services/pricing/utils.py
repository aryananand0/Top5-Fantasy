"""
Shared pricing utility functions.

Pure math helpers — no DB access, easy to unit-test.
"""

from models.enums import Position
from services.pricing.constants import PRICE_MAX, PRICE_MIN


def round_to_half(value: float) -> float:
    """Round a price to the nearest 0.5 (e.g. 5.7 → 5.5, 5.8 → 6.0)."""
    return round(value * 2) / 2


def clamp_price(price: float, position: Position) -> float:
    """Clamp price to the allowed position range. Does NOT round."""
    lo = PRICE_MIN[position]
    hi = PRICE_MAX[position]
    return max(lo, min(hi, price))


def weighted_average(values: list[float], weights: list[int]) -> float:
    """
    Weighted average of values using weights (both lists, same length allowed to differ).
    Uses zip so shorter list determines length.
    Returns 0.0 for empty input.
    """
    pairs = list(zip(values, weights))
    if not pairs:
        return 0.0
    total_weight = sum(w for _, w in pairs)
    if total_weight == 0:
        return 0.0
    return sum(v * w for v, w in pairs) / total_weight
