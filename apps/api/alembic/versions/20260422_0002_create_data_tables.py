"""create data tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-22
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- seasons ---
    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("label", sa.String(20), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("label"),
    )

    # --- competitions ---
    op.create_table(
        "competitions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("country", sa.String(50), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # --- teams ---
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("short_name", sa.String(50), nullable=True),
        sa.Column("tla", sa.String(5), nullable=True),
        sa.Column(
            "competition_id", sa.Integer(),
            sa.ForeignKey("competitions.id"), nullable=False, index=True,
        ),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column("badge_url", sa.String(500), nullable=True),
        sa.Column("strength", sa.SmallInteger(), nullable=False, server_default=sa.text("3")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )

    # --- players ---
    # position_enum is created here on first use (no create_type=False).
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("position", sa.Enum("GK", "DEF", "MID", "FWD", name="position_enum"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("nationality", sa.String(50), nullable=True),
        sa.Column("base_price", sa.Numeric(6, 1), nullable=False),
        sa.Column("current_price", sa.Numeric(6, 1), nullable=False),
        sa.Column("starter_confidence", sa.SmallInteger(), nullable=False, server_default=sa.text("3")),
        sa.Column("form_score", sa.Numeric(5, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("availability_note", sa.String(200), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id", "season_id", name="uq_player_external_season"),
    )
    op.create_index("ix_players_team_season", "players", ["team_id", "season_id"])
    op.create_index("ix_players_position", "players", ["position"])
    op.create_index("ix_players_current_price", "players", ["current_price"])

    # --- fixtures ---
    # fixture_status_enum and data_quality_enum are created here on first use.
    # gameweek_id is an integer column only — the FK to gameweeks is added in
    # migration 0003 after the gameweeks table is created.
    op.create_table(
        "fixtures",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("competition_id", sa.Integer(), sa.ForeignKey("competitions.id"), nullable=False),
        sa.Column("gameweek_id", sa.Integer(), nullable=True),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("kickoff_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum("SCHEDULED", "LIVE", "FINISHED", "POSTPONED", "CANCELLED",
                    name="fixture_status_enum"),
            nullable=False,
            server_default=sa.text("'SCHEDULED'"),
        ),
        sa.Column("home_score", sa.SmallInteger(), nullable=True),
        sa.Column("away_score", sa.SmallInteger(), nullable=True),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column(
            "data_quality_status",
            sa.Enum("full", "partial", "estimated", name="data_quality_enum"),
            nullable=False,
            server_default=sa.text("'full'"),
        ),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id", name="uq_fixture_external_id"),
    )
    op.create_index("ix_fixtures_gameweek", "fixtures", ["gameweek_id"])
    op.create_index("ix_fixtures_kickoff", "fixtures", ["kickoff_at"])
    op.create_index("ix_fixtures_status", "fixtures", ["status"])


def downgrade() -> None:
    op.drop_index("ix_fixtures_status", table_name="fixtures")
    op.drop_index("ix_fixtures_kickoff", table_name="fixtures")
    op.drop_index("ix_fixtures_gameweek", table_name="fixtures")
    op.drop_table("fixtures")
    op.drop_index("ix_players_current_price", table_name="players")
    op.drop_index("ix_players_position", table_name="players")
    op.drop_index("ix_players_team_season", table_name="players")
    op.drop_table("players")
    op.drop_table("teams")
    op.drop_table("competitions")
    op.drop_table("seasons")

    op.execute("DROP TYPE IF EXISTS data_quality_enum")
    op.execute("DROP TYPE IF EXISTS fixture_status_enum")
    op.execute("DROP TYPE IF EXISTS position_enum")
