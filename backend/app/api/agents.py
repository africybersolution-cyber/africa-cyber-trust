"""Agent API - Application, Dashboard, Payouts"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.agent import Agent, Commission, AgentPayout
from app.services.agent_service import AgentService


router = APIRouter(prefix="/api/agents", tags=["Agents"])


# ===== REQUEST MODELS =====

class AgentApplicationRequest(BaseModel):
    """Agent signup application."""
    country: str  # ISO code (e.g., "RW")
    parent_referral_code: Optional[str] = None  # For MLM


class PayoutRequest(BaseModel):
    """Request payout of commissions."""
    amount: float
    method: str  # mobile_money, crypto
    destination: str  # Phone number or wallet address
    currency: str = "USD"


# ===== ENDPOINTS =====

@router.post("/apply")
async def apply_as_agent(
    request: AgentApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply to become an agent.

    Creates pending agent application that admin must approve.
    """
    # Check if already an agent
    existing = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"You are already an agent with status: {existing.status}"
        )

    # Validate country code
    if len(request.country) != 2:
        raise HTTPException(status_code=400, detail="Country must be 2-letter ISO code (e.g., RW)")

    # Create agent
    try:
        agent = AgentService.create_agent(
            db=db,
            user_id=current_user.id,
            country=request.country.upper(),
            parent_referral_code=request.parent_referral_code
        )

        return {
            "success": True,
            "agent_id": str(agent.id),
            "referral_code": agent.referral_code,
            "status": agent.status,
            "message": "Agent application submitted! Admin will review and approve."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_my_agent_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's agent profile and stats.

    Returns full dashboard data including earnings, tier, customers, etc.
    """
    # Get agent profile
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent. Apply first using POST /api/agents/apply")

    # Get stats
    stats = AgentService.get_agent_stats(db, agent.id)

    # Get recent commissions
    recent_commissions = db.query(Commission).filter(
        Commission.agent_id == agent.id
    ).order_by(Commission.created_at.desc()).limit(10).all()

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
            "approved_at": agent.approved_at.isoformat() if agent.approved_at else None,
            "created_at": agent.created_at.isoformat() if agent.created_at else None
        },
        "stats": stats,
        "recent_commissions": [
            {
                "id": str(c.id),
                "amount": float(c.commission_amount),
                "type": c.commission_type,
                "tier": c.tier,
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


@router.get("/commissions")
async def get_my_commissions(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get my commission history.

    Can filter by status (pending, paid).
    """
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    query = db.query(Commission).filter(Commission.agent_id == agent.id)

    if status:
        query = query.filter(Commission.status == status)

    total = query.count()
    commissions = query.order_by(Commission.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "commissions": [
            {
                "id": str(c.id),
                "amount": float(c.amount),
                "commission_rate": float(c.commission_rate),
                "commission_amount": float(c.commission_amount),
                "tier": c.tier,
                "type": c.commission_type,
                "status": c.status,
                "paid_at": c.paid_at.isoformat() if c.paid_at else None,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in commissions
        ]
    }


@router.post("/payouts/request")
async def request_payout(
    request: PayoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request payout of earned commissions.

    Minimum payout: $50
    Methods: mobile_money, crypto
    """
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    if agent.status != "approved":
        raise HTTPException(status_code=403, detail="Your agent account is not approved yet")

    # Get pending commission balance
    stats = AgentService.get_agent_stats(db, agent.id)
    pending_balance = stats.get("pending_commissions", 0)

    # Validate amount
    if request.amount < 50:
        raise HTTPException(status_code=400, detail="Minimum payout is $50")

    if request.amount > pending_balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. You have ${pending_balance:.2f} available"
        )

    # Validate method
    if request.method not in ["mobile_money", "crypto"]:
        raise HTTPException(status_code=400, detail="Method must be 'mobile_money' or 'crypto'")

    # Create payout request
    payout = AgentPayout(
        agent_id=agent.id,
        amount=request.amount,
        currency=request.currency,
        method=request.method,
        destination=request.destination,
        status="pending"
    )

    db.add(payout)
    db.commit()
    db.refresh(payout)

    return {
        "success": True,
        "payout_id": str(payout.id),
        "amount": float(payout.amount),
        "method": payout.method,
        "status": payout.status,
        "message": "Payout request submitted! Admin will process within 1-3 business days."
    }


@router.get("/payouts")
async def get_my_payouts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get my payout history."""
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    payouts = db.query(AgentPayout).filter(
        AgentPayout.agent_id == agent.id
    ).order_by(AgentPayout.created_at.desc()).all()

    return {
        "payouts": [
            {
                "id": str(p.id),
                "amount": float(p.amount),
                "currency": p.currency,
                "method": p.method,
                "destination": p.destination,
                "status": p.status,
                "requested_at": p.requested_at.isoformat() if p.requested_at else None,
                "processed_at": p.processed_at.isoformat() if p.processed_at else None,
                "rejection_reason": p.rejection_reason
            }
            for p in payouts
        ]
    }


@router.get("/referral-link")
async def get_referral_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get referral link for sharing.

    Returns signup link with agent's referral code.
    """
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    base_url = "https://africa-cyber-trust.vercel.app"  # Update with actual frontend URL

    return {
        "referral_code": agent.referral_code,
        "referral_link": f"{base_url}/signup?ref={agent.referral_code}",
        "mlm_link": f"{base_url}/agents/apply?parent={agent.referral_code}",
        "share_message": f"Join Africa Cyber Trust and get cybersecurity protection for your business! Use my code: {agent.referral_code}"
    }
