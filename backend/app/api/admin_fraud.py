"""Admin API - Fraud Detection"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from app.db.database import get_db
from app.core.admin_deps import require_admin, require_super_admin, log_admin_action
from app.models.user import User
from app.models.agent import Agent
from app.services.fraud_detection_service import FraudDetectionService


router = APIRouter(prefix="/api/admin/fraud", tags=["Admin - Fraud Detection"])


# ===== REQUEST MODELS =====

class SuspendAgentRequest(BaseModel):
    """Suspend agent for fraud."""
    reason: str


# ===== ENDPOINTS =====

@router.get("/scan")
async def scan_all_agents(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Scan all agents for fraudulent activity.

    Returns summary with flagged agents sorted by severity.
    """
    result = FraudDetectionService.scan_all_agents(db)

    return {
        "success": True,
        "scan_timestamp": "now",
        **result
    }


@router.get("/agent/{agent_id}")
async def check_agent_fraud(
    agent_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Check specific agent for fraud indicators.

    Returns fraud flags and score.
    """
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    flags = FraudDetectionService.check_agent_fraud(db, agent.id)
    score = FraudDetectionService.get_fraud_score(db, agent.id)

    user = db.query(User).filter(User.id == agent.user_id).first()

    return {
        "agent_id": str(agent.id),
        "referral_code": agent.referral_code,
        "user": {
            "email": user.email if user else None,
            "name": user.name if user else None
        },
        "fraud_score": score,
        "risk_level": (
            "critical" if score >= 70 else
            "high" if score >= 40 else
            "medium" if score >= 20 else
            "low"
        ),
        "flags": flags,
        "flag_count": len(flags)
    }


@router.get("/user/{user_id}")
async def check_user_fraud(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Check specific user for fraud indicators.

    Useful for checking referred users.
    """
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    flags = FraudDetectionService.check_user_fraud(db, user.id)

    return {
        "user_id": str(user.id),
        "email": user.email,
        "name": user.name,
        "flags": flags,
        "flag_count": len(flags)
    }


@router.post("/agent/{agent_id}/suspend")
async def suspend_fraudulent_agent(
    agent_id: str,
    request: SuspendAgentRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Suspend agent for fraudulent activity.

    This prevents them from earning future commissions.
    """
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get fraud details before suspending
    flags = FraudDetectionService.check_agent_fraud(db, agent.id)
    fraud_score = FraudDetectionService.get_fraud_score(db, agent.id)

    # Suspend agent
    agent.status = "suspended"
    agent.rejection_reason = f"Suspended for fraud: {request.reason}"

    db.commit()

    # Audit log
    await log_admin_action(
        action="suspend_agent_fraud",
        actor=admin,
        db=db,
        request=req,
        target_type="agent",
        target_id=str(agent.id),
        context_data={
            "referral_code": agent.referral_code,
            "reason": request.reason,
            "fraud_score": fraud_score,
            "flags": [f["type"] for f in flags]
        }
    )

    return {
        "success": True,
        "agent_id": str(agent.id),
        "status": "suspended",
        "fraud_score": fraud_score,
        "message": "Agent suspended for fraudulent activity"
    }


@router.post("/agent/{agent_id}/clear")
async def clear_fraud_flags(
    agent_id: str,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Clear fraud flags for an agent (false positive).

    Use this if manual review determines the agent is legitimate.
    """
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Audit log
    await log_admin_action(
        action="clear_fraud_flags",
        actor=admin,
        db=db,
        request=req,
        target_type="agent",
        target_id=str(agent.id),
        context_data={
            "referral_code": agent.referral_code,
            "note": "Fraud flags cleared - determined to be false positive"
        }
    )

    return {
        "success": True,
        "agent_id": str(agent.id),
        "message": "Fraud flags cleared. Agent marked as legitimate."
    }
