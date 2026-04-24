"""
Pure unit tests for the scoring rules engine.

No DB required — tests call score_player_fixture() directly with
explicit inputs and verify the breakdown and total.
"""

import os
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost/top5fantasy_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-used-in-prod")

import pytest

from models.enums import Position, ScoringMode
from services.scoring.rules import (
    ASSIST_POINTS,
    CAPTAIN_MULTIPLIER,
    CLEAN_SHEET_POINTS,
    GOAL_POINTS,
    LONG_PLAY_BONUS,
    LONG_PLAY_THRESHOLD,
    RED_CARD_POINTS,
    YELLOW_CARD_POINTS,
    OWN_GOAL_POINTS,
    score_player_fixture,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score(
    position: Position = Position.MID,
    appeared: bool = True,
    minutes_played: int = 90,
    goals: int = 0,
    assists: int = 0,
    own_goals: int = 0,
    yellow_cards: int = 0,
    red_cards: int = 0,
    clean_sheet: bool = False,
    scoring_mode: ScoringMode = ScoringMode.RICH,
):
    return score_player_fixture(
        position=position,
        appeared=appeared,
        minutes_played=minutes_played,
        goals=goals,
        assists=assists,
        own_goals=own_goals,
        yellow_cards=yellow_cards,
        red_cards=red_cards,
        clean_sheet=clean_sheet,
        scoring_mode=scoring_mode,
    )


# ---------------------------------------------------------------------------
# Appearance
# ---------------------------------------------------------------------------

class TestAppearance:
    def test_did_not_appear_zero_points(self):
        bd = _score(appeared=False, minutes_played=0)
        assert bd.total == 0
        assert bd.appearance == 0

    def test_appeared_one_point(self):
        bd = _score(appeared=True, minutes_played=30)
        assert bd.appearance == 1

    def test_appeared_with_no_minutes_still_zero_appearance(self):
        # appeared=False overrides everything
        bd = _score(appeared=False, minutes_played=90)
        assert bd.total == 0


# ---------------------------------------------------------------------------
# 60-minute bonus
# ---------------------------------------------------------------------------

class TestLongPlayBonus:
    def test_exactly_60_minutes_earns_bonus_rich(self):
        bd = _score(minutes_played=60, scoring_mode=ScoringMode.RICH)
        assert bd.long_play_bonus == LONG_PLAY_BONUS

    def test_59_minutes_no_bonus_rich(self):
        bd = _score(minutes_played=59, scoring_mode=ScoringMode.RICH)
        assert bd.long_play_bonus == 0

    def test_90_minutes_earns_bonus_rich(self):
        bd = _score(minutes_played=90, scoring_mode=ScoringMode.RICH)
        assert bd.long_play_bonus == LONG_PLAY_BONUS

    def test_no_bonus_in_fallback_mode(self):
        bd = _score(minutes_played=90, scoring_mode=ScoringMode.FALLBACK)
        assert bd.long_play_bonus == 0

    def test_did_not_appear_no_bonus(self):
        bd = _score(appeared=False, minutes_played=90)
        assert bd.long_play_bonus == 0


# ---------------------------------------------------------------------------
# Goals by position
# ---------------------------------------------------------------------------

class TestGoalPoints:
    @pytest.mark.parametrize("position,expected", [
        (Position.FWD, 4),
        (Position.MID, 5),
        (Position.DEF, 6),
        (Position.GK,  6),
    ])
    def test_single_goal(self, position, expected):
        bd = _score(position=position, goals=1, minutes_played=90)
        assert bd.goals == expected

    def test_two_goals_fwd(self):
        bd = _score(position=Position.FWD, goals=2, minutes_played=90)
        assert bd.goals == GOAL_POINTS[Position.FWD] * 2

    def test_no_goal_zero_goal_points(self):
        bd = _score(goals=0)
        assert bd.goals == 0

    def test_goals_not_awarded_if_did_not_appear(self):
        bd = _score(appeared=False, goals=2)
        assert bd.total == 0


# ---------------------------------------------------------------------------
# Assists
# ---------------------------------------------------------------------------

class TestAssistPoints:
    def test_single_assist(self):
        bd = _score(assists=1)
        assert bd.assists == ASSIST_POINTS

    def test_two_assists(self):
        bd = _score(assists=2)
        assert bd.assists == ASSIST_POINTS * 2

    def test_no_assist(self):
        bd = _score(assists=0)
        assert bd.assists == 0


# ---------------------------------------------------------------------------
# Clean sheet (DEF / GK only)
# ---------------------------------------------------------------------------

class TestCleanSheet:
    @pytest.mark.parametrize("position", [Position.DEF, Position.GK])
    def test_clean_sheet_eligible_positions(self, position):
        bd = _score(position=position, clean_sheet=True, minutes_played=90)
        assert bd.clean_sheet == CLEAN_SHEET_POINTS

    @pytest.mark.parametrize("position", [Position.MID, Position.FWD])
    def test_clean_sheet_ineligible_positions(self, position):
        bd = _score(position=position, clean_sheet=True, minutes_played=90)
        assert bd.clean_sheet == 0

    def test_no_clean_sheet_zero_points(self):
        bd = _score(position=Position.DEF, clean_sheet=False)
        assert bd.clean_sheet == 0

    def test_clean_sheet_not_awarded_if_did_not_appear(self):
        bd = _score(position=Position.DEF, appeared=False, clean_sheet=True)
        assert bd.total == 0


# ---------------------------------------------------------------------------
# Negative events
# ---------------------------------------------------------------------------

class TestNegatives:
    def test_yellow_card(self):
        bd = _score(yellow_cards=1)
        assert bd.yellow_cards == YELLOW_CARD_POINTS

    def test_two_yellow_cards(self):
        bd = _score(yellow_cards=2)
        assert bd.yellow_cards == YELLOW_CARD_POINTS * 2

    def test_red_card(self):
        bd = _score(red_cards=1)
        assert bd.red_cards == RED_CARD_POINTS

    def test_own_goal(self):
        bd = _score(own_goals=1)
        assert bd.own_goals == OWN_GOAL_POINTS

    def test_two_own_goals(self):
        bd = _score(own_goals=2)
        assert bd.own_goals == OWN_GOAL_POINTS * 2

    def test_negatives_not_applied_if_did_not_appear(self):
        # Cards accumulated but player marked as not appeared → 0 points total
        bd = _score(appeared=False, yellow_cards=1, red_cards=1, own_goals=1)
        assert bd.total == 0


# ---------------------------------------------------------------------------
# Combined / real-world examples
# ---------------------------------------------------------------------------

class TestCombined:
    def test_typical_outfield_match(self):
        # MID played 75 min, scored 1, assisted 1, yellow card
        bd = _score(
            position=Position.MID,
            appeared=True,
            minutes_played=75,
            goals=1,
            assists=1,
            yellow_cards=1,
            scoring_mode=ScoringMode.RICH,
        )
        expected = (
            1               # appearance
            + 1             # 60+ bonus
            + GOAL_POINTS[Position.MID]  # goal
            + ASSIST_POINTS             # assist
            + YELLOW_CARD_POINTS        # yellow
        )
        assert bd.total == expected

    def test_gk_clean_sheet_rich(self):
        bd = _score(
            position=Position.GK,
            appeared=True,
            minutes_played=90,
            clean_sheet=True,
            scoring_mode=ScoringMode.RICH,
        )
        expected = 1 + 1 + CLEAN_SHEET_POINTS  # appearance + 60+ + CS
        assert bd.total == expected

    def test_gk_clean_sheet_fallback_no_60bonus(self):
        bd = _score(
            position=Position.GK,
            appeared=True,
            minutes_played=90,
            clean_sheet=True,
            scoring_mode=ScoringMode.FALLBACK,
        )
        expected = 1 + CLEAN_SHEET_POINTS  # appearance + CS (no 60+ bonus in fallback)
        assert bd.total == expected

    def test_zero_point_player_who_appeared_briefly(self):
        # DEF came on for 5 min (under 60), no events
        bd = _score(
            position=Position.DEF,
            appeared=True,
            minutes_played=5,
            scoring_mode=ScoringMode.RICH,
        )
        assert bd.total == 1  # appearance only

    def test_mode_used_stored(self):
        bd = _score(scoring_mode=ScoringMode.FALLBACK)
        assert bd.mode_used == ScoringMode.FALLBACK


# ---------------------------------------------------------------------------
# Scoring mode — FALLBACK behavior
# ---------------------------------------------------------------------------

class TestFallbackMode:
    def test_fallback_skips_60_bonus(self):
        rich = _score(minutes_played=90, scoring_mode=ScoringMode.RICH)
        fallback = _score(minutes_played=90, scoring_mode=ScoringMode.FALLBACK)
        assert rich.total == fallback.total + LONG_PLAY_BONUS

    def test_fallback_still_scores_goals(self):
        bd = _score(
            position=Position.FWD,
            goals=1,
            minutes_played=90,
            scoring_mode=ScoringMode.FALLBACK,
        )
        assert bd.goals == GOAL_POINTS[Position.FWD]

    def test_fallback_still_scores_appearance(self):
        bd = _score(appeared=True, scoring_mode=ScoringMode.FALLBACK)
        assert bd.appearance == 1
