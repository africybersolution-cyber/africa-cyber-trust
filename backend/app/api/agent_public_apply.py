"""Public Agent Application API - No auth required"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
import random
import string

from app.db.database import get_db
from app.models.agent import Agent
from app.models.user import User, UserRole


router = APIRouter(prefix="/api/agents", tags=["Agent Application"])


class PublicAgentApplicationRequest(BaseModel):
    """Public agent application - no login required."""
    name: str
    email: EmailStr
    phone_number: str
    country: str  # ISO code (e.g., "RW")
    parent_referral_code: Optional[str] = None


@router.post("/apply-public")
async def apply_as_agent_public(
    request: PublicAgentApplicationRequest,
    db: Session = Depends(get_db)
):
    """
    Public agent application endpoint.

    Creates inactive user account + pending agent application.
    When admin approves:
    1. Activate user account
    2. Generate random password
    3. Send email with credentials
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        # Check if they're already an agent
        existing_agent = db.query(Agent).filter(Agent.user_id == existing_user.id).first()
        if existing_agent:
            raise HTTPException(
                status_code=400,
                detail="An agent application already exists for this email. Please check your email for updates."
            )

    # Validate country code
    if len(request.country) != 2:
        raise HTTPException(status_code=400, detail="Country must be 2-letter ISO code (e.g., RW)")

    # Create inactive user account (will be activated on approval)
    if not existing_user:
        # Generate temporary password (will be replaced on approval)
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        new_user = User(
            id=uuid.uuid4(),
            email=request.email,
            name=request.name,
            phone_number=request.phone_number,
            hashed_password=pwd_context.hash(temp_password),
            role=UserRole.NORMAL_USER,
            is_active=False,  # INACTIVE until approved
            email_verified=False
        )

        db.add(new_user)
        db.flush()  # Get the user ID
        user = new_user
    else:
        # Update existing user's phone if provided
        if request.phone_number and not existing_user.phone_number:
            existing_user.phone_number = request.phone_number
        user = existing_user

    # Generate referral code (8 chars, random)
    referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Make sure referral code is unique
    while db.query(Agent).filter(Agent.referral_code == referral_code).first():
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Find parent agent if referral code provided
    parent_agent_id = None
    if request.parent_referral_code:
        parent_agent = db.query(Agent).filter(
            Agent.referral_code == request.parent_referral_code.upper()
        ).first()

        if parent_agent:
            parent_agent_id = parent_agent.id

    # Create pending agent application
    agent = Agent(
        id=uuid.uuid4(),
        user_id=user.id,
        referral_code=referral_code,
        country=request.country.upper(),
        status="pending",
        tier="bronze",
        parent_agent_id=parent_agent_id,
        demo_scans_remaining=5  # Will get more on approval
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "success": True,
        "message": "Application submitted successfully! You'll receive an email with your login credentials within 48 hours once approved.",
        "referral_code": referral_code
    }
