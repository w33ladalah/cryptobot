"""Create table token_platform

Revision ID: bf92527561b2
Revises: d6679398b341
Create Date: 2025-02-15 04:15:23.358628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'bf92527561b2'
down_revision: Union[str, None] = 'd6679398b341'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'token_platform',
        sa.Column('token_id', sa.BigInteger(), nullable=False),
        sa.Column('platform_id', sa.BigInteger(), nullable=False),
        # sa.ForeignKeyConstraint(['platform_id'], ['platforms.id'], ),
        # sa.ForeignKeyConstraint(['token_id'], ['tokens.id'], ),
        # sa.PrimaryKeyConstraint('token_id', 'platform_id')
    )

    op.create_foreign_key('fk_token_platform_token_id', 'token_platform', 'tokens', ['token_id'], ['id'])
    op.create_foreign_key('fk_token_platform_platform_id', 'token_platform', 'platforms', ['platform_id'], ['id'])
    op.create_primary_key('pk_token_platform', 'token_platform', ['token_id', 'platform_id'])


def downgrade() -> None:
    op.drop_table('token_platform')
