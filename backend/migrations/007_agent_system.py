"""
Agent & Affiliate System - Phase 2

Multi-tier commission system with agent management, payouts, and country managers.

Migration 007
"""
from sqlalchemy import text

def upgrade(engine):
    """Add agent and commission tables."""

    with engine.connect() as conn:
        # 1. Create agents table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                referral_code VARCHAR(20) NOT NULL UNIQUE,
                country VARCHAR(2) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                tier VARCHAR(20) NOT NULL DEFAULT 'bronze',
                total_sales DECIMAL(10, 2) NOT NULL DEFAULT 0,
                total_commissions DECIMAL(10, 2) NOT NULL DEFAULT 0,
                monthly_sales DECIMAL(10, 2) NOT NULL DEFAULT 0,
                is_country_manager BOOLEAN NOT NULL DEFAULT false,
                approved_at TIMESTAMP WITH TIME ZONE,
                approved_by UUID REFERENCES users(id),
                rejected_at TIMESTAMP WITH TIME ZONE,
                rejection_reason TEXT,
                demo_scans_remaining INTEGER NOT NULL DEFAULT 5,
                parent_agent_id UUID REFERENCES agents(id),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);
            CREATE INDEX IF NOT EXISTS idx_agents_referral_code ON agents(referral_code);
            CREATE INDEX IF NOT EXISTS idx_agents_country ON agents(country);
            CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
            CREATE INDEX IF NOT EXISTS idx_agents_parent ON agents(parent_agent_id);
        """))

        # 2. Create commissions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS commissions (
                id BIGSERIAL PRIMARY KEY,
                agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
                payment_id UUID NOT NULL REFERENCES payments(id),
                customer_user_id UUID NOT NULL REFERENCES users(id),
                amount DECIMAL(10, 2) NOT NULL,
                commission_rate DECIMAL(5, 2) NOT NULL,
                commission_amount DECIMAL(10, 2) NOT NULL,
                tier VARCHAR(20) NOT NULL,
                commission_type VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                paid_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                UNIQUE(payment_id, agent_id, commission_type)
            );

            CREATE INDEX IF NOT EXISTS idx_commissions_agent ON commissions(agent_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_commissions_payment ON commissions(payment_id);
            CREATE INDEX IF NOT EXISTS idx_commissions_status ON commissions(status);
        """))

        # 3. Create payouts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agent_payouts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
                amount DECIMAL(10, 2) NOT NULL,
                currency VARCHAR(3) NOT NULL DEFAULT 'USD',
                method VARCHAR(20) NOT NULL,
                destination TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                requested_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                processed_at TIMESTAMP WITH TIME ZONE,
                processed_by UUID REFERENCES users(id),
                rejection_reason TEXT,
                transaction_reference TEXT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_payouts_agent ON agent_payouts(agent_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_payouts_status ON agent_payouts(status);
        """))

        # 4. Create monthly sales tracking table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agent_monthly_sales (
                id BIGSERIAL PRIMARY KEY,
                agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
                month_year VARCHAR(7) NOT NULL,
                total_sales DECIMAL(10, 2) NOT NULL DEFAULT 0,
                total_commissions DECIMAL(10, 2) NOT NULL DEFAULT 0,
                tier_at_month_end VARCHAR(20),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                UNIQUE(agent_id, month_year)
            );

            CREATE INDEX IF NOT EXISTS idx_monthly_sales_agent ON agent_monthly_sales(agent_id, month_year DESC);
        """))

        # 5. Add agent_referred_by to users table
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS agent_referred_by VARCHAR(20);

            CREATE INDEX IF NOT EXISTS idx_users_agent_referral ON users(agent_referred_by);
        """))

        # 6. Add comments for documentation
        conn.execute(text("""
            COMMENT ON TABLE agents IS
            'Affiliate agents who refer customers and earn commissions';

            COMMENT ON TABLE commissions IS
            'Commission records for agent earnings - includes direct and override commissions';

            COMMENT ON TABLE agent_payouts IS
            'Payout requests from agents - supports mobile money and crypto';

            COMMENT ON COLUMN agents.tier IS
            'Commission tier: bronze (15%), silver (20%), gold (25%)';

            COMMENT ON COLUMN commissions.commission_type IS
            'Type: direct, override (from sub-agent), or country_manager_bonus';
        """))

        conn.commit()
        print("[MIGRATION 007] Agent system tables created")


def downgrade(engine):
    """Remove agent system tables."""

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS agent_monthly_sales CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS agent_payouts CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS commissions CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS agents CASCADE;"))
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS agent_referred_by;"))

        conn.commit()
        print("[MIGRATION 007] Agent system removed")


if __name__ == "__main__":
    # Test migration
    from app.db.database import get_engine

    engine = get_engine()
    if engine:
        print("Running migration 007...")
        upgrade(engine)
        print("Migration complete!")
    else:
        print("Could not connect to database")
