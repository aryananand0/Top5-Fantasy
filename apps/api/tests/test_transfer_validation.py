"""
Unit tests for transfer validation pure functions.
No DB, no fixtures — just logic.
"""

import pytest

from services.transfers.validation import TransferError, compute_points_hit, validate_transfer_pairs


# ---------------------------------------------------------------------------
# validate_transfer_pairs
# ---------------------------------------------------------------------------

ACTIVE = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}


def test_valid_single_transfer():
    errors = validate_transfer_pairs([(1, 11)], ACTIVE)
    assert errors == []


def test_valid_multi_transfer():
    errors = validate_transfer_pairs([(1, 11), (2, 12), (3, 13)], ACTIVE)
    assert errors == []


def test_empty_pairs_returns_error():
    errors = validate_transfer_pairs([], ACTIVE)
    assert any(e.code == "no_transfers" for e in errors)


def test_too_many_pairs():
    pairs = [(i, i + 20) for i in range(1, 7)]  # 6 pairs > MAX_TRANSFERS_PER_REQUEST
    errors = validate_transfer_pairs(pairs, ACTIVE)
    assert any(e.code == "too_many_transfers" for e in errors)


def test_no_op_transfer_same_player():
    errors = validate_transfer_pairs([(1, 1)], ACTIVE)
    assert any(e.code == "no_op_transfer" for e in errors)


def test_duplicate_player_out():
    errors = validate_transfer_pairs([(1, 11), (1, 12)], ACTIVE)
    assert any(e.code == "duplicate_player_out" for e in errors)


def test_duplicate_player_in():
    errors = validate_transfer_pairs([(1, 11), (2, 11)], ACTIVE)
    assert any(e.code == "duplicate_player_in" for e in errors)


def test_player_out_not_in_squad():
    errors = validate_transfer_pairs([(99, 11)], ACTIVE)
    assert any(e.code == "player_out_not_in_squad" for e in errors)


def test_player_in_already_in_squad():
    # Player 5 is in ACTIVE and not being transferred out
    errors = validate_transfer_pairs([(1, 5)], ACTIVE)
    assert any(e.code == "player_already_in_squad" for e in errors)


def test_player_in_allowed_if_being_sold_in_same_batch():
    # Player 5 is sold out in first pair, so can be bought in second pair
    errors = validate_transfer_pairs([(5, 11), (1, 5)], ACTIVE)
    # player 5 is in out_ids so projected_squad excludes it → no error
    assert not any(e.code == "player_already_in_squad" for e in errors)


def test_cross_pair_conflict():
    # Player 11 is being bought in pair 0 but sold in pair 1 (and 11 is not in active squad)
    errors = validate_transfer_pairs([(1, 11), (11, 12)], ACTIVE)
    assert any(e.code == "transfer_conflict" for e in errors)


def test_multiple_errors_returned():
    # No-op AND player_out not in squad
    errors = validate_transfer_pairs([(99, 99)], ACTIVE)
    codes = {e.code for e in errors}
    assert "no_op_transfer" in codes
    assert "player_out_not_in_squad" in codes


def test_transfer_error_str():
    e = TransferError("some_code", "Some message.")
    assert str(e) == "Some message."


# ---------------------------------------------------------------------------
# compute_points_hit
# ---------------------------------------------------------------------------

def test_zero_hit_when_all_free():
    points, paid = compute_points_hit(2, 3)
    assert points == 0
    assert paid == 0


def test_hit_when_no_free_transfers():
    points, paid = compute_points_hit(2, 0)
    assert points == 8  # 2 × 4
    assert paid == 2


def test_partial_free_hit():
    # 3 transfers, 1 free → 2 paid × 4 = 8
    points, paid = compute_points_hit(3, 1)
    assert points == 8
    assert paid == 2


def test_more_free_than_transfers():
    points, paid = compute_points_hit(1, 5)
    assert points == 0
    assert paid == 0


def test_exactly_uses_all_free():
    points, paid = compute_points_hit(3, 3)
    assert points == 0
    assert paid == 0


def test_single_paid_transfer():
    points, paid = compute_points_hit(2, 1)
    assert points == 4
    assert paid == 1
