"""
Super Admin System - Phase 1

Adds role-based access control, admin audit logging, and manual user/subscription management.

Migration 006
"""
from sqlalchemy import text

def upgrade(engine):
    """Add super admin capabilities."""

    with engine.connect() as conn:
        # 1. Extend users table with roles and admin features
        conn.execute(text("""
            -- Add role column (default to customer for existing users)
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'customer';

            -- Add active status flag
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true;

            -- Add TOTP secret for 2FA (admin only)
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(64);

            -- Track referral attribution
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS referred_by_code VARCHAR(20);

            -- Track manual grants (for negotiated deals)
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS granted_by_admin_id UUID REFERENCES users(id);
        """))

        # 2. Create indexes for performance
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
            CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
            CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users(referred_by_code);
        """))

        # 3. Create admin audit log table (append-only)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id BIGSERIAL PRIMARY KEY,
                actor_id UUID NOT NULL REFERENCES users(id),
                action VARCHAR(60) NOT NULL,
                target_type VARCHAR(40),
                target_id TEXT,
                context_data JSONB,
                ip_address INET,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_audit_actor
                ON admin_audit_logs(actor_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_audit_action
                ON admin_audit_logs(action);
            CREATE INDEX IF NOT EXISTS idx_audit_created
                ON admin_audit_logs(created_at DESC);
        """))

        # 4. Add comment for documentation
        conn.execute(text("""
            COMMENT ON TABLE admin_audit_logs IS
            'Append-only audit trail for all admin actions. Never update or delete.';

            COMMENT ON COLUMN users.role IS
            'User role: customer, agent, support_admin, super_admin';
        """))

        conn.commit()
        print("[MIGRATION 006] ✅ Super admin system tables created")


def downgrade(engine):
    """Remove super admin additions (use with caution in production)."""

    with engine.connect() as conn:
        # Drop audit log
        conn.execute(text("DROP TABLE IF EXISTS admin_audit_logs CASCADE;"))

        # Remove user columns (keep data, just remove columns)
        conn.execute(text("""
            ALTER TABLE users DROP COLUMN IF EXISTS role;
            ALTER TABLE users DROP COLUMN IF EXISTS is_active;
            ALTER TABLE users DROP COLUMN IF EXISTS totp_secret;
            ALTER TABLE users DROP COLUMN IF EXISTS referred_by_code;
            ALTER TABLE users DROP COLUMN IF EXISTS granted_by_admin_id;
        """))

        conn.commit()
        print("[MIGRATION 006] ⚠️  Super admin system removed")


if __name__ == "__main__":
    # Test migration
    from app.db.database import get_engine

    engine = get_engine()
    if engine:
        print("Running migration 006...")
        upgrade(engine)
        print("Migration complete!")
    else:
        print("Could not connect to database")
