"""Admin Audit Logs - Compliance & Security Tracking

View all admin actions with filtering and search.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.db.database import get_db
from app.core.admin_deps import require_admin
from app.models.user import User
from app.models.admin_audit import AdminAuditLog


router = APIRouter(prefix="/api/admin/audit-logs", tags=["Admin - Audit"])


@router.get("/")
async def list_audit_logs(
    action: Optional[str] = None,
    actor_email: Optional[str] = None,
    target_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all admin audit logs with filtering.

    Filters:
    - action: Specific action type (create_user, grant_plan, etc.)
    - actor_email: Email of admin who performed the action
    - target_type: Type of target (user, asset, payment, etc.)
    - start_date/end_date: Date range filter

    Returns logs in reverse chronological order (newest first).
    """
    query = db.query(AdminAuditLog)

    # Apply filters
    if action:
        query = query.filter(AdminAuditLog.action == action)

    if actor_email:
        # Join with users to filter by email
        query = query.join(User, User.id == AdminAuditLog.actor_id).filter(
            User.email.ilike(f"%{actor_email}%")
        )

    if target_type:
        query = query.filter(AdminAuditLog.target_type == target_type)

    if start_date:
        query = query.filter(AdminAuditLog.created_at >= datetime.fromisoformat(start_date))

    if end_date:
        query = query.filter(AdminAuditLog.created_at <= datetime.fromisoformat(end_date))

    # Get total count
    total = query.count()

    # Apply pagination
    logs = query.order_by(AdminAuditLog.created_at.desc()).offset(skip).limit(limit).all()

    # Get actor details for each log
    results = []
    for log in logs:
        actor = db.query(User).filter(User.id == log.actor_id).first()

        results.append({
            "id": str(log.id),
            "action": log.action,
            "actor": {
                "id": str(actor.id) if actor else None,
                "email": actor.email if actor else "Unknown",
                "name": actor.name if actor else "Unknown"
            },
            "target_type": log.target_type,
            "target_id": log.target_id,
            "metadata": log.metadata,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": results
    }


@router.get("/actions")
async def list_available_actions(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all unique action types in the audit log.

    Useful for populating filter dropdowns in admin UI.
    """
    actions = db.query(AdminAuditLog.action).distinct().all()

    return {
        "actions": sorted([a[0] for a in actions if a[0]]),
        "count": len(actions)
    }


@router.get("/recent")
async def get_recent_audit_logs(
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get recent audit logs (last X hours).

    Quick view for monitoring recent admin activity.
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    logs = db.query(AdminAuditLog).filter(
        AdminAuditLog.created_at >= cutoff
    ).order_by(
        AdminAuditLog.created_at.desc()
    ).limit(100).all()

    results = []
    for log in logs:
        actor = db.query(User).filter(User.id == log.actor_id).first()

        results.append({
            "id": str(log.id),
            "action": log.action,
            "actor_email": actor.email if actor else "Unknown",
            "target_type": log.target_type,
            "target_id": log.target_id,
            "metadata": log.metadata,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })

    return {
        "period_hours": hours,
        "count": len(results),
        "logs": results
    }


@router.get("/stats")
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Audit log statistics for the specified period.

    Shows:
    - Total actions
    - Actions by type
    - Most active admins
    - Activity timeline
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Total actions
    total_actions = db.query(AdminAuditLog).filter(
        AdminAuditLog.created_at >= cutoff
    ).count()

    # Actions by type
    from sqlalchemy import func
    actions_by_type = db.query(
        AdminAuditLog.action,
        func.count(AdminAuditLog.id).label('count')
    ).filter(
        AdminAuditLog.created_at >= cutoff
    ).group_by(
        AdminAuditLog.action
    ).order_by(
        func.count(AdminAuditLog.id).desc()
    ).all()

    # Most active admins
    active_admins = db.query(
        AdminAuditLog.actor_id,
        func.count(AdminAuditLog.id).label('count')
    ).filter(
        AdminAuditLog.created_at >= cutoff
    ).group_by(
        AdminAuditLog.actor_id
    ).order_by(
        func.count(AdminAuditLog.id).desc()
    ).limit(10).all()

    # Get admin details
    admin_stats = []
    for actor_id, count in active_admins:
        actor = db.query(User).filter(User.id == actor_id).first()
        if actor:
            admin_stats.append({
                "email": actor.email,
                "name": actor.name,
                "action_count": count
            })

    return {
        "period_days": days,
        "total_actions": total_actions,
        "actions_by_type": [
            {"action": a[0], "count": a[1]}
            for a in actions_by_type
        ],
        "most_active_admins": admin_stats,
        "generated_at": datetime.utcnow().isoformat()
    }
