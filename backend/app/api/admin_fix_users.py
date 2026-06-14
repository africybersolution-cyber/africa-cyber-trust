"""Admin endpoint to fix existing users - Give them STARTER trial"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone, timedelta

from app.db.database import get_db
from app.models.user import User

router = APIRouter()


@router.post("/admin/fix-users")
@router.get("/admin/fix-users")
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
        # Count users needing update (both NULL trial AND old "personal" type)
        count_result = db.execute(text("""
            SELECT COUNT(*) FROM users
            WHERE trial_started_at IS NULL OR account_type = 'personal'
        """))
        count = count_result.fetchone()[0]

        if count == 0:
            return {
                "success": True,
                "message": "All users already have trials activated!",
                "updated_count": 0,
                "users": []
            }

        # Update users (both NULL trial AND old "personal" type)
        db.execute(text("""
            UPDATE users
            SET
                account_type = 'starter',
                trial_started_at = COALESCE(trial_started_at, NOW()),
                trial_ends_at = COALESCE(trial_ends_at, NOW() + INTERVAL '14 days'),
                trial_status = COALESCE(trial_status, 'active'),
                updated_at = NOW()
            WHERE trial_started_at IS NULL OR account_type = 'personal'
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


@router.post("/admin/create-companies")
@router.get("/admin/create-companies")
async def create_companies_for_users(db: Session = Depends(get_db)):
    """
    Create personal companies for users without company_id.

    **No authentication required for initial setup**
    """

    try:
        from app.models.user import User
        from app.models.company import Company
        from sqlalchemy import text

        # Find users without company
        result = db.execute(text("""
            SELECT id, name, email FROM users WHERE company_id IS NULL
        """))

        users_without_company = result.fetchall()

        if len(users_without_company) == 0:
            return {
                "success": True,
                "message": "All users already have companies!",
                "created_count": 0
            }

        created_companies = []

        for user_row in users_without_company:
            user_id, user_name, user_email = user_row

            # Create personal company
            company = Company(
                name=f"{user_name}'s Account",
                country="Unknown",
                plan_id="free",
                is_active=True
            )
            db.add(company)
            db.flush()

            # Update user with company_id
            db.execute(text("""
                UPDATE users SET company_id = :company_id WHERE id = :user_id
            """), {"company_id": company.id, "user_id": user_id})

            created_companies.append({
                "user_email": user_email,
                "company_name": company.name,
                "company_id": str(company.id)
            })

        db.commit()

        return {
            "success": True,
            "message": f"Created {len(created_companies)} companies!",
            "created_count": len(created_companies),
            "companies": created_companies
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create companies: {str(e)}"
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
