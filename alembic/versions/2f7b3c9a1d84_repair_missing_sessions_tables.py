"""Repair session tables missing from databases already marked at the prior head.

Revision ID: 2f7b3c9a1d84
Revises: dffbc88ce38d
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f7b3c9a1d84"
down_revision: Union[str, Sequence[str], None] = "dffbc88ce38d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("sessions"):
        op.create_table(
            "sessions",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("exercise_id", sa.Integer(), nullable=False),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        )

    inspector = sa.inspect(bind)
    if not inspector.has_table("sets"):
        op.create_table(
            "sets",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("session_id", sa.Integer(), nullable=False),
            sa.Column("exercise_id", sa.Integer(), nullable=False),
            sa.Column("reps", sa.Integer(), nullable=False),
            sa.Column("weight", sa.Float(), nullable=False),
            sa.Column("order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
            sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        )

    indexes = {index["name"] for index in sa.inspect(bind).get_indexes("sets")}
    if "ix_sets_session_id" not in indexes:
        op.create_index("ix_sets_session_id", "sets", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sets_session_id", table_name="sets")
    op.drop_table("sets")
    op.drop_table("sessions")
