"""Add alias_id column to tokens table

Revision ID: 879a32a0d0cd
Revises: 865310a0c412
Create Date: 2025-02-11 22:55:11.392688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '879a32a0d0cd'
down_revision: Union[str, None] = '865310a0c412'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tokens', sa.Column('alias_id', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('tokens', 'alias_id')
