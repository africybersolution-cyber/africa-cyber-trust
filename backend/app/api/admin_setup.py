"""Temporary admin setup endpoint - DELETE AFTER USE"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid

from app.db.database import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/admin/setup-super-admin")
@router.get("/admin/setup-super-admin")
async def setup_super_admin(db: Session = Depends(get_db)):
    """
    One-time setup: Create africybersolution@gmail.com as super admin.

    WARNING: NO AUTHENTICATION REQUIRED - DELETE THIS ENDPOINT AFTER USE
    """

    email = "africybersolution@gmail.com"
    new_password = "Africyber@2024"
    name = "Roben Hakizimana"

    try:
        # Check if user exists
        result = db.execute(
            text("SELECT id, email, role FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()

        if user:
            # User exists, just update to super admin
            hashed_password = pwd_context.hash(new_password)

            db.execute(
                text("""
                    UPDATE users
                    SET role = 'SUPER_ADMIN',
                        hashed_password = :password,
                        is_active = true
                    WHERE email = :email
                """),
                {"password": hashed_password, "email": email}
            )
            db.commit()

            return {
                "success": True,
                "message": f"{email} is now a SUPER ADMIN",
                "email": email,
                "password": "Africyber@2024",
                "login_url": "http://localhost:3002",
                "note": "User already existed, upgraded to SUPER_ADMIN"
            }

        # User doesn't exist, create new
        hashed_password = pwd_context.hash(new_password)
        user_id = str(uuid.uuid4())

        db.execute(
            text("""
                INSERT INTO users (
                    id, email, name, hashed_password, role,
                    email_verified, is_active, account_type,
                    trial_status, trial_started_at, trial_ends_at,
                    created_at, updated_at
                ) VALUES (
                    :id, :email, :name, :password, 'SUPER_ADMIN',
                    true, true, 'enterprise',
                    'active', :now, :trial_end,
                    :now, :now
                )
            """),
            {
                "id": user_id,
                "email": email,
                "name": name,
                "password": hashed_password,
                "now": datetime.utcnow(),
                "trial_end": datetime.utcnow() + timedelta(days=365)  # 1 year trial
            }
        )
        db.commit()

        return {
            "success": True,
            "message": f"Created {email} as SUPER ADMIN",
            "email": email,
            "password": "Africyber@2024",
            "login_url": "http://localhost:3002",
            "note": "New account created with SUPER_ADMIN role"
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
