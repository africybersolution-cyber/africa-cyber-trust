"""Admin Analytics - Revenue, Users, System Metrics

Real-time analytics dashboard for super admins.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from datetime import datetime, timedelta
from typing import Optional, List
import json

from app.db.database import get_db
from app.core.admin_deps import require_admin
from app.models.user import User, UserRole
from app.models.subscription import Subscription, Payment
from app.models.asset import Asset
from app.models.scan import Scan, Finding


router = APIRouter(prefix="/api/admin/analytics", tags=["Admin - Analytics"])


@router.get("/live-metrics")
async def get_live_metrics(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Real-time platform metrics for admin dashboard.

    Shows current state of the platform at a glance.
    """
    # User counts - Count ALL users (including admins, agents, etc)
    # Exclude only system accounts if needed
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    # Subscription counts - Use account_type field (starter, professional, enterprise)
    # Many users have account_type instead of Subscription records during trial
    starter_count = db.query(User).filter(
        User.account_type == "starter",
        User.is_active == True
    ).count()

    professional_count = db.query(User).filter(
        User.account_type == "professional",
        User.is_active == True
    ).count()

    enterprise_count = db.query(User).filter(
        User.account_type == "enterprise",
        User.is_active == True
    ).count()

    active_subs = starter_count + professional_count + enterprise_count

    # Trial users - users with trial_status = 'active'
    trial_users = db.query(User).filter(
        User.trial_status == "active",
        User.is_active == True
    ).count()

    # Revenue (completed payments only)
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "completed"
    ).scalar() or 0

    # This month's revenue
    first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "completed",
        Payment.paid_at >= first_of_month
    ).scalar() or 0

    # MRR calculation based on account_type (already counted above)
    # Calculate MRR based on current pricing
    mrr = (starter_count * 15) + (professional_count * 79) + (enterprise_count * 299)

    # Asset & scan metrics
    total_assets = db.query(Asset).count()
    total_scans = db.query(Scan).count()

    # Findings count - wrap in try/except for missing columns
    try:
        total_findings = db.query(Finding).count()
        critical_findings = db.query(Finding).filter(
            Finding.severity == "critical",
            Finding.resolved == False
        ).count()
    except Exception as e:
        print(f"[WARNING] Failed to query findings (missing columns): {e}")
        total_findings = 0
        critical_findings = 0

    # Recent signups (last 7 days) - Count ALL new users
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_signups = db.query(User).filter(
        User.created_at >= week_ago
    ).count()

    # Payment method breakdown
    momo_payments = db.query(Payment).filter(
        Payment.status == "completed",
        Payment.payment_method == "mobile_money"
    ).count()

    crypto_payments = db.query(Payment).filter(
        Payment.status == "completed",
        Payment.payment_method == "crypto"
    ).count()

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "trial": trial_users,
            "recent_signups_7d": recent_signups
        },
        "revenue": {
            "total_all_time": float(total_revenue),
            "this_month": float(monthly_revenue),
            "mrr": float(mrr),
            "currency": "USD"
        },
        "subscriptions": {
            "active": active_subs,
            "starter": starter_count,
            "professional": professional_count,
            "enterprise": enterprise_count
        },
        "platform": {
            "total_assets": total_assets,
            "total_scans": total_scans,
            "total_findings": total_findings,
            "critical_findings": critical_findings
        },
        "payments": {
            "mobile_money": momo_payments,
            "crypto": crypto_payments,
            "total": momo_payments + crypto_payments
        },
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/revenue")
async def get_revenue_analytics(
    group_by: str = Query("month", regex="^(day|month|country|plan|method)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Revenue analytics with grouping options.

    Group by:
    - day: Daily revenue
    - month: Monthly revenue
    - country: Revenue by country
    - plan: Revenue by plan type
    - method: Revenue by payment method (mobile money vs crypto)
    """
    query = db.query(Payment).filter(Payment.status == "completed")

    # Apply date filters
    if start_date:
        query = query.filter(Payment.paid_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Payment.paid_at <= datetime.fromisoformat(end_date))

    results = []

    if group_by == "country":
        # Group by country
        country_revenue = db.query(
            Payment.country,
            func.sum(Payment.amount).label("total"),
            func.count(Payment.id).label("count")
        ).filter(
            Payment.status == "completed"
        ).group_by(Payment.country).all()

        results = [
            {
                "country": r.country or "Unknown",
                "total": float(r.total or 0),
                "count": r.count
            }
            for r in country_revenue
        ]

    elif group_by == "plan":
        # Group by subscription plan
        # Need to join with subscriptions or infer from amount
        plan_revenue = db.query(
            func.count(Payment.id).label("count"),
            func.sum(Payment.amount).label("total")
        ).filter(Payment.status == "completed").all()

        # Simplified grouping by amount ranges
        starter_payments = query.filter(Payment.amount <= 20).all()
        professional_payments = query.filter(Payment.amount > 20, Payment.amount <= 150).all()
        enterprise_payments = query.filter(Payment.amount > 150).all()

        results = [
            {
                "plan": "starter",
                "total": sum(p.amount for p in starter_payments),
                "count": len(starter_payments)
            },
            {
                "plan": "professional",
                "total": sum(p.amount for p in professional_payments),
                "count": len(professional_payments)
            },
            {
                "plan": "enterprise",
                "total": sum(p.amount for p in enterprise_payments),
                "count": len(enterprise_payments)
            }
        ]

    elif group_by == "method":
        # Group by payment method
        method_revenue = db.query(
            Payment.payment_method,
            func.sum(Payment.amount).label("total"),
            func.count(Payment.id).label("count")
        ).filter(
            Payment.status == "completed"
        ).group_by(Payment.payment_method).all()

        results = [
            {
                "method": r.payment_method or "Unknown",
                "total": float(r.total or 0),
                "count": r.count
            }
            for r in method_revenue
        ]

    elif group_by == "month":
        # Group by month
        monthly_revenue = db.query(
            func.date_trunc('month', Payment.paid_at).label('month'),
            func.sum(Payment.amount).label("total"),
            func.count(Payment.id).label("count")
        ).filter(
            Payment.status == "completed"
        ).group_by(func.date_trunc('month', Payment.paid_at)).order_by('month').all()

        results = [
            {
                "month": r.month.strftime("%Y-%m") if r.month else "Unknown",
                "total": float(r.total or 0),
                "count": r.count
            }
            for r in monthly_revenue
        ]

    return {
        "group_by": group_by,
        "results": results,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/user-growth")
async def get_user_growth(
    period: str = Query("month", regex="^(day|week|month)$"),
    limit: int = Query(12, ge=1, le=90),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    User growth over time (signups, conversions, churn).
    """
    # Calculate date range
    if period == "day":
        trunc = 'day'
        limit = min(limit, 90)  # Max 90 days
    elif period == "week":
        trunc = 'week'
        limit = min(limit, 52)  # Max 52 weeks
    else:  # month
        trunc = 'month'
        limit = min(limit, 24)  # Max 24 months

    # Signups over time
    signups = db.query(
        func.date_trunc(trunc, User.created_at).label('period'),
        func.count(User.id).label("count")
    ).filter(
        User.role == UserRole.NORMAL_USER
    ).group_by(func.date_trunc(trunc, User.created_at)).order_by('period').limit(limit).all()

    # Trial conversions over time
    conversions = db.query(
        func.date_trunc(trunc, User.created_at).label('period'),
        func.count(User.id).label("count")
    ).filter(
        User.trial_status == "converted"
    ).group_by(func.date_trunc(trunc, User.created_at)).order_by('period').limit(limit).all()

    return {
        "period": period,
        "signups": [
            {
                "period": r.period.strftime("%Y-%m-%d" if period == "day" else "%Y-%m"),
                "count": r.count
            }
            for r in signups
        ],
        "conversions": [
            {
                "period": r.period.strftime("%Y-%m-%d" if period == "day" else "%Y-%m"),
                "count": r.count
            }
            for r in conversions
        ],
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/top-customers")
async def get_top_customers(
    limit: int = Query(10, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Top customers by total spend.

    Useful for identifying VIP customers and potential enterprise leads.
    """
    # Get users with their total spending
    top_spenders = db.query(
        User.id,
        User.email,
        User.name,
        User.account_type,
        func.sum(Payment.amount).label("total_spent"),
        func.count(Payment.id).label("payment_count")
    ).join(
        Payment, Payment.user_id == User.id
    ).filter(
        Payment.status == "completed"
    ).group_by(
        User.id, User.email, User.name, User.account_type
    ).order_by(
        func.sum(Payment.amount).desc()
    ).limit(limit).all()

    return {
        "top_customers": [
            {
                "user_id": str(r.id),
                "email": r.email,
                "name": r.name,
                "account_type": r.account_type,
                "total_spent": float(r.total_spent or 0),
                "payment_count": r.payment_count
            }
            for r in top_spenders
        ],
        "generated_at": datetime.utcnow().isoformat()
    }
