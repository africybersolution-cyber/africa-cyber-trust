"""Admin API - Agent Management"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.core.admin_deps import require_admin, require_super_admin, log_admin_action
from app.models.user import User
from app.models.agent import Agent, Commission, AgentPayout
from app.services.agent_service import AgentService
from app.services.whatsapp_service import whatsapp_service


router = APIRouter(prefix="/api/admin/agents", tags=["Admin - Agents"])


# ===== REQUEST MODELS =====

class ApproveAgentRequest(BaseModel):
    """Approve agent application."""
    grant_demo_scans: int = 5


class RejectAgentRequest(BaseModel):
    """Reject agent application."""
    reason: str


class ProcessPayoutRequest(BaseModel):
    """Process payout request."""
    action: str  # approve, reject
    transaction_reference: Optional[str] = None
    rejection_reason: Optional[str] = None


class SetCountryManagerRequest(BaseModel):
    """Assign agent as country manager."""
    country: str


# ===== LEADERBOARD =====

@router.get("/leaderboard")
async def get_agent_leaderboard(
    period: str = Query("all_time", regex="^(all_time|this_month|this_week)$"),
    metric: str = Query("sales", regex="^(sales|commissions)$"),
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get agent leaderboard rankings.

    Periods: all_time, this_month, this_week
    Metrics: sales, commissions
    """
    from datetime import datetime, timedelta

    # Base query - only approved agents
    query = db.query(Agent).filter(Agent.status == "approved")

    # Apply period filter
    if period == "this_month":
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Use monthly_sales for this month
        if metric == "sales":
            query = query.order_by(Agent.monthly_sales.desc())
        else:
            # Get commissions this month
            query = query.join(Commission, Commission.agent_id == Agent.id).filter(
                Commission.created_at >= month_start
            ).group_by(Agent.id).order_by(
                func.sum(Commission.commission_amount).desc()
            )
    elif period == "this_week":
        week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        if metric == "sales":
            # No weekly sales tracking - use monthly as proxy
            query = query.order_by(Agent.monthly_sales.desc())
        else:
            # Get commissions this week
            query = query.join(Commission, Commission.agent_id == Agent.id).filter(
                Commission.created_at >= week_start
            ).group_by(Agent.id).order_by(
                func.sum(Commission.commission_amount).desc()
            )
    else:  # all_time
        if metric == "sales":
            query = query.order_by(Agent.total_sales.desc())
        else:
            query = query.order_by(Agent.total_commissions.desc())

    # Get top agents
    agents = query.limit(limit).all()

    # Build leaderboard
    leaderboard = []
    for idx, agent in enumerate(agents, start=1):
        user = db.query(User).filter(User.id == agent.user_id).first()
        stats = AgentService.get_agent_stats(db, agent.id)

        # Calculate metric value based on period
        if period == "this_month":
            if metric == "sales":
                metric_value = float(agent.monthly_sales or 0)
            else:
                month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                month_commissions = db.query(func.sum(Commission.commission_amount)).filter(
                    Commission.agent_id == agent.id,
                    Commission.created_at >= month_start
                ).scalar() or 0
                metric_value = float(month_commissions)
        elif period == "this_week":
            week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

            if metric == "sales":
                # Approximate weekly sales (monthly / 4)
                metric_value = float(agent.monthly_sales or 0) / 4
            else:
                week_commissions = db.query(func.sum(Commission.commission_amount)).filter(
                    Commission.agent_id == agent.id,
                    Commission.created_at >= week_start
                ).scalar() or 0
                metric_value = float(week_commissions)
        else:  # all_time
            if metric == "sales":
                metric_value = float(agent.total_sales or 0)
            else:
                metric_value = float(agent.total_commissions or 0)

        leaderboard.append({
            "rank": idx,
            "agent": {
                "id": str(agent.id),
                "referral_code": agent.referral_code,
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email
                } if user else None,
                "country": agent.country,
                "tier": agent.tier,
                "is_country_manager": agent.is_country_manager
            },
            "metric_value": metric_value,
            "total_sales": float(agent.total_sales or 0),
            "total_commissions": float(agent.total_commissions or 0),
            "total_customers": stats.get("total_customers", 0),
            "sub_agents": stats.get("sub_agents", 0)
        })

    return {
        "period": period,
        "metric": metric,
        "total": len(leaderboard),
        "leaderboard": leaderboard
    }


