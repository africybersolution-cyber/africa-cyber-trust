"""
Run Migration 009: Refresh Tokens

Execute this script to create the refresh_tokens table in production.
Usage: python run_migration_009.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Run the refresh_tokens migration."""
    print("Connecting to database...")
    print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'hidden'}")

    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as connection:
            print("\n[*] Creating refresh_tokens table...")

            # Create table
            connection.execute(text("""
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
            connection.commit()
            print("[OK] Table created")

            # Create indexes
            print("\n[*] Creating indexes...")
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
            """))
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
            """))
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);
            """))
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_refresh_tokens_revoked ON refresh_tokens(is_revoked);
            """))
            connection.commit()
            print("[OK] Indexes created")

            # Verify
            result = connection.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = 'refresh_tokens';
            """))
            count = result.scalar()

            if count == 1:
                print("\n[OK] Migration 009 completed successfully!")
                print(" Refresh token system is now active")
            else:
                print("\n[ERROR] Migration verification failed")
                return False

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION 009: Refresh Tokens System")
    print("=" * 60)

    success = run_migration()

    if success:
        print("\n" + "=" * 60)
        print("[OK] MIGRATION COMPLETE!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("[ERROR] MIGRATION FAILED!")
        print("=" * 60)
        sys.exit(1)
