"""
Transfer validation — pure functions, no DB access.

Pre-DB checks that catch obvious errors before touching the database.
Final squad validity is checked by reusing services/squads/validation.py.
"""

from dataclasses import dataclass

from services.transfers.constants import MAX_TRANSFERS_PER_REQUEST


@dataclass(frozen=True)
class TransferError:
    code: str
    message: str

    def __str__(self) -> str:
        return self.message


def validate_transfer_pairs(
    pairs: list[tuple[int, int]],
    active_player_ids: set[int],
) -> list[TransferError]:
    """
    Pure pre-DB validation of transfer pair inputs.

    Checks:
    - At least one pair provided
    - At most MAX_TRANSFERS_PER_REQUEST pairs
    - No no-op transfers (player_in == player_out)
    - player_out is in the active squad
    - player_in is not already in the squad
    - No duplicate player_out IDs across pairs
    - No duplicate player_in IDs across pairs
    - player_in not already leaving in another pair
    - player_out not already arriving in another pair
    """
    errors: list[TransferError] = []

    if not pairs:
        errors.append(TransferError("no_transfers", "At least one transfer pair is required."))
        return errors

    if len(pairs) > MAX_TRANSFERS_PER_REQUEST:
        errors.append(TransferError(
            "too_many_transfers",
            f"Maximum {MAX_TRANSFERS_PER_REQUEST} transfers per request (got {len(pairs)}).",
        ))
        return errors

    # Compute the "effective squad" after removals to check for duplicates
    # and membership across pairs correctly.
    out_ids: list[int] = [p[0] for p in pairs]
    in_ids: list[int] = [p[1] for p in pairs]

    # No-op: same player in and out
    for player_out_id, player_in_id in pairs:
        if player_out_id == player_in_id:
            errors.append(TransferError(
                "no_op_transfer",
                f"Player {player_out_id} is both in and out — no-op transfers are not allowed.",
            ))

    # Duplicate player_out IDs
    if len(set(out_ids)) < len(out_ids):
        errors.append(TransferError(
            "duplicate_player_out",
            "The same player appears multiple times as a transfer out.",
        ))

    # Duplicate player_in IDs
    if len(set(in_ids)) < len(in_ids):
        errors.append(TransferError(
            "duplicate_player_in",
            "The same player appears multiple times as a transfer in.",
        ))

    # player_out must be in active squad
    for player_out_id, _ in pairs:
        if player_out_id not in active_player_ids:
            errors.append(TransferError(
                "player_out_not_in_squad",
                f"Player {player_out_id} is not in your active squad.",
            ))

    # player_in must not already be in squad (excluding players being sold in this batch)
    projected_squad = (active_player_ids - set(out_ids))
    for _, player_in_id in pairs:
        if player_in_id in projected_squad:
            errors.append(TransferError(
                "player_already_in_squad",
                f"Player {player_in_id} is already in your squad.",
            ))

    # Cross-pair conflict: player being bought cannot also be in the "out" list
    for player_out_id, player_in_id in pairs:
        if player_in_id in out_ids and player_in_id != player_out_id:
            errors.append(TransferError(
                "transfer_conflict",
                f"Player {player_in_id} cannot be transferred in while also being transferred out.",
            ))

    return errors


def compute_points_hit(num_transfers: int, free_transfers_available: int) -> tuple[int, int]:
    """
    Return (total_points_hit, paid_transfer_count) for a batch of transfers.

    free_transfers_available: how many free transfers the user currently has.
    """
    paid = max(0, num_transfers - free_transfers_available)
    from services.transfers.constants import POINTS_PER_EXTRA_TRANSFER
    return paid * POINTS_PER_EXTRA_TRANSFER, paid
