"""
Pricing engine unit tests.

All tests are pure — no database, no mocks required for the core logic.
Tests cover:
  - Initial price formula (position + strength + SC)
  - Price rounding to nearest 0.5
  - Position min/max clamping
  - Weekly price delta computation (form thresholds)
  - Weighted average (form score math)
  - Position average form computation
  - Sparse data handling
"""

import pytest

from models.enums import Position
from services.pricing.constants import (
    DROP_THRESHOLD,
    PRICE_MAX,
    PRICE_MIN,
    PRICE_STEP,
    RISE_THRESHOLD,
    SC_BONUS,
    STRENGTH_BONUS,
)
from services.pricing.initial import compute_initial_price
from services.pricing.signals import compute_position_avg_form
from services.pricing.utils import clamp_price, round_to_half, weighted_average
from services.pricing.weekly import compute_price_delta


# ---------------------------------------------------------------------------
# Rounding
# ---------------------------------------------------------------------------

class TestRoundToHalf:
    def test_already_on_half(self):
        assert round_to_half(5.5) == 5.5

    def test_rounds_down(self):
        # 5.7 → nearest 0.5 is 5.5 (because 5.7 * 2 = 11.4 → round to 11 → 5.5)
        assert round_to_half(5.7) == 5.5

    def test_rounds_up(self):
        # 5.8 → nearest 0.5 is 6.0 (5.8 * 2 = 11.6 → round to 12 → 6.0)
        assert round_to_half(5.8) == 6.0

    def test_whole_number(self):
        assert round_to_half(6.0) == 6.0

    def test_exactly_halfway(self):
        # 5.75 * 2 = 11.5 → Python rounds to 12 (banker's rounding) → 6.0
        result = round_to_half(5.75)
        assert result in (5.5, 6.0)  # either is acceptable for halfway

    def test_zero(self):
        assert round_to_half(0.0) == 0.0


# ---------------------------------------------------------------------------
# Clamping
# ---------------------------------------------------------------------------

class TestClampPrice:
    def test_within_bounds_unchanged(self):
        assert clamp_price(5.5, Position.MID) == 5.5

    def test_clamps_to_min(self):
        # Price of 2.0 for a GK should clamp to GK min (3.5)
        assert clamp_price(2.0, Position.GK) == PRICE_MIN[Position.GK]

    def test_clamps_to_max(self):
        # Price of 20.0 for a FWD should clamp to FWD max (12.0)
        assert clamp_price(20.0, Position.FWD) == PRICE_MAX[Position.FWD]

    def test_clamp_min_is_correct_per_position(self):
        assert clamp_price(1.0, Position.GK) == 3.5
        assert clamp_price(1.0, Position.DEF) == 3.5
        assert clamp_price(1.0, Position.MID) == 4.0
        assert clamp_price(1.0, Position.FWD) == 4.5

    def test_clamp_max_is_correct_per_position(self):
        assert clamp_price(99.0, Position.GK) == 6.5
        assert clamp_price(99.0, Position.DEF) == 8.0
        assert clamp_price(99.0, Position.MID) == 11.0
        assert clamp_price(99.0, Position.FWD) == 12.0

    def test_result_is_not_rounded(self):
        # clamp_price does NOT round — rounding happens in initial.py explicitly
        result = clamp_price(5.73, Position.MID)
        assert result == pytest.approx(5.73)


# ---------------------------------------------------------------------------
# Initial price formula
# ---------------------------------------------------------------------------

class TestComputeInitialPrice:
    def test_neutral_player_is_position_base(self):
        # strength=3 (bonus=0), SC=3 (bonus=0) → base price only
        assert compute_initial_price(Position.GK, 3) == 4.5
        assert compute_initial_price(Position.DEF, 3) == 4.5
        assert compute_initial_price(Position.MID, 3) == 5.5
        assert compute_initial_price(Position.FWD, 3) == 6.0

    def test_strength_5_premium_mid(self):
        # MID: base=5.5 + strength_5=+2.5 + SC3=0 = 8.0
        assert compute_initial_price(Position.MID, 5) == 8.0

    def test_strength_1_budget_fwd(self):
        # FWD: base=6.0 + strength_1=-1.0 + SC3=0 = 5.0
        assert compute_initial_price(Position.FWD, 1) == 5.0

    def test_star_player_premium_fwd(self):
        # FWD: base=6.0 + strength_5=+2.5 + SC5=+1.5 = 10.0
        assert compute_initial_price(Position.FWD, 5, starter_confidence=5) == 10.0

    def test_fringe_player_strength_1_gk(self):
        # GK: base=4.5 + strength_1=-1.0 + SC1=-1.0 = 2.5 → clamped to 3.5
        assert compute_initial_price(Position.GK, 1, starter_confidence=1) == 3.5

    def test_result_always_rounds_to_half(self):
        for pos in Position:
            for strength in range(1, 6):
                price = compute_initial_price(pos, strength)
                assert price * 2 == int(price * 2), f"Price {price} not on 0.5 boundary"

    def test_result_always_within_bounds(self):
        for pos in Position:
            for strength in range(1, 6):
                for sc in range(1, 6):
                    price = compute_initial_price(pos, strength, starter_confidence=sc)
                    assert PRICE_MIN[pos] <= price <= PRICE_MAX[pos], (
                        f"{pos.value} strength={strength} SC={sc} gave price={price} out of range"
                    )

    def test_higher_strength_means_higher_price(self):
        # Holding position and SC constant, higher strength → higher price
        prices = [compute_initial_price(Position.MID, s) for s in range(1, 6)]
        assert prices == sorted(prices)

    def test_higher_sc_means_higher_price(self):
        prices = [compute_initial_price(Position.FWD, 3, starter_confidence=sc) for sc in range(1, 6)]
        assert prices == sorted(prices)


