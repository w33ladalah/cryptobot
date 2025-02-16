"""Add foreign key token_id to platforms table

Revision ID: 9c3d1689024c
Revises: 85e4b7cef2af
Create Date: 2025-02-16 04:41:58.351901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '9c3d1689024c'
down_revision: Union[str, None] = '85e4b7cef2af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("platforms", sa.Column("token_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key("fk_token_id", "platforms", "tokens", ["token_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_token_id", "platforms", type_="foreignkey")
    op.drop_column("platforms", "token_id")
