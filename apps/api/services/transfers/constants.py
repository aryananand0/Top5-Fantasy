"""
Transfer system constants.

Banking model:
  - Users start each squad with INITIAL_FREE_TRANSFERS (1).
  - Each gameweek rollover grants FREE_TRANSFERS_PER_GW (2) new free transfers.
  - Unused free transfers bank up to MAX_FREE_TRANSFERS_BANKED (3).
  - Extra transfers beyond available free transfers cost POINTS_PER_EXTRA_TRANSFER (4).

Formula at rollover: new_banked = min(current_banked + FREE_TRANSFERS_PER_GW, MAX_FREE_TRANSFERS_BANKED)
Formula at apply:    points_hit = max(0, len(transfers) - free_transfers_banked) * POINTS_PER_EXTRA_TRANSFER
"""

# New free transfers credited each gameweek rollover
FREE_TRANSFERS_PER_GW: int = 2

# Cap on banked free transfers (unused rollover up to this)
MAX_FREE_TRANSFERS_BANKED: int = 3

# Point penalty per transfer beyond free allowance
POINTS_PER_EXTRA_TRANSFER: int = 4

# Maximum transfers allowed in a single preview/apply request
MAX_TRANSFERS_PER_REQUEST: int = 5
