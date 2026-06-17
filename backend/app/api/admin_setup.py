"""Temporary admin setup endpoint - DELETE AFTER USE"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext

from app.db.database import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/admin/setup-super-admin")
@router.get("/admin/setup-super-admin")
async def setup_super_admin(db: Session = Depends(get_db)):
    """
    One-time setup: Make africybersolution@gmail.com a super admin.

    WARNING: NO AUTHENTICATION REQUIRED - DELETE THIS ENDPOINT AFTER USE
    """

    email = "africybersolution@gmail.com"
    new_password = "Africyber@2024"

    try:
        # Check if user exists
        result = db.execute(
            text("SELECT id, email, role FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()

        if not user:
            return {
                "success": False,
                "message": f"User {email} not found. Please sign up first."
            }

        # Hash password
        hashed_password = pwd_context.hash(new_password)

        # Update user to super admin with new password
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
            "note": "DELETE THIS ENDPOINT IMMEDIATELY AFTER USE"
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
