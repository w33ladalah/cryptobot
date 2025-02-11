"""Alter updated_at to nullable

Revision ID: 452ba2ec6d2b
Revises: 879a32a0d0cd
Create Date: 2025-02-11 22:59:57.416906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '452ba2ec6d2b'
down_revision: Union[str, None] = '879a32a0d0cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('tokens', 'updated_at', existing_type=mysql.DATETIME(), nullable=True)


def downgrade() -> None:
    op.alter_column('tokens', 'updated_at', existing_type=mysql.DATETIME(), nullable=False)
