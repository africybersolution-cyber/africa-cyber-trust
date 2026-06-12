"""
Migration: Comprehensive Verification System Tables
Created: 2026-06-09
Purpose: Add verification_history, verification_tokens, and audit_logs tables
"""
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings


def create_verification_history_table(conn):
    """Create verification_history table to track all verification attempts."""
    sql = """
    CREATE TABLE IF NOT EXISTS verification_history (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
        method VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        attempted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        completed_at TIMESTAMP WITH TIME ZONE,
        ip_address VARCHAR(100),
        user_agent TEXT,
        error_message TEXT,
        verification_data JSONB,

        -- Indexes for performance
        CONSTRAINT verification_history_method_check
            CHECK (method IN ('dns_txt', 'html_file', 'admin_email', 'meta_tag', 'cname')),
        CONSTRAINT verification_history_status_check
            CHECK (status IN ('pending', 'success', 'failed', 'expired'))
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_verification_history_asset_id
        ON verification_history(asset_id);
    CREATE INDEX IF NOT EXISTS idx_verification_history_status
        ON verification_history(status);
    CREATE INDEX IF NOT EXISTS idx_verification_history_attempted_at
        ON verification_history(attempted_at DESC);

    -- Add comment
    COMMENT ON TABLE verification_history IS
        'Tracks all domain verification attempts with complete audit trail';
    """

    print("Creating verification_history table...")
    conn.execute(text(sql))
    conn.commit()
    print("[OK] verification_history table created successfully")


def create_verification_tokens_table(conn):
    """Create verification_tokens table for secure token management."""
    sql = """
    CREATE TABLE IF NOT EXISTS verification_tokens (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
        token VARCHAR(255) NOT NULL UNIQUE,
        method VARCHAR(50) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        used_at TIMESTAMP WITH TIME ZONE,
        is_valid BOOLEAN NOT NULL DEFAULT TRUE,

        -- Constraints
        CONSTRAINT verification_tokens_method_check
            CHECK (method IN ('dns_txt', 'html_file', 'admin_email', 'meta_tag', 'cname'))
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_verification_tokens_asset_id
        ON verification_tokens(asset_id);
    CREATE INDEX IF NOT EXISTS idx_verification_tokens_token
        ON verification_tokens(token);
    CREATE INDEX IF NOT EXISTS idx_verification_tokens_expires_at
        ON verification_tokens(expires_at);
    CREATE INDEX IF NOT EXISTS idx_verification_tokens_is_valid
        ON verification_tokens(is_valid) WHERE is_valid = TRUE;

    -- Add comment
    COMMENT ON TABLE verification_tokens IS
        'Manages verification tokens with expiration and usage tracking';
    """

    print("Creating verification_tokens table...")
    conn.execute(text(sql))
    conn.commit()
    print("[OK] verification_tokens table created successfully")


def create_audit_logs_table(conn):
    """Create audit_logs table for complete activity tracking."""
    sql = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
        user_id UUID REFERENCES users(id) ON DELETE SET NULL,
        action VARCHAR(100) NOT NULL,
        details JSONB,
        ip_address VARCHAR(100),
        user_agent TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

        -- Constraints
        CONSTRAINT audit_logs_action_check
            CHECK (action IN (
                'verification_started',
                'verification_completed',
                'verification_failed',
                'token_generated',
                'token_expired',
                'token_used',
                'manual_approval',
                'manual_rejection',
                're_verification_required'
            ))
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_audit_logs_asset_id
        ON audit_logs(asset_id);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id
        ON audit_logs(user_id);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_action
        ON audit_logs(action);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
        ON audit_logs(created_at DESC);

    -- Add comment
    COMMENT ON TABLE audit_logs IS
        'Complete audit trail of all verification and security activities';
    """

    print("Creating audit_logs table...")
    conn.execute(text(sql))
    conn.commit()
    print("[OK] audit_logs table created successfully")


def verify_tables(conn):
    """Verify that all tables were created successfully."""
    print("\n[CHECK] Verifying table creation...")

    tables = ['verification_history', 'verification_tokens', 'audit_logs']

    for table in tables:
        result = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = '{table}'
            );
        """))
        exists = result.fetchone()[0]

        if exists:
            print(f"  [OK] {table} exists")
        else:
            print(f"  [X] {table} MISSING!")
            return False

    print("\n[OK] All tables verified successfully!")
    return True


def run_migration():
    """Run the complete migration."""
    print("=" * 60)
    print("VERIFICATION SYSTEM MIGRATION")
    print("=" * 60)
    print()

    try:
        # Connect to database
        print("Connecting to database...")
        engine = create_engine(settings.DATABASE_URL)
        conn = engine.connect()
        print("[OK] Connected to database\n")

        # Create tables
        create_verification_history_table(conn)
        print()
        create_verification_tokens_table(conn)
        print()
        create_audit_logs_table(conn)
        print()

        # Verify tables
        if verify_tables(conn):
            print("\n" + "=" * 60)
            print("MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            return True
        else:
            print("\n[ERROR] Migration verification failed!")
            return False

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
