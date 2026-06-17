"""Migration 009 - Add phone_number to users table"""
from sqlalchemy import text


def upgrade(db):
    """Add phone_number column to users table."""
    print("[Migration 009] Adding phone_number column to users table...")

    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='users' AND column_name='phone_number'
        """))

        if result.fetchone():
            print("[Migration 009] phone_number column already exists, skipping")
            return

        # Add phone_number column
        db.execute(text("""
            ALTER TABLE users
            ADD COLUMN phone_number VARCHAR(20)
        """))

        db.commit()
        print("[Migration 009] ✓ phone_number column added successfully")

    except Exception as e:
        print(f"[Migration 009] Error: {e}")
        db.rollback()
        raise


def downgrade(db):
    """Remove phone_number column."""
    print("[Migration 009] Removing phone_number column...")

    try:
        db.execute(text("""
            ALTER TABLE users
            DROP COLUMN IF EXISTS phone_number
        """))

        db.commit()
        print("[Migration 009] ✓ phone_number column removed")

    except Exception as e:
        print(f"[Migration 009] Error: {e}")
        db.rollback()
        raise
