"""merge heads

Revision ID: 47908aacfc8a
Revises: 1811cc470654, e1f8c819ee6a
Create Date: 2026-06-26 14:49:37.604888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47908aacfc8a'
down_revision: Union[str, Sequence[str], None] = ('1811cc470654', 'e1f8c819ee6a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
