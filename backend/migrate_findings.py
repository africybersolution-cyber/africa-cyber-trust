#!/usr/bin/env python3
"""
Migration script to add missing columns to findings table.
Run this ONCE on Render to fix the database schema.
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Add missing columns to findings table."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False

    # Fix SQLAlchemy 2.0 URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    print(f"🔗 Connecting to database...")
    engine = create_engine(database_url)

    migration_sql = """
    -- Add missing columns to findings table
    ALTER TABLE findings
    ADD COLUMN IF NOT EXISTS assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS resolution_notes TEXT,
    ADD COLUMN IF NOT EXISTS marked_resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS status_changed_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS status_changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS finding_data JSONB;

    -- Add status column if it doesn't exist
    ALTER TABLE findings
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'open' NOT NULL;

    -- Create index on status
    CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(status);
    """

    try:
        with engine.connect() as conn:
            print("🔧 Running migration...")
            conn.execute(text(migration_sql))
            conn.commit()
            print("✅ Migration completed successfully!")

            # Verify
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'findings'
                AND column_name IN ('assignee_id', 'resolution_notes', 'verified_by', 'status')
                ORDER BY column_name
            """))

            columns = [row[0] for row in result]
            print(f"📊 Verified columns: {', '.join(columns)}")

            return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("FINDINGS TABLE MIGRATION")
    print("=" * 60)
    success = run_migration()
    print("=" * 60)
    if success:
        print("✅ MIGRATION SUCCESSFUL - Scanning should work now!")
    else:
        print("❌ MIGRATION FAILED - Check errors above")
    print("=" * 60)
