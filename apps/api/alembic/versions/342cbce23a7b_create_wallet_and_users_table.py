"""Create wallet and users table

Revision ID: 342cbce23a7b
Revises: c001614f32ae
Create Date: 2025-03-01 02:03:25.123144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '342cbce23a7b'
down_revision: Union[str, None] = 'c001614f32ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("username", mysql.VARCHAR(length=50), nullable=False),
        sa.Column("email", mysql.VARCHAR(length=100), nullable=True),
        sa.Column("hashed_password", mysql.VARCHAR(length=255), nullable=False),
        sa.Column("created_at", mysql.DATETIME(), nullable=True),
        sa.Column("updated_at", mysql.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index("users_email", "users", ["email"], unique=True)
    op.create_index("users_username", "users", ["username"], unique=True)

    op.create_table(
        "wallets",
        sa.Column("id", mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("user_id", mysql.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("wallet_name", mysql.VARCHAR(length=100), nullable=True),
        sa.Column("wallet_address", mysql.VARCHAR(length=42), nullable=True),
        sa.Column("wallet_currency", mysql.VARCHAR(length=50), nullable=True),
        sa.Column("created_at", mysql.DATETIME(), nullable=True),
        sa.Column("updated_at", mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_id"),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index("wallets_wallet_address", "wallets", ["wallet_address"], unique=True)
    op.create_index("wallets_wallet_name", "wallets", ["wallet_name"], unique=False)
    op.create_index("wallets_wallet_currency", "wallets", ["wallet_currency"], unique=False)


def downgrade() -> None:
    op.drop_index("wallets_wallet_currency", table_name="wallets")
    op.drop_index("wallets_wallet_name", table_name="wallets")
    op.drop_index("wallets_wallet_address", table_name="wallets")
    op.drop_table("wallets")
    op.drop_index("users_username", table_name="users")
    op.drop_index("users_email", table_name="users")
    op.drop_table("users")
