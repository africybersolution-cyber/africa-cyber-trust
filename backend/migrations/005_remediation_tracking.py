"""
Remediation tracking enhancement for findings.

Adds status tracking, assignment, and verification fields.
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    """Add remediation tracking fields to findings table."""

    # Add status field (replaces simple resolved boolean)
    op.add_column('findings', sa.Column('status', sa.String(20), server_default='open', nullable=False))

    # Add assignment tracking
    op.add_column('findings', sa.Column('assignee_id', sa.UUID(), nullable=True))

    # Add resolution tracking
    op.add_column('findings', sa.Column('resolution_notes', sa.Text, nullable=True))
    op.add_column('findings', sa.Column('marked_resolved_by', sa.UUID(), nullable=True))

    # Add verification tracking
    op.add_column('findings', sa.Column('verified_by', sa.UUID(), nullable=True))
    op.add_column('findings', sa.Column('verified_at', sa.TIMESTAMP(timezone=True), nullable=True))

    # Add last status change tracking
    op.add_column('findings', sa.Column('status_changed_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('findings', sa.Column('status_changed_by', sa.UUID(), nullable=True))

    # Create index on status for filtering
    op.create_index('ix_findings_status', 'findings', ['status'])

    # Migrate existing data: resolved=true → status='resolved'
    op.execute("""
        UPDATE findings
        SET status = CASE
            WHEN resolved = true THEN 'resolved'
            ELSE 'open'
        END
    """)


def downgrade():
    """Remove remediation tracking fields."""
    op.drop_index('ix_findings_status', 'findings')
    op.drop_column('findings', 'status_changed_by')
    op.drop_column('findings', 'status_changed_at')
    op.drop_column('findings', 'verified_at')
    op.drop_column('findings', 'verified_by')
    op.drop_column('findings', 'marked_resolved_by')
    op.drop_column('findings', 'resolution_notes')
    op.drop_column('findings', 'assignee_id')
    op.drop_column('findings', 'status')
