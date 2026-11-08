"""rename_fps_statuses_to_status
Revision ID: 032af810b6b7
Revises: f35dafa94c6b
Create Date: 2026-06-26 15:46:37.517229
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '032af810b6b7'
down_revision: Union[str, Sequence[str], None] = 'f35dafa94c6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename table
    op.rename_table('fps_statuses', 'status')

    # Rename indexes
    op.execute("ALTER INDEX ix_fps_statuses_id RENAME TO ix_status_id")
    op.execute("ALTER INDEX ix_fps_statuses_name RENAME TO ix_status_name")
    op.execute("ALTER TABLE status RENAME CONSTRAINT fps_statuses_pkey TO status_pkey")

    # Drop all FK constraints on fps_details referencing status_id,
    # regardless of auto-generated name, then recreate pointing at renamed table.
    op.execute("""
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (
                SELECT conname FROM pg_constraint
                WHERE conrelid = 'fps_details'::regclass
                AND contype = 'f'
                AND conname LIKE '%status%'
            ) LOOP
                EXECUTE 'ALTER TABLE fps_details DROP CONSTRAINT ' || quote_ident(r.conname);
            END LOOP;
        END $$;
    """)
    op.create_foreign_key(None, 'fps_details', 'status', ['status_id'], ['id'])

    # Same for webhook_events
    op.execute("""
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (
                SELECT conname FROM pg_constraint
                WHERE conrelid = 'webhook_events'::regclass
                AND contype = 'f'
                AND conname LIKE '%status%'
            ) LOOP
                EXECUTE 'ALTER TABLE webhook_events DROP CONSTRAINT ' || quote_ident(r.conname);
            END LOOP;
        END $$;
    """)
    op.create_foreign_key(None, 'webhook_events', 'status', ['status_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'webhook_events', type_='foreignkey')
    op.create_foreign_key('webhook_events_status_id_fkey', 'webhook_events', 'fps_statuses', ['status_id'], ['id'])
    op.drop_constraint(None, 'fps_details', type_='foreignkey')
    op.create_foreign_key('fps_details_status_id_fkey', 'fps_details', 'fps_statuses', ['status_id'], ['id'])

    op.rename_table('status', 'fps_statuses')

    op.execute("ALTER INDEX ix_status_id RENAME TO ix_fps_statuses_id")
    op.execute("ALTER INDEX ix_status_name RENAME TO ix_fps_statuses_name")
    op.execute("ALTER TABLE fps_statuses RENAME CONSTRAINT status_pkey TO fps_statuses_pkey")