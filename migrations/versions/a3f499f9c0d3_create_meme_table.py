"""create meme table

Revision ID: a3f499f9c0d3
Revises: 
Create Date: 2024-06-18 14:32:25.931591

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3f499f9c0d3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    table_name = "memes"

    op.create_table(
        table_name,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("meme_url", sa.String(length=255), unique=True),
        sa.Column("meme_description", sa.String(length=255), unique=True),
    )


def downgrade() -> None:
    table_name = "memes"
    op.drop_table(table_name)
