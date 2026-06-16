"""
Migration: Add password-reset columns to users table

The User model declares `reset_token` and `reset_token_expires`, but no prior
migration added them to the database. Any query that loads User columns (e.g.
the security-alert email lookup after a scan, and the password-reset flow)
fails with: column users.reset_token does not exist.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings


def run_migration():
    """Add reset_token / reset_token_expires columns to users."""
    print("=" * 70)
    print("MIGRATION: User password-reset columns")
    print("=" * 70)
    print()

    engine = create_engine(settings.DATABASE_URL)

    with engine.begin() as conn:
        print("1. Adding reset_token columns to users table...")
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255),
            ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP WITH TIME ZONE;
        """))
        print("   [OK] users.reset_token / users.reset_token_expires ensured")
        print()

    print("=" * 70)
    print("MIGRATION COMPLETE!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
