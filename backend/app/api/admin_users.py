"""Admin API - User Management

Endpoints for super admins to manage users, grant plans, and view activity.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.db.database import get_db
from app.core.admin_deps import require_super_admin, require_admin, log_admin_action
from app.models.user import User, UserRole
from app.models.subscription import Subscription
from app.services.subscription_service import SubscriptionService
from passlib.context import CryptContext


router = APIRouter(prefix="/api/admin/users", tags=["Admin - Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ===== REQUEST/RESPONSE MODELS =====

class CreateUserRequest(BaseModel):
    """Request to create a new user manually."""
    email: EmailStr
    name: str
    password: str
    role: str = "customer"  # customer, agent, support_admin, super_admin
    account_type: str = "starter"  # starter, professional, enterprise
    grant_plan: bool = False  # If true, grant a subscription immediately
    plan_duration_days: Optional[int] = 30
    company_name: Optional[str] = None


class GrantPlanRequest(BaseModel):
    """Request to grant a subscription plan to a user."""
    plan_name: str  # starter, professional, enterprise
    duration_days: int = 30
    reason: str  # Why this grant was made (for audit)
    custom_price: Optional[float] = None
    currency: Optional[str] = "USD"


class UpdateUserStatusRequest(BaseModel):
    """Request to activate/suspend a user."""
    is_active: bool
    reason: str


class UserResponse(BaseModel):
    """User details for admin view."""
    id: str
    email: str
    name: str
    role: str
    account_type: str
    is_active: bool
    email_verified: bool
    trial_status: Optional[str]
    trial_ends_at: Optional[str]
    last_login_at: Optional[str]
    created_at: str
    company_id: Optional[str]
    referred_by_code: Optional[str]
    granted_by_admin_id: Optional[str]


# ===== ENDPOINTS =====

@router.post("/", status_code=201)
async def create_user(
    request: CreateUserRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new user manually (bypassing signup flow).

    Use cases:
    - Partner/negotiated deals
    - Testing accounts
    - Manual migrations
    - Special arrangements

    All actions are audited.
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"User with email {request.email} already exists")

    # Validate role
    try:
        user_role = UserRole[request.role.upper()] if hasattr(UserRole, request.role.upper()) else UserRole.NORMAL_USER
    except:
        user_role = UserRole.NORMAL_USER

    # Hash password
    hashed_password = pwd_context.hash(request.password)

    # Create company if provided
    company_id = None
    if request.company_name:
        from app.models.company import Company
        company = Company(
            name=request.company_name,
            created_at=datetime.utcnow()
        )
        db.add(company)
        db.flush()  # Get company ID
        company_id = company.id

    # Create user
    user = User(
        email=request.email,
        name=request.name,
        hashed_password=hashed_password,
        role=user_role,
        account_type=request.account_type,
        is_active=True,
        email_verified=True,  # Auto-verify for manually created users
        company_id=company_id,
        granted_by_admin_id=admin.id,  # Track who created this user
        created_at=datetime.utcnow()
    )

    db.add(user)
    db.flush()  # Get user ID for subscription

    # Grant plan if requested
    subscription_id = None
    if request.grant_plan:
        subscription = SubscriptionService.create_subscription(
            db=db,
            user_id=user.id,
            plan_name=request.account_type,
            duration_days=request.plan_duration_days or 30
        )
        subscription_id = subscription.id

    db.commit()
    db.refresh(user)

    # Audit log
    await log_admin_action(
        action="create_user",
        actor=admin,
        db=db,
        request=req,
        target_type="user",
        target_id=str(user.id),
        metadata={
            "email": user.email,
            "role": request.role,
            "account_type": request.account_type,
            "granted_plan": request.grant_plan,
            "subscription_id": str(subscription_id) if subscription_id else None
        }
    )

    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "account_type": user.account_type,
        "message": "User created successfully" + (" with subscription" if request.grant_plan else "")
    }


@router.post("/{user_id}/grant-plan")
async def grant_plan(
    user_id: str,
    request: GrantPlanRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Grant a subscription plan to a user without payment.

    Use cases:
    - Negotiated deals
    - Partner arrangements
    - Refund compensation
    - Marketing promotions

    Creates a subscription with `granted_by_admin_id` set.
    """
    # Get user
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate plan name
    if request.plan_name not in ["starter", "professional", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid plan name")

    # Create subscription
    subscription = SubscriptionService.create_subscription(
        db=db,
        user_id=user.id,
        plan_name=request.plan_name,
        duration_days=request.duration_days
    )

    # Update user account type
    user.account_type = request.plan_name
    user.granted_by_admin_id = admin.id

    db.commit()
    db.refresh(subscription)

    # Audit log
    await log_admin_action(
        action="grant_plan",
        actor=admin,
        db=db,
        request=req,
        target_type="user",
        target_id=str(user.id),
        metadata={
            "plan_name": request.plan_name,
            "duration_days": request.duration_days,
            "reason": request.reason,
            "custom_price": request.custom_price,
            "subscription_id": str(subscription.id)
        }
    )

    return {
        "user_id": str(user.id),
        "subscription_id": str(subscription.id),
        "plan_name": request.plan_name,
        "expires_at": subscription.expires_at.isoformat(),
        "message": "Plan granted successfully"
    }


@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: str,
    request: UpdateUserStatusRequest,
    req: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Activate or suspend a user account.

    Suspended users cannot login or access the platform.
    """
    # Get user
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent admins from suspending other admins
    if user.role in [UserRole.SUPER_ADMIN, UserRole.PLATFORM_ADMIN]:
        raise HTTPException(status_code=403, detail="Cannot suspend admin users")

    # Update status
    old_status = user.is_active
    user.is_active = request.is_active

    db.commit()

    # Audit log
    await log_admin_action(
        action="update_user_status",
        actor=admin,
        db=db,
        request=req,
        target_type="user",
        target_id=str(user.id),
        metadata={
            "old_status": old_status,
            "new_status": request.is_active,
            "reason": request.reason
        }
    )

    return {
        "user_id": str(user.id),
        "is_active": user.is_active,
        "message": f"User {'activated' if request.is_active else 'suspended'} successfully"
    }


@router.get("/")
async def list_users(
    email: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filters.

    Supports pagination and filtering by email, role, and status.
    """
    query = db.query(User)

    # Apply filters
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))

    if role:
        try:
            user_role = UserRole[role.upper()]
            query = query.filter(User.role == user_role)
        except:
            pass  # Invalid role, ignore filter

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "name": u.name,
                "role": u.role.value,
                "account_type": u.account_type,
                "is_active": u.is_active,
                "trial_status": u.trial_status,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None
            }
            for u in users
        ]
    }


@router.get("/{user_id}")
async def get_user_details(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific user.

    Includes subscription, company, and activity details.
    """
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get active subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == "active"
    ).first()

    # Get company if exists
    company = None
    if user.company_id:
        from app.models.company import Company
        company = db.query(Company).filter(Company.id == user.company_id).first()

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "account_type": user.account_type,
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "trial_status": user.trial_status,
        "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "company": {
            "id": str(company.id),
            "name": company.name
        } if company else None,
        "subscription": {
            "id": str(subscription.id),
            "plan_name": subscription.plan_name,
            "status": subscription.status,
            "expires_at": subscription.expires_at.isoformat()
        } if subscription else None,
        "referred_by_code": user.referred_by_code,
        "granted_by_admin_id": str(user.granted_by_admin_id) if user.granted_by_admin_id else None
    }
