"""
Top5 Fantasy — scoring engine.

Public surface:
  score_gameweek(db, gameweek_id)            Full GW scoring pass (fixtures → lineups → user scores)
  compute_fixture_player_points(db, fid)     Score one fixture's PlayerMatchStats rows
  compute_and_save_lineup_points(db, lid)    Aggregate one lineup (captain/VC logic)
  finalize_gameweek_ranks(db, gameweek_id)   Assign rank_global after all scores are in
"""

from .aggregate_gameweek_scores import finalize_gameweek_ranks, score_gameweek
from .compute_lineup_points import compute_and_save_lineup_points
from .compute_player_points import compute_fixture_player_points

__all__ = [
    "score_gameweek",
    "compute_fixture_player_points",
    "compute_and_save_lineup_points",
    "finalize_gameweek_ranks",
]
