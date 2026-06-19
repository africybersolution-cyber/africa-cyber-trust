"""Migration 009: Refresh Token System

Creates refresh_tokens table for secure JWT token management with revocation support.
This enables httpOnly cookie-based authentication and logout functionality.
"""
from sqlalchemy import text


def upgrade(db_connection):
    """Add refresh_tokens table."""

    # Create refresh_tokens table
    db_connection.execute(text("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token VARCHAR(500) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            is_revoked BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            revoked_at TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent VARCHAR(500)
        );
    """))

    # Create indexes for performance
    db_connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
        CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
        CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);
        CREATE INDEX IF NOT EXISTS idx_refresh_tokens_revoked ON refresh_tokens(is_revoked);
    """))

    print("✅ Migration 009: refresh_tokens table created")


def downgrade(db_connection):
    """Remove refresh_tokens table."""

    db_connection.execute(text("""
        DROP TABLE IF EXISTS refresh_tokens CASCADE;
    """))

    print("✅ Migration 009: refresh_tokens table dropped")