# ---------------------------------------------------------------------------
# Weighted average (form score math)
# ---------------------------------------------------------------------------

class TestWeightedAverage:
    def test_equal_weights(self):
        result = weighted_average([4.0, 4.0, 4.0], [1, 1, 1])
        assert result == pytest.approx(4.0)

    def test_recent_points_weighted_higher(self):
        # High recent score with high weight should pull average up
        result = weighted_average([10.0, 2.0, 2.0], [5, 4, 3])
        assert result > 4.5  # simple average would be ~4.67

    def test_single_value(self):
        assert weighted_average([7.0], [5]) == pytest.approx(7.0)

    def test_empty_returns_zero(self):
        assert weighted_average([], []) == 0.0

    def test_form_weights_add_up(self):
        from services.pricing.constants import FORM_WEIGHTS
        # Weights [5, 4, 3, 2, 1] sum to 15
        assert sum(FORM_WEIGHTS) == 15


# ---------------------------------------------------------------------------
# Position average form
# ---------------------------------------------------------------------------

class TestComputePositionAvgForm:
    def test_single_position(self):
        form_map = {1: 5.0, 2: 3.0, 3: 4.0}
        pos_map = {1: "MID", 2: "MID", 3: "MID"}
        result = compute_position_avg_form(form_map, pos_map)
        assert result["MID"] == pytest.approx(4.0)

    def test_multiple_positions(self):
        form_map = {1: 6.0, 2: 3.0, 3: 4.0, 4: 2.0}
        pos_map = {1: "FWD", 2: "FWD", 3: "MID", 4: "DEF"}
        result = compute_position_avg_form(form_map, pos_map)
        assert result["FWD"] == pytest.approx(4.5)
        assert result["MID"] == pytest.approx(4.0)
        assert result["DEF"] == pytest.approx(2.0)

    def test_empty_returns_empty(self):
        result = compute_position_avg_form({}, {})
        assert result == {}

    def test_missing_position_skipped(self):
        form_map = {1: 5.0}
        pos_map = {}  # player 1 has no position — should be skipped
        result = compute_position_avg_form(form_map, pos_map)
        assert result == {}


# ---------------------------------------------------------------------------
# Weekly price delta
# ---------------------------------------------------------------------------

class TestComputePriceDelta:
    def test_high_form_raises_price(self):
        # form_delta well above RISE_THRESHOLD
        delta = compute_price_delta(RISE_THRESHOLD + 1.0, 6.0, Position.MID)
        assert delta == pytest.approx(PRICE_STEP)

    def test_exactly_at_rise_threshold(self):
        delta = compute_price_delta(RISE_THRESHOLD, 6.0, Position.MID)
        assert delta == pytest.approx(PRICE_STEP)

    def test_low_form_drops_price(self):
        delta = compute_price_delta(DROP_THRESHOLD - 1.0, 6.0, Position.MID)
        assert delta == pytest.approx(-PRICE_STEP)

    def test_exactly_at_drop_threshold(self):
        delta = compute_price_delta(DROP_THRESHOLD, 6.0, Position.MID)
        assert delta == pytest.approx(-PRICE_STEP)

    def test_within_thresholds_no_change(self):
        delta = compute_price_delta(0.5, 6.0, Position.MID)
        assert delta == 0.0

        delta = compute_price_delta(-0.5, 6.0, Position.MID)
        assert delta == 0.0

    def test_rise_capped_at_position_max(self):
        # Player already at max price — delta should be 0
        max_price = PRICE_MAX[Position.MID]
        delta = compute_price_delta(RISE_THRESHOLD + 5.0, max_price, Position.MID)
        # clamp_price(max_price + 0.1) = max_price → net delta = 0
        assert delta == pytest.approx(0.0)

    def test_drop_capped_at_position_min(self):
        min_price = PRICE_MIN[Position.DEF]
        delta = compute_price_delta(DROP_THRESHOLD - 5.0, min_price, Position.DEF)
        assert delta == pytest.approx(0.0)

    def test_zero_form_delta_no_change(self):
        delta = compute_price_delta(0.0, 5.5, Position.GK)
        assert delta == 0.0


# ---------------------------------------------------------------------------
# Sparse data edge cases
# ---------------------------------------------------------------------------

class TestSparseDataBehavior:
    def test_weighted_average_fewer_values_than_weights(self):
        # Player only had 2 recent games — still works, just uses first 2 weights
        from services.pricing.constants import FORM_WEIGHTS
        result = weighted_average([8.0, 5.0], FORM_WEIGHTS)
        # zip stops at shorter list (2 values, 2 weights)
        expected = (8.0 * 5 + 5.0 * 4) / (5 + 4)
        assert result == pytest.approx(expected)

    def test_all_zero_form_no_delta(self):
        # Before scoring job runs, all form_scores = 0.0
        # form_delta = 0 - 0 = 0, within thresholds → no price change
        delta = compute_price_delta(0.0, 5.5, Position.MID)
        assert delta == 0.0

    def test_position_avg_with_zeros_produces_zero_avg(self):
        # If all players have form_score=0, avg=0, delta=0 for everyone → stable
        form_map = {1: 0.0, 2: 0.0, 3: 0.0}
        pos_map = {1: "MID", 2: "MID", 3: "MID"}
        avg = compute_position_avg_form(form_map, pos_map)
        assert avg["MID"] == 0.0
        delta = compute_price_delta(0.0 - 0.0, 5.5, Position.MID)
        assert delta == 0.0
