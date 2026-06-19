"""Breach monitoring API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.breach import BreachCheck, BreachResult, PasteExposure
from app.services.breach_monitor_service import breach_monitor_service
from app.core.config import settings


router = APIRouter(prefix="/api/breaches", tags=["breaches"])


class BreachCheckRequest(BaseModel):
    """Request to check for breaches."""
    target: str  # Email or domain to check
    check_type: str = "domain"  # 'email' or 'domain'


class BreachCheckResponse(BaseModel):
    """Breach check result."""
    id: str
    check_type: str
    target: str
    breaches_found: int
    pastes_found: int
    total_pwn_count: int
    highest_severity: str | None
    status: str
    checked_at: datetime
    breaches: List[dict]


@router.post("/check")
async def check_for_breaches(
    request: BreachCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check an email or domain for data breaches.

    Returns:
        BreachCheck with all found breaches
    """
    # Create check record
    check = BreachCheck(
        user_id=current_user.id,
        company_id=current_user.company_id,
        check_type=request.check_type,
        target=request.target,
        status="pending"
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    try:
        breaches_data = []
        pastes_data = []

        # Check based on type
        if request.check_type == "email":
            # Email requires API key
            if not settings.WHATSAPP_API_KEY:  # TODO: Add HIBP_API_KEY to config
                raise HTTPException(
                    status_code=503,
                    detail="HaveIBeenPwned API key not configured. Contact support."
                )

            breaches_data = await breach_monitor_service.check_email_breaches(request.target)
            pastes_data = await breach_monitor_service.check_paste_exposures(request.target)

        elif request.check_type == "domain":
            # Domain checks are free (no API key needed)
            breaches_data = await breach_monitor_service.check_domain_breaches(request.target)

        else:
            raise HTTPException(status_code=400, detail="Invalid check_type. Use 'email' or 'domain'")

        # Store breach results
        total_pwn_count = 0
        severities = []

        for breach_data in breaches_data:
            # Calculate severity
            severity = breach_monitor_service.get_severity(breach_data)
            severities.append(severity)
            total_pwn_count += breach_data.get("pwn_count", 0)

            # Create breach result
            breach_result = BreachResult(
                breach_check_id=check.id,
                breach_name=breach_data.get("name"),
                title=breach_data.get("title"),
                domain=breach_data.get("domain"),
                breach_date=breach_data.get("breach_date"),
                added_date=datetime.fromisoformat(breach_data["added_date"].replace("Z", "+00:00")) if breach_data.get("added_date") else None,
                modified_date=datetime.fromisoformat(breach_data["modified_date"].replace("Z", "+00:00")) if breach_data.get("modified_date") else None,
                pwn_count=breach_data.get("pwn_count", 0),
                data_classes=breach_data.get("data_classes", []),
                description=breach_data.get("description", ""),
                is_verified=breach_data.get("is_verified", False),
                is_fabricated=breach_data.get("is_fabricated", False),
                is_sensitive=breach_data.get("is_sensitive", False),
                is_retired=breach_data.get("is_retired", False),
                is_spam_list=breach_data.get("is_spam_list", False),
                severity=severity,
                logo_path=breach_data.get("logo_path", "")
            )
            db.add(breach_result)

        # Store paste exposures
        for paste_data in pastes_data:
            paste = PasteExposure(
                breach_check_id=check.id,
                source=paste_data.get("source"),
                paste_id=paste_data.get("id"),
                title=paste_data.get("title"),
                date=datetime.fromisoformat(paste_data["date"].replace("Z", "+00:00")) if paste_data.get("date") else None,
                email_count=paste_data.get("email_count", 0)
            )
            db.add(paste)

        # Update check record
        check.status = "completed"
        check.breaches_found = len(breaches_data)
        check.pastes_found = len(pastes_data)
        check.total_pwn_count = total_pwn_count
        check.highest_severity = max(severities, key=lambda s: ["low", "medium", "high", "critical"].index(s)) if severities else "none"

        db.commit()
        db.refresh(check)

        # Build response
        breaches_list = [
            {
                "name": b.breach_name,
                "title": b.title,
                "domain": b.domain,
                "breach_date": b.breach_date,
                "pwn_count": b.pwn_count,
                "data_classes": b.data_classes,
                "description": b.description,
                "severity": b.severity,
                "is_verified": b.is_verified,
                "is_sensitive": b.is_sensitive,
            }
            for b in check.breaches
        ]

        return {
            "id": str(check.id),
            "check_type": check.check_type,
            "target": check.target,
            "breaches_found": check.breaches_found,
            "pastes_found": check.pastes_found,
            "total_pwn_count": check.total_pwn_count,
            "highest_severity": check.highest_severity,
            "status": check.status,
            "checked_at": check.checked_at,
            "breaches": breaches_list
        }

    except Exception as e:
        check.status = "failed"
        check.error_message = str(e)
        db.commit()
        print(f"Breach check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Breach check failed. Please try again.")


@router.get("/history")
async def get_breach_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's breach check history."""
    checks = db.query(BreachCheck).filter(
        BreachCheck.user_id == current_user.id
    ).order_by(BreachCheck.checked_at.desc()).limit(50).all()

    return [
        {
            "id": str(check.id),
            "check_type": check.check_type,
            "target": check.target,
            "breaches_found": check.breaches_found,
            "pastes_found": check.pastes_found,
            "highest_severity": check.highest_severity,
            "status": check.status,
            "checked_at": check.checked_at,
        }
        for check in checks
    ]


@router.get("/{check_id}")
async def get_breach_details(
    check_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed results of a breach check."""
    check = db.query(BreachCheck).filter(
        BreachCheck.id == check_id,
        BreachCheck.user_id == current_user.id
    ).first()

    if not check:
        raise HTTPException(status_code=404, detail="Breach check not found")

    breaches_list = [
        {
            "name": b.breach_name,
            "title": b.title,
            "domain": b.domain,
            "breach_date": b.breach_date,
            "pwn_count": b.pwn_count,
            "data_classes": b.data_classes,
            "description": b.description,
            "severity": b.severity,
            "is_verified": b.is_verified,
            "is_sensitive": b.is_sensitive,
            "logo_path": b.logo_path,
        }
        for b in check.breaches
    ]

    pastes_list = [
        {
            "source": p.source,
            "title": p.title,
            "date": p.date,
            "email_count": p.email_count,
        }
        for p in db.query(PasteExposure).filter(PasteExposure.breach_check_id == check.id).all()
    ]

    return {
        "id": str(check.id),
        "check_type": check.check_type,
        "target": check.target,
        "breaches_found": check.breaches_found,
        "pastes_found": check.pastes_found,
        "total_pwn_count": check.total_pwn_count,
        "highest_severity": check.highest_severity,
        "status": check.status,
        "checked_at": check.checked_at,
        "breaches": breaches_list,
        "pastes": pastes_list,
    }
