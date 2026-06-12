"""Migration script to update assets table with new columns."""
from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate_assets_table():
    """Add missing columns to assets table."""
    engine = create_engine(settings.DATABASE_URL)

    migrations = [
        # Add name column if it doesn't exist
        """
        ALTER TABLE assets
        ADD COLUMN IF NOT EXISTS name VARCHAR(255);
        """,

        # Add monitoring columns
        """
        ALTER TABLE assets
        ADD COLUMN IF NOT EXISTS scan_interval VARCHAR(50) DEFAULT '24h',
        ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'pending',
        ADD COLUMN IF NOT EXISTS score VARCHAR(50),
        ADD COLUMN IF NOT EXISTS alerts_enabled BOOLEAN DEFAULT true,
        ADD COLUMN IF NOT EXISTS next_scan_at TIMESTAMP WITH TIME ZONE;
        """,
    ]

    with engine.connect() as conn:
        print("Running migrations...")
        for migration in migrations:
            try:
                conn.execute(text(migration))
                conn.commit()
                print(f"OK Migration applied successfully")
            except Exception as e:
                print(f"ERROR Migration failed: {e}")
                conn.rollback()

    print("\nSUCCESS All migrations completed!")

if __name__ == "__main__":
    migrate_assets_table()