# ===== ENDPOINTS =====

@router.get("/")
async def list_agents(
    status: Optional[str] = None,
    country: Optional[str] = None,
    tier: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all agents with filtering.

    Filters: status, country, tier
    """
    query = db.query(Agent)

    if status:
        query = query.filter(Agent.status == status)

    if country:
        query = query.filter(Agent.country == country.upper())

    if tier:
        query = query.filter(Agent.tier == tier)

    total = query.count()
    agents = query.order_by(Agent.created_at.desc()).offset(skip).limit(limit).all()

    # Enrich with user data
    results = []
    for agent in agents:
        user = db.query(User).filter(User.id == agent.user_id).first()
        stats = AgentService.get_agent_stats(db, agent.id)

        results.append({
            "id": str(agent.id),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name
            } if user else None,
            "referral_code": agent.referral_code,
            "country": agent.country,
            "status": agent.status,
            "tier": agent.tier,
            "is_country_manager": agent.is_country_manager,
            "total_sales": float(agent.total_sales or 0),
            "total_commissions": float(agent.total_commissions or 0),
            "monthly_sales": float(agent.monthly_sales or 0),
            "total_customers": stats.get("total_customers", 0),
            "sub_agents": stats.get("sub_agents", 0),
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "approved_at": agent.approved_at.isoformat() if agent.approved_at else None
        })

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "agents": results
    }


@router.get("/{agent_id}")
async def get_agent_details(
    agent_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed agent information."""
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    user = db.query(User).filter(User.id == agent.user_id).first()
    stats = AgentService.get_agent_stats(db, agent_id)

    # Get recent commissions
    recent_commissions = db.query(Commission).filter(
        Commission.agent_id == agent.id
    ).order_by(Commission.created_at.desc()).limit(20).all()

    # Get sub-agents
    sub_agents = db.query(Agent).filter(
        Agent.parent_agent_id == agent.id
    ).all()

    return {
        "agent": {
            "id": str(agent.id),
            "referral_code": agent.referral_code,
            "country": agent.country,
            "status": agent.status,
            "tier": agent.tier,
            "is_country_manager": agent.is_country_manager,
            "demo_scans_remaining": agent.demo_scans_remaining,
            "total_sales": float(agent.total_sales or 0),
            "monthly_sales": float(agent.monthly_sales or 0),
            "total_commissions": float(agent.total_commissions or 0),
            "approved_at": agent.approved_at.isoformat() if agent.approved_at else None,
            "rejected_at": agent.rejected_at.isoformat() if agent.rejected_at else None,
            "rejection_reason": agent.rejection_reason,
            "created_at": agent.created_at.isoformat() if agent.created_at else None
        },
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        } if user else None,
        "stats": stats,
        "recent_commissions": [
            {
                "id": str(c.id),
                "amount": float(c.commission_amount),
                "type": c.commission_type,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in recent_commissions
        ],
        "sub_agents": [
            {
                "id": str(a.id),
                "referral_code": a.referral_code,
                "tier": a.tier,
                "status": a.status,
                "total_sales": float(a.total_sales or 0)
            }
            for a in sub_agents
        ]
    }


@router.post("/{agent_id}/approve")
async def approve_agent(
    agent_id: str,
    request: ApproveAgentRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Approve agent application.

    Grants demo scans and activates referral tracking.
    """
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent.status != "pending":
        raise HTTPException(status_code=400, detail=f"Agent is already {agent.status}")

    # Get user
    user = db.query(User).filter(User.id == agent.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found for this agent")

    # Generate random password for new agent
    import random
    import string
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    # Update user account: activate + set new password
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user.is_active = True
    user.password_hash = pwd_context.hash(new_password)

    # Approve agent
    agent.status = "approved"
    agent.approved_at = datetime.utcnow()
    agent.approved_by = admin.id
    agent.demo_scans_remaining = request.grant_demo_scans

    db.commit()
    db.refresh(agent)

    # Send email with credentials
    try:
        from app.services.email_service import EmailService

        email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0047AB 0%, #1E90FF 100%);
                          color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                .content {{ background: #f9f9f9; padding: 30px; margin: 20px 0; border-radius: 10px; }}
                .credentials {{ background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .code {{ background-color: #e5e7eb; padding: 4px 8px; border-radius: 4px; font-family: monospace; }}
                .button {{ display: inline-block; background: #0047AB; color: white;
                          padding: 15px 40px; text-decoration: none; border-radius: 8px;
                          font-weight: bold; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                    <p>Your Agent Application is Approved</p>
                </div>

                <div class="content">
                    <h2>Welcome {user.name}!</h2>
                    <p>Your application to become an Africa Cyber Trust agent has been <strong>approved</strong>! You can now start earning commissions by referring customers to our cybersecurity services.</p>

                    <div class="credentials">
                        <h3>Your Login Credentials:</h3>
                        <p><strong>Email:</strong> {user.email}</p>
                        <p><strong>Password:</strong> <span class="code">{new_password}</span></p>
                        <p><strong>Your Referral Code:</strong> <span class="code" style="background-color: #dbeafe; color: #1e40af; font-weight: bold;">{agent.referral_code}</span></p>
                    </div>

                    <a href="http://localhost:3004" class="button">Access Agent Portal</a>

                    <h3>What's Next?</h3>
                    <ul>
                        <li>Log in to your agent portal using the credentials above</li>
                        <li>Complete the training courses to learn how to be a successful agent</li>
                        <li>Start referring customers and earning commissions!</li>
                        <li>Share your referral code to build your network</li>
                    </ul>

                    <p style="margin-top: 30px;"><strong>Welcome to the Africa Cyber Trust agent network!</strong></p>
                </div>

                <p style="color: #6b7280; font-size: 12px; text-align: center;">
                    This email was sent by Africa Cyber Trust. If you did not apply to become an agent, please ignore this email.
                </p>
            </div>
        </body>
        </html>
        """

        EmailService.send_verification_email(
            to_email=user.email,
            domain="Agent Credentials",
            verification_link=email_html  # Reusing this param for HTML content
        )

        print(f"[INFO] Credentials email sent to {user.email}")
    except Exception as e:
        print(f"[WARNING] Failed to send credentials email: {e}")
        # Don't fail approval if email sending fails

    # Send WhatsApp notification
    if user.phone_number:
        try:
            whatsapp_service.send_agent_approved(
                to_number=user.phone_number,
                agent_name=user.name,
                referral_code=agent.referral_code
            )
        except Exception as e:
            print(f"[WARNING] WhatsApp notification failed: {e}")
            # Don't fail approval if WhatsApp fails

    # Audit log
    await log_admin_action(
        action="approve_agent",
        actor=admin,
        db=db,
        request=req,
        target_type="agent",
        target_id=str(agent.id),
        context_data={
            "referral_code": agent.referral_code,
            "country": agent.country,
            "demo_scans": request.grant_demo_scans
        }
    )

    return {
        "success": True,
        "agent_id": str(agent.id),
        "referral_code": agent.referral_code,
        "status": agent.status,
        "message": "Agent approved successfully!"
    }


@router.post("/{agent_id}/reject")
async def reject_agent(
    agent_id: str,
    request: RejectAgentRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Reject agent application."""
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Reject
    agent.status = "rejected"
    agent.rejected_at = datetime.utcnow()
    agent.rejection_reason = request.reason

    db.commit()

    # Audit log
    await log_admin_action(
        action="reject_agent",
        actor=admin,
        db=db,
        request=req,
        target_type="agent",
        target_id=str(agent.id),
        context_data={
            "referral_code": agent.referral_code,
            "reason": request.reason
        }
    )

    return {
        "success": True,
        "message": "Agent application rejected"
    }


@router.get("/payouts/pending")
async def get_pending_payouts(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all pending payout requests."""
    payouts = db.query(AgentPayout).filter(
        AgentPayout.status == "pending"
    ).order_by(AgentPayout.requested_at).all()

    results = []
    for payout in payouts:
        agent = db.query(Agent).filter(Agent.id == payout.agent_id).first()
        user = db.query(User).filter(User.id == agent.user_id).first() if agent else None

        results.append({
            "id": str(payout.id),
            "agent": {
                "id": str(agent.id),
                "referral_code": agent.referral_code,
                "user": {
                    "email": user.email,
                    "name": user.name
                } if user else None
            } if agent else None,
            "amount": float(payout.amount),
            "currency": payout.currency,
            "method": payout.method,
            "destination": payout.destination,
            "requested_at": payout.requested_at.isoformat() if payout.requested_at else None
        })

    return {
        "total": len(results),
        "payouts": results
    }


@router.post("/payouts/{payout_id}/process")
async def process_payout(
    payout_id: str,
    request: ProcessPayoutRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Process payout request (approve or reject).

    If approved, admin must manually send payment via PawaPay/crypto.
    """
    payout = db.query(AgentPayout).filter(AgentPayout.id == uuid.UUID(payout_id)).first()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")

    if payout.status != "pending":
        raise HTTPException(status_code=400, detail=f"Payout already {payout.status}")

    if request.action == "approve":
        payout.status = "paid"
        payout.processed_at = datetime.utcnow()
        payout.processed_by = admin.id
        payout.transaction_reference = request.transaction_reference

        # Mark commissions as paid
        commissions = db.query(Commission).filter(
            Commission.agent_id == payout.agent_id,
            Commission.status == "pending"
        ).limit(int(payout.amount / 10)).all()  # Rough estimate

        for commission in commissions:
            commission.status = "paid"
            commission.paid_at = datetime.utcnow()

        # Send WhatsApp notification for approved payout
        agent = db.query(Agent).filter(Agent.id == payout.agent_id).first()
        if agent:
            user = db.query(User).filter(User.id == agent.user_id).first()
            if user and user.phone_number:
                try:
                    whatsapp_service.send_payout_processed(
                        to_number=user.phone_number,
                        agent_name=user.name,
                        amount=float(payout.amount),
                        method="Mobile Money" if payout.method == "mobile_money" else "Crypto"
                    )
                except Exception as e:
                    print(f"[WARNING] WhatsApp payout notification failed: {e}")

    elif request.action == "reject":
        payout.status = "rejected"
        payout.processed_at = datetime.utcnow()
        payout.processed_by = admin.id
        payout.rejection_reason = request.rejection_reason

    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    db.commit()

    # Audit log
    await log_admin_action(
        action=f"payout_{request.action}",
        actor=admin,
        db=db,
        request=req,
        target_type="payout",
        target_id=str(payout.id),
        context_data={
            "amount": float(payout.amount),
            "method": payout.method,
            "transaction_ref": request.transaction_reference
        }
    )

    return {
        "success": True,
        "payout_id": str(payout.id),
        "status": payout.status,
        "message": f"Payout {request.action}d successfully"
    }


@router.post("/{agent_id}/set-country-manager")
async def set_country_manager(
    agent_id: str,
    request: SetCountryManagerRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Assign agent as country manager.

    Country manager gets 3% bonus on all sales in their country.
    Only one country manager per country.
    """
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent.status != "approved":
        raise HTTPException(status_code=400, detail="Agent must be approved first")

    # Remove existing country manager
    existing_cm = db.query(Agent).filter(
        Agent.country == request.country.upper(),
        Agent.is_country_manager == True
    ).first()

    if existing_cm:
        existing_cm.is_country_manager = False

    # Set new country manager
    agent.is_country_manager = True
    agent.country = request.country.upper()

    db.commit()

    # Audit log
    await log_admin_action(
        action="set_country_manager",
        actor=admin,
        db=db,
        request=req,
        target_type="agent",
        target_id=str(agent.id),
        context_data={
            "country": request.country.upper(),
            "referral_code": agent.referral_code,
            "replaced": str(existing_cm.id) if existing_cm else None
        }
    )

    return {
        "success": True,
        "agent_id": str(agent.id),
        "country": agent.country,
        "is_country_manager": True,
        "message": f"Agent is now country manager for {agent.country}"
    }
