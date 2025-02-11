"""Initial migration

Revision ID: 12d29c1476ce
Revises:
Create Date: 2025-02-10 14:02:45.385823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12d29c1476ce'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('token_pairs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pair_address', sa.String(length=50), nullable=False),
    sa.Column('base_symbol', sa.String(length=50), nullable=True),
    sa.Column('base_address', sa.String(length=42), nullable=True),
    sa.Column('quote_symbol', sa.String(length=50), nullable=True),
    sa.Column('exchange_name', sa.String(length=100), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('volume_24h', sa.Float(), nullable=True),
    sa.Column('liquidity', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('pair_address')
    )


def downgrade() -> None:
    op.drop_table('token_pairs')
