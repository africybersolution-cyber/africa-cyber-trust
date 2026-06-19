"""Authentication endpoints for login, signup, and user management."""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.services.auth_service import AuthService
from app.services.trial_service import TrialService
from app.services.access_control_service import AccessControlService
from app.services.email_service import EmailService
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
    account_type: str = Field(default='starter')  # 'starter', 'professional', or 'enterprise'
    referral_code: Optional[str] = None  # Agent referral code (links customer to agent for commissions)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "name": "John Doe",
                "account_type": "starter"
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
    industry: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request."""
    token: str
    new_password: str = Field(..., min_length=8)


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
    signup_request: UserSignupRequest,
    response: Response,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Sign up a new user with trial period."""
    # Validate account type
    valid_plans = ['starter', 'professional', 'enterprise']
    if signup_request.account_type not in valid_plans:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid account_type. Must be one of: {', '.join(valid_plans)}"
        )

    try:
        user = AuthService.create_user(
            db=db,
            email=signup_request.email,
            password=signup_request.password,
            name=signup_request.name,
            referred_by_code=signup_request.referral_code
        )

        # Set account type and start plan-specific trial
        user.account_type = signup_request.account_type
        db.commit()

        # Start trial (14 days for all paid tiers)
        TrialService.start_trial(user, db, plan_name=signup_request.account_type)

        # Include company_id in JWT token
        token_data = {
            "sub": user.email,
            "user_id": str(user.id),
            "role": user.role,
            "company_id": str(user.company_id) if user.company_id else None,
            "account_type": user.account_type
        }

        access_token = AuthService.create_access_token(data=token_data)

        # Create refresh token and set as httpOnly cookie
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        refresh_token = AuthService.create_refresh_token(
            db=db,
            user_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Set refresh token as httpOnly cookie (7 days)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            path="/"
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
        # Log the error but don't expose internal details to client
        print(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Signup failed. Please try again later.")


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
        "starter": {
            "trial_days": TrialService.get_trial_days('starter'),
            "description": "14-day free trial - Dashboard + vulnerability scanning, 5 assets max"
        },
        "professional": {
            "trial_days": TrialService.get_trial_days('professional'),
            "description": "14-day free trial - Unlimited assets, 10 team members, full features"
        },
        "enterprise": {
            "trial_days": TrialService.get_trial_days('enterprise'),
            "description": "14-day free trial - Everything unlimited, priority support"
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
    business_request: BusinessRegisterRequest,
    response: Response,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Register a new business."""
    try:
        result = AuthService.register_business(
            db=db,
            company_name=business_request.company_name,
            email=business_request.email,
            password=business_request.password,
            name=business_request.name,
            country=business_request.country,
            domain=business_request.domain,
            phone=business_request.phone,
            size=business_request.size,
            industry=business_request.industry
        )

        # Start 14-day trial for business (professional plan)
        user = result["user"]
        user.account_type = 'professional'
        db.commit()
        TrialService.start_trial(user, db, plan_name='professional')

        # Create refresh token and set as httpOnly cookie
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        refresh_token = AuthService.create_refresh_token(
            db=db,
            user_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Set refresh token as httpOnly cookie (7 days)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            path="/"
        )

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
                "plan": result["company"].plan_id,
                "industry": getattr(result["company"], "industry", None)
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the error but don't expose internal details to client
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again later.")


@router.post("/login")
async def login(
    response: Response,
    request: Request,
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

    # Include company_id in JWT token payload
    token_data = {
        "sub": user.email,
        "user_id": str(user.id),
        "role": user.role,
        "company_id": str(user.company_id) if user.company_id else None,
        "account_type": user.account_type
    }

    print(f"[LOGIN] Creating token for {user.email}")
    print(f"[LOGIN] Token data: {token_data}")

    access_token = AuthService.create_access_token(data=token_data)

    # Create refresh token and set as httpOnly cookie
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    refresh_token = AuthService.create_refresh_token(
        db=db,
        user_id=str(user.id),
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Set refresh token as httpOnly cookie (7 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="lax",  # CSRF protection
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        path="/"
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
async def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    response = {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at,
        "account_type": current_user.account_type,
        "company_id": str(current_user.company_id) if current_user.company_id else None
    }

    # Add company data if user has a company
    if current_user.company_id:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if company:
            response["company"] = {
                "id": str(company.id),
                "name": company.name,
                "country": company.country,
                "plan": company.plan_id
            }

    print(f"[GET /me] User: {current_user.email}, Company ID: {current_user.company_id}")

    return response


@router.post("/refresh")
async def refresh_access_token(
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token from httpOnly cookie.
    Returns a new access token.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    # Verify refresh token and get user
    user = AuthService.verify_refresh_token(db, refresh_token)

    if not user:
        # Clear invalid cookie
        response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Create new access token
    token_data = {
        "sub": user.email,
        "user_id": str(user.id),
        "role": user.role,
        "company_id": str(user.company_id) if user.company_id else None,
        "account_type": user.account_type
    }

    access_token = AuthService.create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Logout user and revoke refresh token."""
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        # Revoke the refresh token
        AuthService.revoke_refresh_token(db, refresh_token)

    # Clear the refresh token cookie
    response.delete_cookie(key="refresh_token", path="/")

    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request password reset email.
    Generates a reset token and sends email with reset link.
    """
    try:
        import secrets
        from datetime import datetime as dt, timedelta, timezone
        import traceback

        print(f"\n[FORGOT-PASSWORD] Starting for email: {request.email}")

        user = db.query(User).filter(User.email == request.email).first()

        # Always return success even if email doesn't exist (security best practice)
        if not user:
            print(f"[FORGOT-PASSWORD] User not found: {request.email}")
            return {"message": "If that email exists, a reset link has been sent"}

        print(f"[FORGOT-PASSWORD] User found: {user.email}")

        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        print(f"[FORGOT-PASSWORD] Token generated")

        # Store token in user record (expires in 1 hour) - use timezone-aware datetime
        user.reset_token = reset_token
        user.reset_token_expires = dt.now(timezone.utc) + timedelta(hours=1)
        print(f"[FORGOT-PASSWORD] About to commit to database...")
        db.commit()
        print(f"[FORGOT-PASSWORD] Database commit successful!")

        # Send password reset email via EmailService
        try:
            reset_link = f"https://www.africybertrust.com/reset-password?token={reset_token}"
            print(f"[FORGOT-PASSWORD] About to send email to: {user.email}")

            # Send email to the customer who requested password reset
            EmailService.send_password_reset_email(
                to_email=user.email,  # Send to the customer's email
                reset_link=reset_link
            )

            # Also print to console for development
            print(f"\n{'='*60}")
            print(f"PASSWORD RESET LINK FOR: {user.email}")
            print(f"Link: {reset_link}")
            print(f"Email sent to: {user.email} (FROM: africybersolution@gmail.com)")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"[FORGOT-PASSWORD] ❌ Error sending email: {e}")
            print(f"[FORGOT-PASSWORD] Traceback: {traceback.format_exc()}")
            # Print link to console as fallback
            print(f"\nPassword reset link: https://www.africybertrust.com/reset-password?token={reset_token}\n")
            # Still return success to user

        print(f"[FORGOT-PASSWORD] ✅ Complete!")
        return {"message": "If that email exists, a reset link has been sent"}

    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print(f"[FORGOT-PASSWORD] 🔥 CRITICAL ERROR!")
        print(f"Error: {e}")
        print(f"Type: {type(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        print(f"{'='*60}\n")
        # Still return success to user (security practice)
        return {"message": "If that email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using reset token from email.
    """
    from datetime import datetime, timezone
    from app.services.auth_service import AuthService

    # Find user with this reset token
    user = db.query(User).filter(User.reset_token == request.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check if token is expired (use timezone-aware datetime)
    if not user.reset_token_expires or user.reset_token_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )

    # Update password
    user.hashed_password = AuthService.hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password successfully reset. You can now login with your new password."}
