"""Alter primary keys data type

Revision ID: 865310a0c412
Revises: 469e9f2a7d6e
Create Date: 2025-02-11 14:18:34.078594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '865310a0c412'
down_revision: Union[str, None] = '469e9f2a7d6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('token_pairs', 'id', existing_type=mysql.INTEGER(), type_=sa.BigInteger(), existing_autoincrement=True, existing_nullable=False)

def downgrade() -> None:
    op.alter_column('token_pairs', 'id', existing_type=sa.BigInteger(), type_=mysql.INTEGER(), existing_autoincrement=True, existing_nullable=False)
