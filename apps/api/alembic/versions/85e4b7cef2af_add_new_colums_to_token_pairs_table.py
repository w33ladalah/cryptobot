"""Add new colums to token_pairs table

Revision ID: 85e4b7cef2af
Revises: bf92527561b2
Create Date: 2025-02-15 12:31:39.235658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '85e4b7cef2af'
down_revision: Union[str, None] = 'bf92527561b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('token_pairs', sa.Column('chain_id', sa.String(length=50), nullable=True))
    op.add_column('token_pairs', sa.Column('dex_id', sa.String(50), nullable=True))
    op.add_column('token_pairs', sa.Column('pair_url', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('token_pairs', 'chain_id')
    op.drop_column('token_pairs', 'dex_id')
    op.drop_column('token_pairs', 'pair_url')
