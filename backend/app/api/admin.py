"""Admin endpoints for manual access grants."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.subscription import Subscription, ManualAccessGrant
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Middleware to check if user is admin."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


class GrantAccessRequest(BaseModel):
    user_email: str
    plan_name: str  # 'personal' or 'business'
    duration_days: int  # How many days
    custom_price: float = None  # Optional custom price
    currency: str = None
    reason: str
    notes: str = None


@router.post("/grant-access")
async def grant_manual_access(
    request: GrantAccessRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin grants manual subscription access to a user."""

    # Find user by email
    user = db.query(User).filter(User.email == request.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user already has active subscription
    existing = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == 'active'
    ).first()

    if existing:
        # Extend existing subscription
        existing.expires_at = existing.expires_at + timedelta(days=request.duration_days)
        existing.manual_grant = True
        existing.granted_by = admin.email
        existing.grant_reason = request.reason

        if request.custom_price:
            existing.custom_price = request.custom_price
            existing.custom_currency = request.currency or 'RWF'

        subscription = existing
    else:
        # Create new subscription
        subscription = Subscription(
            user_id=user.id,
            plan_name=request.plan_name,
            status='active',
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=request.duration_days),
            manual_grant=True,
            granted_by=admin.email,
            grant_reason=request.reason,
            custom_price=request.custom_price,
            custom_currency=request.currency or 'RWF'
        )
        db.add(subscription)

    # Log the grant
    grant_log = ManualAccessGrant(
        user_id=user.id,
        admin_email=admin.email,
        plan_name=request.plan_name,
        duration_days=request.duration_days,
        custom_price=request.custom_price,
        currency=request.currency,
        reason=request.reason,
        notes=request.notes
    )
    db.add(grant_log)

    # Reset trial status if applicable
    user.trial_status = 'converted'

    db.commit()
    db.refresh(subscription)

    return {
        "message": "Access granted successfully",
        "user_email": user.email,
        "plan": request.plan_name,
        "expires_at": subscription.expires_at.isoformat(),
        "custom_price": request.custom_price,
        "subscription_id": str(subscription.id)
    }


@router.get("/users/search")
async def search_users(
    query: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Search users by email or name."""
    users = db.query(User).filter(
        (User.email.ilike(f"%{query}%")) |
        (User.name.ilike(f"%{query}%"))
    ).limit(20).all()

    return [
        {
            "id": str(u.id),
            "email": u.email,
            "name": u.name,
            "account_type": u.account_type,
            "trial_status": u.trial_status,
            "trial_ends_at": u.trial_ends_at.isoformat() if u.trial_ends_at else None,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]


@router.get("/grants/history")
async def get_grant_history(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get history of manual access grants."""
    grants = db.query(ManualAccessGrant).order_by(
        ManualAccessGrant.created_at.desc()
    ).limit(100).all()

    result = []
    for grant in grants:
        user = db.query(User).get(grant.user_id)
        result.append({
            "id": str(grant.id),
            "user_email": user.email if user else "Unknown",
            "user_name": user.name if user else "Unknown",
            "admin_email": grant.admin_email,
            "plan_name": grant.plan_name,
            "duration_days": grant.duration_days,
            "custom_price": float(grant.custom_price) if grant.custom_price else None,
            "currency": grant.currency,
            "reason": grant.reason,
            "notes": grant.notes,
            "granted_at": grant.created_at.isoformat()
        })

    return result


@router.delete("/revoke-access/{user_id}")
async def revoke_access(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Revoke user's subscription access."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == uuid.UUID(user_id),
        Subscription.status == 'active'
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")

    subscription.status = 'cancelled'
    subscription.expires_at = datetime.utcnow()

    db.commit()

    return {"message": "Access revoked successfully"}


@router.get("/stats")
async def get_admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard stats."""
    total_users = db.query(User).count()
    active_trials = db.query(User).filter(
        User.trial_status == 'active',
        User.trial_ends_at > datetime.utcnow()
    ).count()
    active_subscriptions = db.query(Subscription).filter(
        Subscription.status == 'active',
        Subscription.expires_at > datetime.utcnow()
    ).count()
    manual_grants = db.query(Subscription).filter(
        Subscription.manual_grant == True,
        Subscription.status == 'active'
    ).count()

    return {
        "total_users": total_users,
        "active_trials": active_trials,
        "active_subscriptions": active_subscriptions,
        "manual_grants": manual_grants
    }
