"""
Breach monitoring tables migration.

Creates tables for storing HaveIBeenPwned breach check results.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


def upgrade():
    """Add breach monitoring tables."""

    # breach_checks table
    op.create_table(
        'breach_checks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('asset_id', UUID(as_uuid=True), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('check_type', sa.String(20), nullable=False),
        sa.Column('target', sa.String(255), nullable=False),
        sa.Column('breaches_found', sa.Integer, default=0),
        sa.Column('pastes_found', sa.Integer, default=0),
        sa.Column('total_pwn_count', sa.Integer, default=0),
        sa.Column('highest_severity', sa.String(20)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('error_message', sa.Text),
        sa.Column('checked_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_breach_checks_asset_id', 'breach_checks', ['asset_id'])
    op.create_index('ix_breach_checks_user_id', 'breach_checks', ['user_id'])
    op.create_index('ix_breach_checks_company_id', 'breach_checks', ['company_id'])
    op.create_index('ix_breach_checks_target', 'breach_checks', ['target'])

    # breach_results table
    op.create_table(
        'breach_results',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('breach_check_id', UUID(as_uuid=True), sa.ForeignKey('breach_checks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('breach_name', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255)),
        sa.Column('domain', sa.String(255)),
        sa.Column('breach_date', sa.String(20)),
        sa.Column('added_date', sa.DateTime),
        sa.Column('modified_date', sa.DateTime),
        sa.Column('pwn_count', sa.Integer, default=0),
        sa.Column('data_classes', JSON),
        sa.Column('description', sa.Text),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('is_fabricated', sa.Boolean, default=False),
        sa.Column('is_sensitive', sa.Boolean, default=False),
        sa.Column('is_retired', sa.Boolean, default=False),
        sa.Column('is_spam_list', sa.Boolean, default=False),
        sa.Column('severity', sa.String(20)),
        sa.Column('logo_path', sa.String(500)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_breach_results_breach_check_id', 'breach_results', ['breach_check_id'])
    op.create_index('ix_breach_results_breach_name', 'breach_results', ['breach_name'])

    # paste_exposures table
    op.create_table(
        'paste_exposures',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('breach_check_id', UUID(as_uuid=True), sa.ForeignKey('breach_checks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source', sa.String(50)),
        sa.Column('paste_id', sa.String(100)),
        sa.Column('title', sa.String(500)),
        sa.Column('date', sa.DateTime),
        sa.Column('email_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )


def downgrade():
    """Remove breach monitoring tables."""
    op.drop_table('paste_exposures')
    op.drop_table('breach_results')
    op.drop_table('breach_checks')
