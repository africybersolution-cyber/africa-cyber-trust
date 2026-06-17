"""Temporary endpoint to run migration 006 - DELETE AFTER USE"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db

router = APIRouter()


@router.post("/admin/run-migration-008")
@router.get("/admin/run-migration-008")
async def run_migration_008(db: Session = Depends(get_db)):
    """
    Run migration 008 to add training system tables.

    WARNING: NO AUTHENTICATION - DELETE THIS ENDPOINT AFTER USE
    """

    try:
        # Create training_courses table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS training_courses (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(50) NOT NULL,
                difficulty VARCHAR(20) NOT NULL DEFAULT 'beginner',
                content_type VARCHAR(20) NOT NULL,
                video_url VARCHAR(500),
                document_url VARCHAR(500),
                content_html TEXT,
                duration_minutes INTEGER,
                is_required BOOLEAN NOT NULL DEFAULT false,
                is_published BOOLEAN NOT NULL DEFAULT false,
                order_index INTEGER NOT NULL DEFAULT 0,
                pass_score INTEGER,
                quiz_questions JSONB,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_by UUID REFERENCES users(id)
            );
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_training_category ON training_courses(category);
            CREATE INDEX IF NOT EXISTS idx_training_published ON training_courses(is_published);
            CREATE INDEX IF NOT EXISTS idx_training_order ON training_courses(order_index);
        """))

        # Create course_completions table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS course_completions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
                course_id UUID NOT NULL REFERENCES training_courses(id) ON DELETE CASCADE,
                status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
                progress_percent INTEGER NOT NULL DEFAULT 0,
                score INTEGER,
                started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE,
                certificate_url VARCHAR(500),
                metadata JSONB,
                UNIQUE(agent_id, course_id)
            );
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_completion_agent ON course_completions(agent_id, status);
            CREATE INDEX IF NOT EXISTS idx_completion_course ON course_completions(course_id);
        """))

        db.commit()

        return {
            "success": True,
            "message": "Migration 008 completed successfully!",
            "changes": [
                "Created training_courses table",
                "Created course_completions table",
                "Created indexes"
            ]
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/admin/run-migration-007")
@router.get("/admin/run-migration-007")
async def run_migration_007(db: Session = Depends(get_db)):
    """
    Run migration 007 to add agent system tables.

    WARNING: NO AUTHENTICATION - DELETE THIS ENDPOINT AFTER USE
    """

    try:
        # Create agents table
        db.execute(text("""
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
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);
            CREATE INDEX IF NOT EXISTS idx_agents_referral_code ON agents(referral_code);
            CREATE INDEX IF NOT EXISTS idx_agents_country ON agents(country);
            CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
            CREATE INDEX IF NOT EXISTS idx_agents_parent ON agents(parent_agent_id);
        """))

        # Create commissions table
        db.execute(text("""
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
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_commissions_agent ON commissions(agent_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_commissions_payment ON commissions(payment_id);
            CREATE INDEX IF NOT EXISTS idx_commissions_status ON commissions(status);
        """))

        # Create payouts table
        db.execute(text("""
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
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_payouts_agent ON agent_payouts(agent_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_payouts_status ON agent_payouts(status);
        """))

        # Create monthly sales table
        db.execute(text("""
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
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_monthly_sales_agent ON agent_monthly_sales(agent_id, month_year DESC);
        """))

        # Add agent_referred_by column
        db.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS agent_referred_by VARCHAR(20);
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_agent_referral ON users(agent_referred_by);
        """))

        db.commit()

        return {
            "success": True,
            "message": "Migration 007 completed successfully!",
            "changes": [
                "Created agents table",
                "Created commissions table",
                "Created agent_payouts table",
                "Created agent_monthly_sales table",
                "Added agent_referred_by column to users",
                "Created indexes"
            ]
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/admin/run-migration-006")
@router.get("/admin/run-migration-006")
async def run_migration_006(db: Session = Depends(get_db)):
    """
    Run migration 006 to add admin columns to users table.

    WARNING: NO AUTHENTICATION - DELETE THIS ENDPOINT AFTER USE
    """

    try:
        # Add columns to users table
        db.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(64);
        """))

        db.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS referred_by_code VARCHAR(20);
        """))

        db.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS granted_by_admin_id UUID REFERENCES users(id);
        """))

        # Create indexes
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users(referred_by_code);
        """))

        # Create admin_audit_logs table
        db.execute(text("""
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
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_audit_actor
                ON admin_audit_logs(actor_id, created_at DESC);
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_audit_action
                ON admin_audit_logs(action);
        """))

        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_audit_created
                ON admin_audit_logs(created_at DESC);
        """))

        db.commit()

        return {
            "success": True,
            "message": "Migration 006 completed successfully!",
            "changes": [
                "Added totp_secret column to users",
                "Added referred_by_code column to users",
                "Added granted_by_admin_id column to users",
                "Created admin_audit_logs table",
                "Created indexes"
            ]
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
