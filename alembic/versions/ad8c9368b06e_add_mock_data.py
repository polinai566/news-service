"""Add mock data

Revision ID: ad8c9368b06e
Revises: 2d39d58f154e
Create Date: 2025-10-02 22:31:25.048269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad8c9368b06e'
down_revision: Union[str, Sequence[str], None] = '2d39d58f154e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
