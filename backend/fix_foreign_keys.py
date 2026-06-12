"""
Fix foreign key constraints to use CASCADE delete
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings


def fix_foreign_keys():
    """Update foreign key constraints to CASCADE."""
    print("=" * 70)
    print("FIXING FOREIGN KEY CONSTRAINTS")
    print("=" * 70)
    print()

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        try:
            # Fix verification_history FK
            print("1. Fixing verification_history foreign key...")

            # Drop existing constraint
            conn.execute(text("""
                ALTER TABLE verification_history
                DROP CONSTRAINT IF EXISTS verification_history_asset_id_fkey
            """))

            # Add with CASCADE
            conn.execute(text("""
                ALTER TABLE verification_history
                ADD CONSTRAINT verification_history_asset_id_fkey
                FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
            """))

            print("   [OK] verification_history FK updated to CASCADE")
            print()

            # Fix verification_tokens FK
            print("2. Fixing verification_tokens foreign key...")

            # Drop existing constraint
            conn.execute(text("""
                ALTER TABLE verification_tokens
                DROP CONSTRAINT IF EXISTS verification_tokens_asset_id_fkey
            """))

            # Add with CASCADE
            conn.execute(text("""
                ALTER TABLE verification_tokens
                ADD CONSTRAINT verification_tokens_asset_id_fkey
                FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
            """))

            print("   [OK] verification_tokens FK updated to CASCADE")
            print()

            # Fix audit_logs FKs (SET NULL is better for audit logs)
            print("3. Fixing audit_logs foreign keys...")

            # Drop existing constraints
            conn.execute(text("""
                ALTER TABLE audit_logs
                DROP CONSTRAINT IF EXISTS audit_logs_asset_id_fkey
            """))

            conn.execute(text("""
                ALTER TABLE audit_logs
                DROP CONSTRAINT IF EXISTS audit_logs_user_id_fkey
            """))

            # Add with SET NULL (audit logs should remain even if asset/user deleted)
            conn.execute(text("""
                ALTER TABLE audit_logs
                ADD CONSTRAINT audit_logs_asset_id_fkey
                FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL
            """))

            conn.execute(text("""
                ALTER TABLE audit_logs
                ADD CONSTRAINT audit_logs_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            """))

            print("   [OK] audit_logs FKs updated to SET NULL")
            print()

            conn.commit()

            print("=" * 70)
            print("FOREIGN KEY CONSTRAINTS FIXED!")
            print("=" * 70)
            print()
            print("Changes:")
            print("  - verification_history: CASCADE delete")
            print("  - verification_tokens: CASCADE delete")
            print("  - audit_logs: SET NULL (preserves audit trail)")

            return True

        except Exception as e:
            print(f"\n[ERROR] Failed to fix foreign keys: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


if __name__ == "__main__":
    success = fix_foreign_keys()
    sys.exit(0 if success else 1)
