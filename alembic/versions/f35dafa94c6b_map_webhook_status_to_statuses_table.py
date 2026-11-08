"""map_webhook_status_to_statuses_table
Revision ID: f35dafa94c6b
Revises: 47908aacfc8a
Create Date: 2026-06-26 15:20:49.006937
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f35dafa94c6b'
down_revision: Union[str, Sequence[str], None] = '47908aacfc8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    This migration was originally written against a partially-migrated database.
    On a fresh database, some objects already exist (created by earlier migrations)
    or don't exist (already renamed). All operations are made idempotent with
    if_exists/if_not_exists guards to handle both fresh and existing databases.
    """
    # On existing DBs this index was already renamed by 1ae18084d498.
    # On fresh DBs it doesn't exist either (same migration renamed it).
    # Either way, safe to skip if missing.
    op.drop_index(
        op.f('ix_fps_details_registration_number'),
        table_name='fps_details',
        if_exists=True
    )

    # On fresh DBs this index was already created by 1ae18084d498.
    # Skip if already present.
    op.create_index(
        op.f('ix_fps_details_account_number'),
        'fps_details',
        ['account_number'],
        unique=True,
        if_not_exists=True
    )

    # Add status_id to webhook_events only if it doesn't already exist.
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'webhook_events' AND column_name = 'status_id'
            ) THEN
                ALTER TABLE webhook_events ADD COLUMN status_id INTEGER NOT NULL DEFAULT 2;
            END IF;
        END $$;
    """)

    # Create index only if missing.
    op.create_index(
        op.f('ix_webhook_events_status_id'),
        'webhook_events',
        ['status_id'],
        unique=False,
        if_not_exists=True
    )

    # Create FK from webhook_events.status_id -> fps_statuses.id only if missing.
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conrelid = 'webhook_events'::regclass
                AND contype = 'f'
                AND conname LIKE '%status_id%'
            ) THEN
                ALTER TABLE webhook_events
                ADD CONSTRAINT webhook_events_status_id_fkey
                FOREIGN KEY (status_id) REFERENCES fps_statuses(id);
            END IF;
        END $$;
    """)

    # Drop the old status column only if it still exists.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'webhook_events' AND column_name = 'status'
            ) THEN
                ALTER TABLE webhook_events DROP COLUMN status;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('webhook_events', sa.Column('status', postgresql.ENUM('PENDING', 'PROCESSED', 'FAILED', name='webhookstatus'), server_default=sa.text("'PENDING'::webhookstatus"), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'webhook_events', type_='foreignkey')
    op.drop_index(op.f('ix_webhook_events_status_id'), table_name='webhook_events')
    op.drop_column('webhook_events', 'status_id')
    op.drop_index(op.f('ix_fps_details_account_number'), table_name='fps_details')
    op.create_index(op.f('ix_fps_details_registration_number'), 'fps_details', ['account_number'], unique=True)
