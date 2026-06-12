"""Public background check endpoints for normal users."""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.public_check import (
    PublicCheckURLRequest,
    PublicCheckResponse,
    PublicCheckAppRequest,
    PublicCheckCompanyRequest,
)
from app.services.background_checker import BackgroundCheckerService
from app.services.trust_scorer import TrustScorerService
from app.services.scam_detector_service import scam_detector
from app.services.access_control_service import AccessControlService, AccessLevel
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/url", response_model=PublicCheckResponse)
async def check_url(
    request_data: PublicCheckURLRequest,
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Check if a website is a SCAM or LEGITIMATE.

    This is SAFE for public use - focuses on trust verification, not vulnerability exposure.

    Checks:
    - Domain age (new domains = suspicious)
    - WHOIS privacy (hidden owner = red flag)
    - VirusTotal reputation (malware/phishing blacklists)
    - Google Safe Browsing (dangerous site detection)
    - SSL certificate trust
    - Typosquatting (fake versions of popular sites)
    - Suspicious keywords in domain name

    Access Levels:
    - FREE (no account): 1 scan per day per IP
    - PERSONAL ($5/month): Unlimited scans
    - PROFESSIONAL ($49/month): Unlimited scans + dashboard
    """
    from datetime import datetime
    from app.models.public_check import PublicCheck

    # Try to get authenticated user (optional)
    current_user: Optional[User] = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            current_user = AuthService.get_current_user(db, token)
        except:
            pass  # Invalid token = treat as non-authenticated

    # Get access level
    access_level = AccessControlService.get_user_access_level(current_user, db)

    # Get client IP address
    client_ip = request.client.host

    # FREE users: enforce 1 scan per day limit
    if access_level == AccessLevel.FREE and not current_user:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        scans_today = db.query(PublicCheck).filter(
            PublicCheck.ip_address == client_ip,
            PublicCheck.created_at >= today_start
        ).count()

        if scans_today >= 1:
            raise HTTPException(
                status_code=429,
                detail="Daily limit reached (1 free scan per day). Sign up for unlimited scans starting at $5/month!"
            )

    # Logged-in users with Personal/Professional/Enterprise = unlimited scans
    # (No limit check needed)

    try:
        # Use scam detector (SAFE for public - no vulnerability exposure)
        scam_results = await scam_detector.check_website(request_data.url)

        score = scam_results.get("trust_score", 50)
        risk_level = scam_results.get("risk_level", "medium")
        verdict = scam_results.get("verdict", "Unknown")

        # Get red flags from scam detector
        red_flags = scam_results.get("red_flags", [])
        trust_indicators = scam_results.get("trust_indicators", [])

        # Build summary
        if len(red_flags) == 0:
            summary = f"✅ {verdict} - No major red flags detected."
        elif len(red_flags) <= 2:
            summary = f"⚠️ {verdict} - {len(red_flags)} warning sign(s) detected."
        else:
            summary = f"🚨 {verdict} - {len(red_flags)} red flags found!"

        # Build AI explanation
        domain_info = scam_results.get("domain_info", {})
        age_info = f"Domain is {domain_info.get('age_years', 'unknown')} years old. " if domain_info.get('age_years') else "Domain age unknown. "

        trust_text = ""
        if trust_indicators:
            trust_text = f"Trust indicators: {', '.join(trust_indicators[:3])}. "

        ai_explanation = f"Trust Score: {score}/100. {age_info}{trust_text}{verdict}."

        # Generate safety advice based on risk level
        if risk_level == "low":
            safety_advice = "✅ This website appears legitimate. Always verify URLs and use secure payment methods."
        elif risk_level == "medium":
            safety_advice = "⚠️ Exercise caution. Verify the website is correct before entering personal information or making payments."
        elif risk_level == "high":
            safety_advice = "🚨 HIGH RISK - This website shows multiple red flags. We recommend NOT using this site."
        else:
            safety_advice = "❌ SCAM DETECTED - Do not trust this website. Do not send money or share personal information."

        # Save check to database (link to user if authenticated)
        check_record = PublicCheck(
            user_id=current_user.id if current_user else None,
            input_type="url",
            input_value=request_data.url,
            score=score,
            risk_level=risk_level,
            summary=summary,
            red_flags=red_flags,
            ai_explanation=ai_explanation,
            check_data=scam_results,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent", "")
        )
        db.add(check_record)
        db.commit()
        db.refresh(check_record)

        # Return with proper schema
        return PublicCheckResponse(
            id=str(check_record.id),
            input_type="url",
            input_value=request_data.url,
            score=score,
            risk_level=risk_level,
            summary=summary,
            red_flags=red_flags,
            ai_explanation=ai_explanation,
            safety_advice=safety_advice,
            created_at=check_record.created_at,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security scan failed: {str(e)}")


@router.post("/app", response_model=PublicCheckResponse)
async def check_app(
    request_data: PublicCheckAppRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Run background check on a mobile app.

    Checks:
    - App store reputation and ratings
    - Publisher verification
    - Permissions analysis (if APK provided)
    - Known malware signatures
    - Tracker detection
    """
    # TODO: Implement app checking logic
    raise HTTPException(status_code=501, detail="App checking not yet implemented")


@router.post("/company", response_model=PublicCheckResponse)
async def check_company(
    request_data: PublicCheckCompanyRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Run background check on a company or fintech.

    Checks:
    - Official website verification
    - Business registration signals
    - Domain age and consistency
    - Social media presence
    - User-submitted scam reports
    """
    # TODO: Implement company checking logic
    raise HTTPException(status_code=501, detail="Company checking not yet implemented")


@router.post("/report-scam")
async def report_scam(
    # TODO: Add schema
    db: Session = Depends(get_db),
):
    """
    Submit a scam report for review by security analysts.

    Reports are reviewed before being made public to prevent abuse.
    """
    # TODO: Implement scam reporting
    raise HTTPException(status_code=501, detail="Scam reporting not yet implemented")


@router.get("/my-scans")
async def get_my_scans(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    Get scan history for authenticated user.

    Available to Personal, Professional, and Enterprise users.
    """
    from app.models.public_check import PublicCheck

    # Require authentication
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in to view scan history."
        )

    token = authorization.replace("Bearer ", "")
    current_user = AuthService.get_current_user(db, token)

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    # Get user's scans
    scans = db.query(PublicCheck).filter(
        PublicCheck.user_id == current_user.id
    ).order_by(
        PublicCheck.created_at.desc()
    ).offset(offset).limit(limit).all()

    # Get total count
    total = db.query(PublicCheck).filter(
        PublicCheck.user_id == current_user.id
    ).count()

    return {
        "scans": [
            {
                "id": str(scan.id),
                "input_type": scan.input_type,
                "input_value": scan.input_value,
                "score": scan.score,
                "risk_level": scan.risk_level,
                "summary": scan.summary,
                "created_at": scan.created_at.isoformat()
            }
            for scan in scans
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }
