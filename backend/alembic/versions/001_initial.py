"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-09-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "connected_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("platform", sa.String(32), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("connected", sa.Boolean(), default=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "track_cache",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("platform", sa.String(32), nullable=False),
        sa.Column("platform_id", sa.String(128), nullable=False),
        sa.Column("isrc", sa.String(32), nullable=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("artist", sa.String(512), nullable=False),
        sa.Column("album", sa.String(512), nullable=True),
        sa.Column("danceability", sa.Float(), nullable=True),
        sa.Column("energy", sa.Float(), nullable=True),
        sa.Column("valence", sa.Float(), nullable=True),
        sa.Column("tempo", sa.Float(), nullable=True),
        sa.Column("acousticness", sa.Float(), nullable=True),
        sa.Column("key", sa.Integer(), nullable=True),
        sa.Column("mode", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
    )
    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source_platform", sa.String(32), nullable=False),
        sa.Column("target_platform", sa.String(32), nullable=False),
        sa.Column("source_playlist_id", sa.String(128), nullable=False),
        sa.Column("target_playlist_id", sa.String(128), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("matched", sa.Integer(), default=0),
        sa.Column("unmatched", sa.Integer(), default=0),
        sa.Column("total", sa.Integer(), default=0),
        sa.Column("detail_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("sync_jobs")
    op.drop_table("track_cache")
    op.drop_table("connected_accounts")
    op.drop_table("users")
