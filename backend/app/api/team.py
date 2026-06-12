"""Team management endpoints - invite members, manage roles."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.access_control_service import AccessControlService

router = APIRouter()


# Pydantic Models
class TeamMember(BaseModel):
    id: str
    name: str
    email: str
    role: str  # 'admin', 'analyst', 'viewer'
    status: str  # 'active', 'pending', 'inactive'
    joined_date: str
    company_id: Optional[str] = None

    class Config:
        from_attributes = True


class InviteRequest(BaseModel):
    email: EmailStr
    role: str  # 'admin', 'analyst', 'viewer'
    name: Optional[str] = None


class InviteResponse(BaseModel):
    success: bool
    message: str
    invite_id: str
    email: str
    role: str


class UpdateRoleRequest(BaseModel):
    role: str  # 'admin', 'analyst', 'viewer'


@router.get("/members", response_model=List[TeamMember])
async def list_team_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all team members for the current user's company."""
    # Fetch all users in the same company
    members = db.query(User).filter(
        User.company_id == current_user.company_id
    ).all()

    return [
        TeamMember(
            id=str(member.id),
            name=member.name,
            email=member.email,
            role=member.role,
            status='active',
            joined_date=member.created_at.strftime('%b %d, %Y') if member.created_at else 'Unknown',
            company_id=str(member.company_id) if member.company_id else None
        )
        for member in members
    ]


@router.post("/invite", response_model=InviteResponse)
async def invite_team_member(
    invite: InviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a new team member."""
    # Check if user has admin role
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Only admins can invite team members"
        )

    # Check team member limit based on subscription plan
    team_limit = AccessControlService.get_team_member_limit(current_user, db)
    current_team_count = db.query(User).filter(
        User.company_id == current_user.company_id
    ).count()

    if current_team_count >= team_limit:
        access_level = AccessControlService.get_user_access_level(current_user, db)
        if access_level == 'personal':
            raise HTTPException(
                status_code=403,
                detail=f"Personal plan allows only 1 team member. Upgrade to Professional ($49/month) to add up to 5 members."
            )
        elif access_level == 'professional':
            raise HTTPException(
                status_code=403,
                detail=f"Professional plan allows up to 5 team members. Upgrade to Enterprise for unlimited members."
            )

    # Validate role
    valid_roles = ['admin', 'analyst', 'viewer']
    if invite.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == invite.email).first()
    if existing_user:
        if existing_user.company_id == current_user.company_id:
            raise HTTPException(
                status_code=400,
                detail="User is already a member of your team"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="User already exists in another company"
            )

    # TODO: Send invitation email
    # TODO: Store invitation in database with token
    invite_id = str(uuid.uuid4())

    print(f"📧 Sending invitation to: {invite.email}")
    print(f"   Role: {invite.role}")
    print(f"   From: {current_user.email}")
    print(f"   Company: {current_user.company_id}")

    return InviteResponse(
        success=True,
        message=f"Invitation sent to {invite.email}",
        invite_id=invite_id,
        email=invite.email,
        role=invite.role
    )


@router.delete("/members/{member_id}")
async def remove_team_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a team member."""
    # Check if user has admin role
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Only admins can remove team members"
        )

    # Find the member
    member = db.query(User).filter(User.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Check if member is in the same company
    if member.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot remove member from another company"
        )

    # Prevent removing yourself
    if member.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove yourself from the team"
        )

    # Delete the member
    db.delete(member)
    db.commit()

    return {
        "success": True,
        "message": f"Member {member.email} removed from team",
        "member_id": member_id
    }


@router.patch("/members/{member_id}/role")
async def update_member_role(
    member_id: str,
    update: UpdateRoleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a team member's role."""
    # Check if user has admin role
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Only admins can update member roles"
        )

    # Validate role
    valid_roles = ['admin', 'analyst', 'viewer']
    if update.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    # Find the member
    member = db.query(User).filter(User.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Check if member is in the same company
    if member.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot update member from another company"
        )

    # Update the role
    member.role = update.role
    db.commit()
    db.refresh(member)

    return {
        "success": True,
        "message": f"Role updated to {update.role}",
        "member_id": member_id,
        "new_role": update.role
    }


class TeamStats(BaseModel):
    total_members: int
    active_members: int
    pending_invites: int
    admins: int
    analysts: int
    viewers: int
    member_limit: int
    can_add_members: bool
    access_level: str


@router.get("/stats", response_model=TeamStats)
async def get_team_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team statistics with access control limits."""
    members = db.query(User).filter(
        User.company_id == current_user.company_id
    ).all()

    # Get team member limit based on subscription
    member_limit = AccessControlService.get_team_member_limit(current_user, db)
    access_level = AccessControlService.get_user_access_level(current_user, db)
    total_members = len(members)

    return TeamStats(
        total_members=total_members,
        active_members=total_members,
        pending_invites=0,  # TODO: Count pending invites from database
        admins=len([m for m in members if m.role == 'admin']),
        analysts=len([m for m in members if m.role == 'analyst']),
        viewers=len([m for m in members if m.role == 'viewer']),
        member_limit=member_limit,
        can_add_members=total_members < member_limit,
        access_level=access_level
    )
