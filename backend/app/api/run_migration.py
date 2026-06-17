"""Temporary endpoint to run migration 006 - DELETE AFTER USE"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db

router = APIRouter()


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
