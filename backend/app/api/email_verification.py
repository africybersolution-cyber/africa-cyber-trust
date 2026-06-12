"""Email verification API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service
import secrets

router = APIRouter()


class SendVerificationEmailRequest(BaseModel):
    """Request to send verification email."""
    email: EmailStr
    company_name: str
    domain: str


class VerifyEmailTokenRequest(BaseModel):
    """Request to verify email token."""
    token: str
    email: EmailStr


# Store tokens temporarily (in production, use Redis or database)
verification_tokens = {}


@router.post("/send-verification-email")
async def send_verification_email(request: SendVerificationEmailRequest):
    """
    Send verification email to the provided email address.

    - **email**: Email address to send verification to (e.g., admin@yourdomain.com)
    - **company_name**: Company name for the email
    - **domain**: Domain being verified
    """
    try:
        # Generate secure token
        token = secrets.token_urlsafe(32)

        # Store token with email and domain
        verification_tokens[token] = {
            "email": request.email,
            "domain": request.domain,
            "company_name": request.company_name
        }

        # Create verification link (frontend will handle this route)
        verification_link = f"http://localhost:3001/business/verify-email?token={token}&email={request.email}"

        # Send email
        success = email_service.send_verification_email(
            to_email=request.email,
            domain=request.domain,
            verification_link=verification_link
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email. Please check email configuration."
            )

        return {
            "success": True,
            "message": f"Verification email sent to {request.email}",
            "email": request.email,
            "domain": request.domain
        }

    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send verification email: {str(e)}"
        )


@router.post("/verify-email-token")
async def verify_email_token(request: VerifyEmailTokenRequest):
    """
    Verify the email token from the verification link.

    - **token**: The verification token from the email link
    - **email**: The email address being verified
    """
    try:
        # Check if token exists
        if request.token not in verification_tokens:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification token"
            )

        # Get stored data
        stored_data = verification_tokens[request.token]

        # Verify email matches
        if stored_data["email"] != request.email:
            raise HTTPException(
                status_code=400,
                detail="Email does not match verification token"
            )

        # Token is valid - remove it (one-time use)
        domain = stored_data["domain"]
        company_name = stored_data["company_name"]
        del verification_tokens[request.token]

        return {
            "success": True,
            "verified": True,
            "message": "Email verified successfully!",
            "domain": domain,
            "company_name": company_name,
            "email": request.email
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error verifying email token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify email token: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "email-verification",
        "smtp_configured": bool(email_service.SENDER_PASSWORD)
    }
