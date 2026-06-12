"""Add verification_token column to assets table."""
from sqlalchemy import create_engine, text
from app.core.config import settings

def add_verification_token():
    """Add verification_token column."""
    engine = create_engine(settings.DATABASE_URL)

    migration = """
    ALTER TABLE assets
    ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255);
    """

    with engine.connect() as conn:
        print("Adding verification_token column...")
        try:
            conn.execute(text(migration))
            conn.commit()
            print("SUCCESS - verification_token column added!")
        except Exception as e:
            print(f"ERROR: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_verification_token()
