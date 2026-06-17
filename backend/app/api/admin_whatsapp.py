"""Admin API - WhatsApp Notifications"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from app.db.database import get_db
from app.core.admin_deps import require_admin, require_super_admin, log_admin_action
from app.models.user import User
from app.models.agent import Agent
from app.services.whatsapp_service import whatsapp_service
from app.services.agent_notifications_service import agent_notifications_service


router = APIRouter(prefix="/api/admin/whatsapp", tags=["Admin - WhatsApp"])


# ===== REQUEST MODELS =====

class TestMessageRequest(BaseModel):
    """Send test WhatsApp message."""
    to_number: str
    message: str


class SendToAgentRequest(BaseModel):
    """Send message to specific agent."""
    agent_id: str
    template: str  # approved, commission, payout, fraud_alert, monthly_summary
    data: Optional[dict] = None


# ===== ENDPOINTS =====

@router.post("/test")
async def send_test_message(
    request: TestMessageRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Send test WhatsApp message.

    For testing Twilio integration.
    """
    result = whatsapp_service.send_message(
        to_number=request.to_number,
        message=request.message
    )

    # Audit log
    await log_admin_action(
        action="whatsapp_test_send",
        actor=admin,
        db=db,
        request=req,
        target_type="whatsapp",
        target_id=request.to_number,
        context_data={
            "success": result.get("success"),
            "message_length": len(request.message)
        }
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to send"))

    return {
        "success": True,
        "message_sid": result.get("message_sid"),
        "message": "WhatsApp message sent successfully"
    }


@router.post("/send-to-agent")
async def send_to_agent(
    request: SendToAgentRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Send WhatsApp notification to specific agent using template.

    Templates: approved, commission, payout, fraud_alert, monthly_summary
    """
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(request.agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    user = db.query(User).filter(User.id == agent.user_id).first()
    if not user or not user.phone_number:
        raise HTTPException(status_code=400, detail="Agent has no phone number")

    # Send based on template
    result = None
    data = request.data or {}

    if request.template == "approved":
        result = whatsapp_service.send_agent_approved(
            to_number=user.phone_number,
            agent_name=user.name,
            referral_code=agent.referral_code
        )

    elif request.template == "commission":
        result = whatsapp_service.send_commission_earned(
            to_number=user.phone_number,
            agent_name=user.name,
            amount=data.get("amount", 0),
            customer_email=data.get("customer_email", "Unknown")
        )

    elif request.template == "payout":
        result = whatsapp_service.send_payout_processed(
            to_number=user.phone_number,
            agent_name=user.name,
            amount=data.get("amount", 0),
            method=data.get("method", "mobile_money")
        )

    elif request.template == "fraud_alert":
        result = whatsapp_service.send_fraud_alert(
            to_number=user.phone_number,
            agent_name=user.name,
            reason=data.get("reason", "Suspicious activity detected")
        )

    elif request.template == "monthly_summary":
        result = whatsapp_service.send_monthly_summary(
            to_number=user.phone_number,
            agent_name=user.name,
            total_sales=data.get("total_sales", 0),
            commissions=data.get("commissions", 0),
            customers=data.get("customers", 0)
        )

    else:
        raise HTTPException(status_code=400, detail=f"Invalid template: {request.template}")

    # Audit log
    await log_admin_action(
        action="whatsapp_send_agent",
        actor=admin,
        db=db,
        request=req,
        target_type="agent",
        target_id=str(agent.id),
        context_data={
            "template": request.template,
            "success": result.get("success") if result else False,
            "phone": user.phone_number
        }
    )

    if not result or not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to send") if result else "Failed to send"
        )

    return {
        "success": True,
        "message_sid": result.get("message_sid"),
        "template": request.template,
        "message": f"WhatsApp notification sent to {user.name}"
    }


@router.get("/config")
async def get_whatsapp_config(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get WhatsApp configuration status.

    Returns whether Twilio is configured.
    """
    is_configured = whatsapp_service.client is not None

    return {
        "configured": is_configured,
        "provider": "Twilio" if is_configured else None,
        "from_number": whatsapp_service.whatsapp_from if is_configured else None,
        "templates": [
            "approved",
            "commission",
            "payout",
            "fraud_alert",
            "monthly_summary",
            "training_reminder"
        ]
    }


@router.post("/send-monthly-summaries")
async def send_monthly_summaries(
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Send monthly performance summary to all agents.

    Manually trigger the monthly summary job.
    """
    result = agent_notifications_service.send_monthly_summaries(db)

    # Audit log
    await log_admin_action(
        action="whatsapp_monthly_summaries",
        actor=admin,
        db=db,
        request=req,
        target_type="bulk",
        target_id="all_agents",
        context_data={
            "sent": result["sent"],
            "failed": result["failed"],
            "total": result["total_agents"]
        }
    )

    return {
        "success": True,
        "message": f"Sent {result['sent']} summaries to agents",
        **result
    }


@router.post("/send-training-reminders")
async def send_training_reminders(
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Send training reminders to agents with incomplete required courses.

    Manually trigger the training reminder job.
    """
    result = agent_notifications_service.send_training_reminders(db)

    # Audit log
    await log_admin_action(
        action="whatsapp_training_reminders",
        actor=admin,
        db=db,
        request=req,
        target_type="bulk",
        target_id="all_agents",
        context_data={
            "sent": result["sent"],
            "total": result["total_agents"]
        }
    )

    return {
        "success": True,
        "message": f"Sent {result['sent']} training reminders",
        **result
    }
