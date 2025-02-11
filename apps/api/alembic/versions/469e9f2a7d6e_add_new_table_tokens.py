"""Add new table: tokens

Revision ID: 469e9f2a7d6e
Revises: 74fd4d7c082e
Create Date: 2025-02-11 14:01:31.840036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '469e9f2a7d6e'
down_revision: Union[str, None] = '74fd4d7c082e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=42), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address')
    )

    op.drop_column('token_pairs', 'base_symbol')
    op.drop_column('token_pairs', 'base_address')
    op.drop_column('token_pairs', 'quote_symbol')
    op.drop_column('token_pairs', 'quote_address')

    op.add_column('token_pairs', sa.Column('base_token_id', sa.Integer(), nullable=False))
    op.add_column('token_pairs', sa.Column('quote_token_id', sa.Integer(), nullable=False))

    op.create_foreign_key('fk_base_token_id', 'token_pairs', 'tokens', ['base_token_id'], ['id'])
    op.create_foreign_key('fk_quote_token_id', 'token_pairs', 'tokens', ['quote_token_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('fk_base_token_id', 'token_pairs', type_='foreignkey')
    op.drop_constraint('fk_quote_token_id', 'token_pairs', type_='foreignkey')

    op.drop_column('token_pairs', 'base_token_id')
    op.drop_column('token_pairs', 'quote_token_id')

    op.add_column('token_pairs', sa.Column('base_symbol', sa.String(length=50), nullable=True))
    op.add_column('token_pairs', sa.Column('base_address', sa.String(length=42), nullable=True))
    op.add_column('token_pairs', sa.Column('quote_symbol', sa.String(length=50), nullable=True))
    op.add_column('token_pairs', sa.Column('quote_address', sa.String(length=42), nullable=True))

    op.drop_table('tokens')
