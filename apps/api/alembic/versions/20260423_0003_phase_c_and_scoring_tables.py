"""Phase C and scoring tables

Adds all tables introduced in Phase C (Steps 8–13) plus the scoring
tables (Step 14). Also adds the fixtures→gameweeks FK that could not
be created in migration 0002 because gameweeks did not exist yet.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-23
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import ENUM as PgENUM

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # gameweeks
    # gameweek_status_enum and scoring_mode_enum are new — created on first use.
    # position_enum and data_quality_enum already exist from migration 0002;
    # reference them via PgENUM(create_type=False) to skip re-creation.
    # -----------------------------------------------------------------------
    op.create_table(
        "gameweeks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("number", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.String(50), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("UPCOMING", "LOCKED", "ACTIVE", "SCORING", "FINISHED",
                    name="gameweek_status_enum"),
            nullable=False,
            server_default=sa.text("'UPCOMING'"),
        ),
        sa.Column(
            "scoring_mode",
            sa.Enum("rich", "fallback", name="scoring_mode_enum"),
            nullable=False,
            server_default=sa.text("'rich'"),
        ),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season_id", "number", name="uq_gameweek_season_number"),
    )
    op.create_index("ix_gameweeks_season_status", "gameweeks", ["season_id", "status"])

    # Now we can add the FK from fixtures.gameweek_id → gameweeks.id
    # (The column already exists from migration 0002; only the constraint was missing.)
    op.create_foreign_key(
        "fk_fixtures_gameweek_id",
        "fixtures", "gameweeks",
        ["gameweek_id"], ["id"],
    )

    # -----------------------------------------------------------------------
    # player_match_stats
    # -----------------------------------------------------------------------
    op.create_table(
        "player_match_stats",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("fixture_id", sa.Integer(), sa.ForeignKey("fixtures.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column(
            "position_snapshot",
            PgENUM("GK", "DEF", "MID", "FWD", name="position_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("started", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("appeared", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("minutes_played", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("goals", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("assists", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("own_goals", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("yellow_cards", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("red_cards", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("clean_sheet", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("fantasy_points", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "data_quality",
            PgENUM("full", "partial", "estimated", name="data_quality_enum", create_type=False),
            nullable=False,
            server_default=sa.text("'full'"),
        ),
        sa.Column("raw_data", JSONB(), nullable=True),
        sa.Column("source_last_updated", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("player_id", "fixture_id", name="uq_player_match_stats"),
    )
    op.create_index("ix_pms_fixture", "player_match_stats", ["fixture_id"])
    op.create_index("ix_pms_player", "player_match_stats", ["player_id"])

    # -----------------------------------------------------------------------
    # price_history
    # -----------------------------------------------------------------------
    op.create_table(
        "price_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("gameweek_id", sa.Integer(), sa.ForeignKey("gameweeks.id"), nullable=False),
        sa.Column("old_price", sa.Numeric(6, 1), nullable=False),
        sa.Column("new_price", sa.Numeric(6, 1), nullable=False),
        sa.Column("change_amount", sa.Numeric(4, 1), nullable=False, server_default=sa.text("0.0")),
        sa.Column("reason_summary", sa.String(200), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("player_id", "gameweek_id", name="uq_price_history_player_gw"),
    )
    op.create_index("ix_price_history_player", "price_history", ["player_id"])

    # -----------------------------------------------------------------------
    # squads
    # -----------------------------------------------------------------------
    op.create_table(
        "squads",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("budget_remaining", sa.Numeric(6, 1), nullable=False),
        sa.Column("free_transfers_banked", sa.SmallInteger(), nullable=False, server_default=sa.text("1")),
        sa.Column("total_points", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "season_id", name="uq_squad_user_season"),
    )
    op.create_index("ix_squads_user", "squads", ["user_id"])

    # -----------------------------------------------------------------------
    # squad_players
    # -----------------------------------------------------------------------
    op.create_table(
        "squad_players",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("squad_id", sa.Integer(), sa.ForeignKey("squads.id"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("purchase_price", sa.Numeric(6, 1), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("squad_id", "player_id", name="uq_squad_player"),
    )
    op.create_index("ix_squad_players_squad", "squad_players", ["squad_id"])

    # -----------------------------------------------------------------------
    # gameweek_lineups
    # -----------------------------------------------------------------------
    op.create_table(
        "gameweek_lineups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("squad_id", sa.Integer(), sa.ForeignKey("squads.id"), nullable=False),
        sa.Column("gameweek_id", sa.Integer(), sa.ForeignKey("gameweeks.id"), nullable=False),
        sa.Column("captain_player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=True),
        sa.Column("vice_captain_player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=True),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("points_scored", sa.Integer(), nullable=True),
        sa.Column("transfer_cost_applied", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("squad_id", "gameweek_id", name="uq_lineup_squad_gameweek"),
    )
    op.create_index("ix_lineups_gameweek", "gameweek_lineups", ["gameweek_id"])

    # -----------------------------------------------------------------------
    # gameweek_lineup_players
    # -----------------------------------------------------------------------
    op.create_table(
        "gameweek_lineup_players",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("lineup_id", sa.Integer(), sa.ForeignKey("gameweek_lineups.id"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("points_scored", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lineup_id", "player_id", name="uq_lineup_player"),
    )
    op.create_index("ix_glp_lineup", "gameweek_lineup_players", ["lineup_id"])

    # -----------------------------------------------------------------------
    # transfers
    # -----------------------------------------------------------------------
    op.create_table(
        "transfers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("squad_id", sa.Integer(), sa.ForeignKey("squads.id"), nullable=False),
        sa.Column("gameweek_id", sa.Integer(), sa.ForeignKey("gameweeks.id"), nullable=False),
        sa.Column("player_out_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("player_in_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("sell_price", sa.Numeric(6, 1), nullable=False),
        sa.Column("buy_price", sa.Numeric(6, 1), nullable=False),
        sa.Column("is_free", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("points_hit", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transfers_squad_gw", "transfers", ["squad_id", "gameweek_id"])

    # -----------------------------------------------------------------------
    # mini_leagues
    # -----------------------------------------------------------------------
    op.create_table(
        "mini_leagues",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("created_by_user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_league_code"),
    )

    # -----------------------------------------------------------------------
    # league_members
    # -----------------------------------------------------------------------
    op.create_table(
        "league_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("league_id", sa.Integer(), sa.ForeignKey("mini_leagues.id"), nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("league_id", "user_id", name="uq_league_member"),
    )
    op.create_index("ix_league_members_league", "league_members", ["league_id"])

    # -----------------------------------------------------------------------
    # user_gameweek_scores  (Step 14 — scoring engine output)
    # -----------------------------------------------------------------------
    op.create_table(
        "user_gameweek_scores",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("squad_id", sa.Integer(), sa.ForeignKey("squads.id"), nullable=False),
        sa.Column("gameweek_id", sa.Integer(), sa.ForeignKey("gameweeks.id"), nullable=False),
        sa.Column("lineup_id", sa.Integer(), sa.ForeignKey("gameweek_lineups.id"), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("transfer_cost", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("captain_points", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("rank_global", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "gameweek_id", name="uq_user_gw_score"),
    )
    op.create_index("ix_ugws_gameweek_points", "user_gameweek_scores", ["gameweek_id", "points"])
    op.create_index("ix_ugws_squad", "user_gameweek_scores", ["squad_id"])


def downgrade() -> None:
    op.drop_index("ix_ugws_squad", table_name="user_gameweek_scores")
    op.drop_index("ix_ugws_gameweek_points", table_name="user_gameweek_scores")
    op.drop_table("user_gameweek_scores")

    op.drop_index("ix_league_members_league", table_name="league_members")
    op.drop_table("league_members")
    op.drop_table("mini_leagues")

    op.drop_index("ix_transfers_squad_gw", table_name="transfers")
    op.drop_table("transfers")

    op.drop_index("ix_glp_lineup", table_name="gameweek_lineup_players")
    op.drop_table("gameweek_lineup_players")
    op.drop_index("ix_lineups_gameweek", table_name="gameweek_lineups")
    op.drop_table("gameweek_lineups")

    op.drop_index("ix_squad_players_squad", table_name="squad_players")
    op.drop_table("squad_players")
    op.drop_index("ix_squads_user", table_name="squads")
    op.drop_table("squads")

    op.drop_index("ix_price_history_player", table_name="price_history")
    op.drop_table("price_history")

    op.drop_index("ix_pms_player", table_name="player_match_stats")
    op.drop_index("ix_pms_fixture", table_name="player_match_stats")
    op.drop_table("player_match_stats")

    op.drop_constraint("fk_fixtures_gameweek_id", "fixtures", type_="foreignkey")

    op.drop_index("ix_gameweeks_season_status", table_name="gameweeks")
    op.drop_table("gameweeks")

    op.execute("DROP TYPE IF EXISTS scoring_mode_enum")
    op.execute("DROP TYPE IF EXISTS gameweek_status_enum")
