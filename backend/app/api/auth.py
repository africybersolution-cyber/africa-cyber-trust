"""Authentication endpoints for login, signup, and user management."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.services.auth_service import AuthService
from app.services.trial_service import TrialService
from app.services.access_control_service import AccessControlService
from app.models.user import User
from app.models.company import Company

router = APIRouter()

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic schemas
class UserSignupRequest(BaseModel):
    """User signup request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)
    account_type: str = Field(default='personal')  # 'personal', 'professional', or 'enterprise'

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "name": "John Doe",
                "account_type": "personal"
            }
        }


class BusinessRegisterRequest(BaseModel):
    """Business registration request."""
    company_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)
    country: str = Field(..., min_length=2, max_length=2)
    domain: Optional[str] = None
    phone: Optional[str] = None
    size: Optional[str] = None


# Dependency to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    print(f"[AUTH] Received token: {token[:50] if token else 'NONE'}...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = AuthService.get_current_user(db, token)
    if user is None:
        print("[AUTH] Token validation failed - user is None")
        raise credentials_exception

    print(f"[AUTH] Token validated successfully for user: {user.email}")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: UserSignupRequest,
    db: Session = Depends(get_db)
):
    """Sign up a new user with trial period."""
    # Validate account type
    valid_plans = ['personal', 'professional', 'enterprise']
    if request.account_type not in valid_plans:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid account_type. Must be one of: {', '.join(valid_plans)}"
        )

    try:
        user = AuthService.create_user(
            db=db,
            email=request.email,
            password=request.password,
            name=request.name
        )

        # Set account type and start plan-specific trial
        user.account_type = request.account_type
        db.commit()

        # Start trial (7 days for personal, 14 days for professional)
        TrialService.start_trial(user, db, plan_name=request.account_type)

        access_token = AuthService.create_access_token(
            data={"sub": user.email, "user_id": str(user.id), "role": user.role}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "account_type": user.account_type,
                "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@router.get("/trial-status")
async def get_trial_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's trial status."""
    is_active = TrialService.check_trial_active(current_user, db)
    days_remaining = TrialService.days_remaining(current_user)
    has_subscription = TrialService.has_active_subscription(current_user.id, db)

    return {
        "trial_status": current_user.trial_status,
        "trial_active": is_active,
        "days_remaining": days_remaining,
        "trial_ends_at": current_user.trial_ends_at.isoformat() if current_user.trial_ends_at else None,
        "has_subscription": has_subscription,
        "account_type": current_user.account_type
    }


@router.get("/trial-info")
async def get_trial_info():
    """Get trial period information for all plans (public endpoint)."""
    return {
        "personal": {
            "trial_days": TrialService.get_trial_days('personal'),
            "description": "7-day free trial - No credit card required"
        },
        "professional": {
            "trial_days": TrialService.get_trial_days('professional'),
            "description": "14-day free trial - Full access to all features"
        },
        "enterprise": {
            "trial_days": TrialService.get_trial_days('enterprise'),
            "description": "Custom trial period - Contact sales"
        }
    }


@router.get("/permissions")
async def get_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's permissions and access level.

    Used by frontend to show/hide features based on subscription.
    """
    permissions = AccessControlService.get_user_permissions(current_user, db)

    return {
        **permissions,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "account_type": current_user.account_type
        }
    }


@router.post("/register-business", status_code=status.HTTP_201_CREATED)
async def register_business(
    request: BusinessRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new business."""
    try:
        result = AuthService.register_business(
            db=db,
            company_name=request.company_name,
            email=request.email,
            password=request.password,
            name=request.name,
            country=request.country,
            domain=request.domain,
            phone=request.phone,
            size=request.size
        )

        # Start 14-day trial for business (professional plan)
        user = result["user"]
        user.account_type = 'professional'
        db.commit()
        TrialService.start_trial(user, db, plan_name='professional')

        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"],
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "account_type": user.account_type,
                "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None
            },
            "company": {
                "id": str(result["company"].id),
                "name": result["company"].name,
                "country": result["company"].country,
                "plan": result["company"].plan_id
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with email and password."""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "role": user.role}
    )

    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }

    # Add company data if user has a company
    if user.company_id:
        company = db.query(Company).filter(Company.id == user.company_id).first()
        if company:
            response_data["company"] = {
                "id": str(company.id),
                "name": company.name,
                "country": company.country,
                "plan": company.plan_id
            }

    return response_data


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user."""
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    Request password reset email.
    Generates a reset token and sends email with reset link.
    """
    import secrets
    from datetime import datetime, timedelta

    user = db.query(User).filter(User.email == email).first()

    # Always return success even if email doesn't exist (security best practice)
    if not user:
        return {"message": "If that email exists, a reset link has been sent"}

    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)

    # Store token in user record (expires in 1 hour)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    # Send password reset email
    try:
        # Add to email queue
        from app.models.email_queue import EmailQueue  # Assuming you have this model

        reset_link = f"https://www.africybertrust.com/reset-password?token={reset_token}"

        email_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #0047AB;">Password Reset Request</h2>
            <p>You requested to reset your password for Africa Cyber Trust Infrastructure.</p>
            <p>Click the button below to reset your password:</p>
            <p style="margin: 30px 0;">
                <a href="{reset_link}" style="background: linear-gradient(135deg, #0047AB 0%, #DAA520 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p style="color: #666; font-size: 14px;">
                This link will expire in 1 hour.<br>
                If you didn't request this, please ignore this email.
            </p>
            <p style="color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                Africa Cyber Trust Infrastructure<br>
                © 2026 All rights reserved
            </p>
        </div>
        """

        # Write to email queue (will be sent by email service)
        email_record = EmailQueue(
            to=user.email,
            subject="Reset Your Password - Africa Cyber Trust",
            html=email_html,
            created_at=datetime.utcnow()
        )
        db.add(email_record)
        db.commit()

    except Exception as e:
        print(f"Error sending password reset email: {e}")
        # Still return success to user

    return {"message": "If that email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Reset password using reset token from email.
    """
    from datetime import datetime
    from app.services.auth_service import AuthService

    # Find user with this reset token
    user = db.query(User).filter(User.reset_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check if token is expired
    if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )

    # Update password
    user.hashed_password = AuthService.get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password successfully reset. You can now login with your new password."}
