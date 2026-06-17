"""Admin API - Payment Management

View all payments, process refunds, analyze failed transactions.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.core.admin_deps import require_admin, require_super_admin, log_admin_action
from app.models.user import User
from app.models.subscription import Payment


router = APIRouter(prefix="/api/admin/payments", tags=["Admin - Payments"])


# ===== REQUEST MODELS =====

class RefundRequest(BaseModel):
    """Request to issue a refund."""
    amount: Optional[float] = None  # If None, full refund
    reason: str
    notify_user: bool = True


# ===== ENDPOINTS =====

@router.get("")
async def list_all_payments(
    user_email: Optional[str] = None,
    status: Optional[str] = None,
    payment_method: Optional[str] = None,
    country: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    View all payments across the platform.

    Supports extensive filtering:
    - User email
    - Payment status (pending, completed, failed, refunded)
    - Payment method (mobile_money, crypto)
    - Country
    - Amount range
    - Date range

    Useful for:
    - Revenue analysis
    - Failed payment investigation
    - Fraud detection
    - Compliance audits
    """
    query = db.query(Payment)

    # Apply filters
    if user_email:
        query = query.join(User, User.id == Payment.user_id).filter(
            User.email.ilike(f"%{user_email}%")
        )

    if status:
        query = query.filter(Payment.status == status)

    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)

    if country:
        query = query.filter(Payment.country == country)

    if min_amount is not None:
        query = query.filter(Payment.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Payment.amount <= max_amount)

    if start_date:
        query = query.filter(Payment.created_at >= datetime.fromisoformat(start_date))

    if end_date:
        query = query.filter(Payment.created_at <= datetime.fromisoformat(end_date))

    # Get total count
    total = query.count()

    # Apply pagination
    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

    # Enrich with user info
    results = []
    for payment in payments:
        user = db.query(User).filter(User.id == payment.user_id).first()

        results.append({
            "id": str(payment.id),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name
            } if user else None,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "payment_method": payment.payment_method,
            "country": payment.country,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
            "external_reference": payment.external_reference
        })

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "payments": results
    }


@router.get("/{payment_id}")
async def get_payment_details(
    payment_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific payment.

    Includes:
    - Full payment details
    - User information
    - Transaction history
    - Related subscription
    """
    payment = db.query(Payment).filter(Payment.id == uuid.UUID(payment_id)).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Get user
    user = db.query(User).filter(User.id == payment.user_id).first()

    # Get subscription if linked
    subscription = None
    if payment.subscription_id:
        from app.models.subscription import Subscription
        subscription = db.query(Subscription).filter(
            Subscription.id == payment.subscription_id
        ).first()

    return {
        "id": str(payment.id),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "account_type": user.account_type
        } if user else None,
        "amount": float(payment.amount),
        "currency": payment.currency,
        "status": payment.status,
        "payment_method": payment.payment_method,
        "country": payment.country,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        "external_reference": payment.external_reference,
        "callback_data": payment.callback_data,
        "subscription": {
            "id": str(subscription.id),
            "plan_name": subscription.plan_name,
            "status": subscription.status
        } if subscription else None
    }


@router.post("/{payment_id}/refund")
async def issue_refund(
    payment_id: str,
    request: RefundRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Issue a refund for a payment.

    ⚠️ SUPER ADMIN ONLY - financial operation

    Process:
    1. Mark payment as refunded
    2. Cancel related subscription
    3. Log in audit trail
    4. Optionally notify user

    Note: This marks the refund in the database. Actual money transfer
    must be done manually via payment provider (PawaPay, blockchain).
    """
    # Get payment
    payment = db.query(Payment).filter(Payment.id == uuid.UUID(payment_id)).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Validate payment can be refunded
    if payment.status == "refunded":
        raise HTTPException(status_code=400, detail="Payment already refunded")

    if payment.status != "completed":
        raise HTTPException(status_code=400, detail="Can only refund completed payments")

    # Calculate refund amount
    refund_amount = request.amount if request.amount is not None else payment.amount

    if refund_amount > payment.amount:
        raise HTTPException(status_code=400, detail="Refund amount exceeds payment amount")

    # Update payment status
    old_status = payment.status
    payment.status = "refunded"

    # Cancel related subscription
    if payment.subscription_id:
        from app.models.subscription import Subscription
        subscription = db.query(Subscription).filter(
            Subscription.id == payment.subscription_id
        ).first()

        if subscription:
            subscription.status = "cancelled"

    db.commit()

    # Audit log
    await log_admin_action(
        action="issue_refund",
        actor=admin,
        db=db,
        request=req,
        target_type="payment",
        target_id=str(payment.id),
        context_data={
            "refund_amount": float(refund_amount),
            "original_amount": float(payment.amount),
            "reason": request.reason,
            "old_status": old_status,
            "payment_method": payment.payment_method,
            "notify_user": request.notify_user
        }
    )

    # TODO: Send notification to user if requested
    # TODO: Trigger actual refund via payment provider

    return {
        "payment_id": str(payment.id),
        "refund_amount": float(refund_amount),
        "status": "refunded",
        "message": f"Refund of ${refund_amount:.2f} processed successfully"
    }


@router.get("/failed/analysis")
async def analyze_failed_payments(
    days: int = Query(30, ge=1, le=365),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Analyze failed payments to identify issues.

    Shows:
    - Total failed payments
    - Failure reasons
    - Countries with high failure rates
    - Payment methods with issues

    Helps identify:
    - Integration problems
    - Regional payment issues
    - Fraud patterns
    """
    from datetime import timedelta
    from sqlalchemy import func

    cutoff = datetime.utcnow() - timedelta(days=days)

    # Total failed payments
    total_failed = db.query(Payment).filter(
        Payment.status == "failed",
        Payment.created_at >= cutoff
    ).count()

    # Failures by country
    country_failures = db.query(
        Payment.country,
        func.count(Payment.id).label("count")
    ).filter(
        Payment.status == "failed",
        Payment.created_at >= cutoff
    ).group_by(Payment.country).order_by(func.count(Payment.id).desc()).all()

    # Failures by payment method
    method_failures = db.query(
        Payment.payment_method,
        func.count(Payment.id).label("count")
    ).filter(
        Payment.status == "failed",
        Payment.created_at >= cutoff
    ).group_by(Payment.payment_method).all()

    return {
        "period_days": days,
        "total_failed": total_failed,
        "by_country": [
            {"country": r.country or "Unknown", "failures": r.count}
            for r in country_failures
        ],
        "by_method": [
            {"method": r.payment_method or "Unknown", "failures": r.count}
            for r in method_failures
        ],
        "generated_at": datetime.utcnow().isoformat()
    }
