"""Add sessions and sets tables

Revision ID: dffbc88ce38d
Revises: 815c40dd2887
Create Date: 2026-11-27 15:05:59.613760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dffbc88ce38d'
down_revision: Union[str, Sequence[str], None] = '815c40dd2887'
branch_labels: Union[str, Sequence[str]] = None
depends_on: Union[str, Sequence[str]] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('user_id_fkey', sa.ForeignKeyConstraint(['user_id'], ['users.id'], ), ),
        sa.Column('exercise_id_fkey', sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ), ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create sets table
    op.create_table(
        'sets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('session_id_fkey', sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ), ),
        sa.Column('exercise_id_fkey', sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ), ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index for faster queries
    op.create_index(op.f('ix_sets_session_id'), 'sets', ['session_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_sets_session_id'), table_name='sets')
    op.drop_table('sets')
    op.drop_table('sessions')