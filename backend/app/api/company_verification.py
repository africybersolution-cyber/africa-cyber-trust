"""Company verification API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.company_verification_service import CompanyVerificationService
from app.services.subscription_service import SubscriptionService
from pydantic import BaseModel
import uuid
import json

router = APIRouter()


class CompanyVerificationRequest(BaseModel):
    company_name: str
    company_tin: str
    country: str
    report_type: str = "basic"


@router.post("/verify")
async def verify_company(
    request: CompanyVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create company verification report."""
    
    credits = SubscriptionService.get_user_credits(db, current_user.id)
    if credits < 5:
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please upgrade your plan."
        )
    
    try:
        report = await CompanyVerificationService.create_report(
            db=db,
            user_id=current_user.id,
            company_name=request.company_name,
            company_tin=request.company_tin,
            country=request.country,
            report_type=request.report_type
        )
        
        return {
            "report_id": str(report.id),
            "status": report.status,
            "risk_score": report.risk_score,
            "credits_used": report.credits_used,
            "credits_remaining": SubscriptionService.get_user_credits(db, current_user.id)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports for current user."""
    from app.models.subscription import CompanyReport
    
    reports = db.query(CompanyReport).filter(
        CompanyReport.user_id == current_user.id
    ).order_by(CompanyReport.created_at.desc()).all()
    
    return [
        {
            "id": str(r.id),
            "company_name": r.company_name,
            "country": r.country,
            "risk_score": r.risk_score,
            "status": r.status,
            "created_at": r.created_at.isoformat()
        }
        for r in reports
    ]


@router.get("/report/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific report details."""
    from app.models.subscription import CompanyReport
    
    report = db.query(CompanyReport).filter(
        CompanyReport.id == uuid.UUID(report_id),
        CompanyReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report_data = {}
    if report.report_data:
        try:
            report_data = eval(report.report_data)
        except:
            report_data = {}
    
    return {
        "id": str(report.id),
        "company_name": report.company_name,
        "company_tin": report.company_tin,
        "country": report.country,
        "risk_score": report.risk_score,
        "status": report.status,
        "report_data": report_data,
        "created_at": report.created_at.isoformat()
    }
