"""Add new column: quote_address

Revision ID: 74fd4d7c082e
Revises: 12d29c1476ce
Create Date: 2025-02-10 15:39:18.229369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '74fd4d7c082e'
down_revision: Union[str, None] = '12d29c1476ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('token_pairs', sa.Column('quote_address', sa.String(length=42), nullable=True))


def downgrade() -> None:
    op.drop_column('token_pairs', 'quote_address')
