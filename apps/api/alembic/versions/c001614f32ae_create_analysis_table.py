"""Create analysis table

Revision ID: c001614f32ae
Revises: 9c3d1689024c
Create Date: 2025-02-20 20:50:11.622186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c001614f32ae'
down_revision: Union[str, None] = '9c3d1689024c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analysis_results",
        sa.Column("id", mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("token_pair_id", mysql.BIGINT(), nullable=False),
        sa.Column("historical_data_key", mysql.VARCHAR(length=100), nullable=False),
        sa.Column("token_pairs_key", mysql.VARCHAR(length=100), nullable=False),
        sa.Column("real_time_data_key", mysql.VARCHAR(length=100), nullable=False),
        sa.Column("combined_data_key", mysql.VARCHAR(length=100), nullable=False),
        sa.Column("buying_decision", mysql.VARCHAR(length=50), nullable=False),
        sa.Column("trend", mysql.VARCHAR(length=50), nullable=False),
        sa.Column("sentiment", mysql.VARCHAR(length=50), nullable=False),
        sa.Column("volatility", mysql.VARCHAR(length=50), nullable=False),
        sa.Column("reasoning", mysql.TEXT(), nullable=False),
        sa.Column("insights", mysql.TEXT(), nullable=False),
        sa.Column("created_at", mysql.DATETIME(), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index("idx_analysis_results_token_id", "analysis_results", ["token_pair_id"], unique=False)
    op.create_foreign_key(
        "fk_analysis_results_token_pair_id",
        "analysis_results",
        "token_pairs",
        ["token_pair_id"],
        ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint("fk_analysis_results_token_pair_id", "analysis_results", type_="foreignkey")
    op.drop_index("idx_analysis_results_token_id", table_name="analysis_results")
    op.drop_table("analysis_results")
