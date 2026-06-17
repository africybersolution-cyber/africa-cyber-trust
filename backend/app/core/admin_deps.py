"""
Admin dependencies for role-based access control and audit logging.

Usage:
    @router.get("/admin/users")
    async def list_users(admin: User = Depends(require_super_admin)):
        ...
"""
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.admin_audit import AdminAuditLog
from app.db.database import get_db


# ===== ROLE-BASED ACCESS CONTROL =====

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require user to be any admin (super_admin or platform_admin).

    Use for read-only or low-risk admin operations.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.PLATFORM_ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required. Contact support if you need elevated permissions."
        )
    return current_user


async def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require user to be super admin.

    Use for high-risk operations: grants, refunds, impersonation, user deletion.
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Super admin access required"
        )
    return current_user


async def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Check that user is active (not suspended)."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account has been suspended. Contact support."
        )
    return current_user


# ===== AUDIT LOGGING =====

async def log_admin_action(
    action: str,
    actor: User,
    db: Session,
    request: Request,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    metadata: Optional[dict] = None
) -> AdminAuditLog:
    """
    Log an admin action to the audit trail.

    Args:
        action: Action performed (e.g., "create_user", "grant_plan", "impersonate")
        actor: Admin user who performed the action
        db: Database session
        request: FastAPI request object (for IP address)
        target_type: Type of target (e.g., "user", "asset", "payment")
        target_id: ID of the target object
        metadata: Additional context data

    Returns:
        Created audit log entry

    Example:
        await log_admin_action(
            action="grant_plan",
            actor=admin,
            db=db,
            request=request,
            target_type="user",
            target_id=str(user.id),
            metadata={"plan": "professional", "duration_days": 30}
        )
    """
    # Get client IP
    ip_address = request.client.host if request else None

    # Create audit log entry
    audit_log = AdminAuditLog(
        actor_id=actor.id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata=metadata,
        ip_address=ip_address,
        created_at=datetime.utcnow()
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    print(f"[AUDIT] {action} by {actor.email} on {target_type}:{target_id}")

    return audit_log


def check_impersonation_token(current_user: User) -> bool:
    """
    Check if the current user is using an impersonation token.

    Impersonation tokens have a special claim that prevents them from:
    - Accessing admin endpoints
    - Performing privileged operations
    - Impersonating other users (no nested impersonation)

    Returns:
        True if impersonating, False otherwise
    """
    # This would check the JWT claims - implementation depends on your JWT structure
    # For now, return False (implement when adding impersonation feature)
    return False
