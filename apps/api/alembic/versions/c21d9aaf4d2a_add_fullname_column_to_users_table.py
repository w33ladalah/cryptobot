"""Add fullname column to users table

Revision ID: c21d9aaf4d2a
Revises: 342cbce23a7b
Create Date: 2025-03-01 06:24:18.729282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c21d9aaf4d2a'
down_revision: Union[str, None] = '342cbce23a7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('fullname', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'fullname')
