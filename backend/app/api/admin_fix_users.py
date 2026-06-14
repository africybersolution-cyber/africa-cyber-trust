"""Admin endpoint to fix existing users - Give them STARTER trial"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone, timedelta

from app.db.database import get_db
from app.models.user import User

router = APIRouter()


@router.post("/admin/fix-users")
async def fix_existing_users(db: Session = Depends(get_db)):
    """
    Fix all existing users without trial - Give them STARTER trial.

    This endpoint:
    1. Finds all users without trial_started_at
    2. Sets account_type='starter'
    3. Activates 14-day trial
    4. Returns list of updated users

    **No authentication required for initial setup - REMOVE AFTER FIRST USE**
    """

    try:
        # Count users needing update
        count_result = db.execute(text("""
            SELECT COUNT(*) FROM users WHERE trial_started_at IS NULL
        """))
        count = count_result.fetchone()[0]

        if count == 0:
            return {
                "success": True,
                "message": "All users already have trials activated!",
                "updated_count": 0,
                "users": []
            }

        # Update users
        db.execute(text("""
            UPDATE users
            SET
                account_type = 'starter',
                trial_started_at = NOW(),
                trial_ends_at = NOW() + INTERVAL '14 days',
                trial_status = 'active',
                updated_at = NOW()
            WHERE trial_started_at IS NULL
        """))

        db.commit()

        # Get updated users
        result = db.execute(text("""
            SELECT
                email,
                name,
                account_type,
                trial_status,
                trial_ends_at AT TIME ZONE 'UTC' as trial_ends
            FROM users
            WHERE account_type = 'starter'
            ORDER BY trial_started_at DESC
        """))

        updated_users = []
        for row in result.fetchall():
            updated_users.append({
                "email": row[0],
                "name": row[1],
                "account_type": row[2],
                "trial_status": row[3],
                "trial_ends_at": str(row[4]) if row[4] else None
            })

        return {
            "success": True,
            "message": f"Successfully updated {count} users to STARTER tier!",
            "updated_count": count,
            "users": updated_users
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update users: {str(e)}"
        )


@router.get("/admin/check-users")
async def check_users_status(db: Session = Depends(get_db)):
    """
    Check status of all users.

    **No authentication required for initial setup**
    """

    try:
        # Get all users
        result = db.execute(text("""
            SELECT
                email,
                name,
                role,
                account_type,
                trial_status,
                trial_started_at,
                trial_ends_at AT TIME ZONE 'UTC' as trial_ends
            FROM users
            ORDER BY created_at DESC
        """))

        users = []
        users_without_trial = 0
        users_with_trial = 0

        for row in result.fetchall():
            user_data = {
                "email": row[0],
                "name": row[1],
                "role": row[2],
                "account_type": row[3],
                "trial_status": row[4],
                "trial_started_at": str(row[5]) if row[5] else None,
                "trial_ends_at": str(row[6]) if row[6] else None
            }
            users.append(user_data)

            if row[5] is None:  # trial_started_at is NULL
                users_without_trial += 1
            else:
                users_with_trial += 1

        return {
            "success": True,
            "total_users": len(users),
            "users_with_trial": users_with_trial,
            "users_without_trial": users_without_trial,
            "users": users
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check users: {str(e)}"
        )
