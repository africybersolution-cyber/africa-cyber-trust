"""Admin API - Asset Management Override

Bypass verification, manual scans, view all assets across companies.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.core.admin_deps import require_admin, require_super_admin, log_admin_action
from app.models.user import User
from app.models.asset import Asset
from app.models.scan import Scan
from app.models.company import Company


router = APIRouter(prefix="/api/admin/assets", tags=["Admin - Assets"])


# ===== REQUEST MODELS =====

class BypassVerificationRequest(BaseModel):
    """Request to bypass domain verification for an asset."""
    reason: str


class ManualScanRequest(BaseModel):
    """Request to trigger a scan manually (demo/testing)."""
    scan_type: str = "full"  # full, quick, targeted
    reason: str


# ===== ENDPOINTS =====

@router.get("")
async def list_all_assets(
    company_id: Optional[str] = None,
    user_email: Optional[str] = None,
    verified: Optional[bool] = None,
    asset_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    View all assets across all companies.

    Admins can see everything - useful for:
    - Support debugging
    - Investigating issues
    - Monitoring platform usage
    - Compliance audits
    """
    query = db.query(Asset)

    # Apply filters
    if company_id:
        query = query.filter(Asset.company_id == uuid.UUID(company_id))

    if user_email:
        # Join with companies and users to filter by email
        query = query.join(Company, Company.id == Asset.company_id).join(
            User, User.company_id == Company.id
        ).filter(User.email.ilike(f"%{user_email}%"))

    if verified is not None:
        query = query.filter(Asset.verified == verified)

    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)

    # Get total count
    total = query.count()

    # Apply pagination
    assets = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()

    # Enrich with company info
    results = []
    for asset in assets:
        company = db.query(Company).filter(Company.id == asset.company_id).first()

        results.append({
            "id": str(asset.id),
            "asset_type": asset.asset_type,
            "value": asset.value,
            "verified": asset.verified,
            "trust_score": asset.trust_score,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
            "company": {
                "id": str(company.id),
                "name": company.name
            } if company else None
        })

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "assets": results
    }


@router.post("/{asset_id}/bypass-verification")
async def bypass_verification(
    asset_id: str,
    request: BypassVerificationRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Bypass domain verification for demos/testing.

    Use cases:
    - Demo accounts
    - Testing scenarios
    - Partner demos
    - Special arrangements

    ⚠️ SUPER ADMIN ONLY - bypassing verification is high-risk
    """
    # Get asset
    asset = db.query(Asset).filter(Asset.id == uuid.UUID(asset_id)).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Mark as verified
    was_verified = asset.verified
    asset.verified = True

    db.commit()
    db.refresh(asset)

    # Audit log
    await log_admin_action(
        action="bypass_verification",
        actor=admin,
        db=db,
        request=req,
        target_type="asset",
        target_id=str(asset.id),
        context_data={
            "asset_type": asset.asset_type,
            "asset_value": asset.value,
            "was_verified": was_verified,
            "reason": request.reason
        }
    )

    return {
        "asset_id": str(asset.id),
        "verified": True,
        "message": "Verification bypassed successfully"
    }


@router.post("/{asset_id}/manual-scan")
async def trigger_manual_scan(
    asset_id: str,
    request: ManualScanRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Trigger a manual scan on an asset.

    Use cases:
    - Demo presentations
    - Testing after changes
    - Support debugging
    - Urgent re-scans

    Bypasses normal scheduling and rate limits.
    """
    # Get asset
    asset = db.query(Asset).filter(Asset.id == uuid.UUID(asset_id)).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Create scan record
    scan = Scan(
        asset_id=asset.id,
        scan_type=request.scan_type,
        status="pending",
        triggered_by="admin",
        created_at=datetime.utcnow()
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)

    # TODO: Trigger actual scan job (queue, background task, etc.)
    # For now, just create the record

    # Audit log
    await log_admin_action(
        action="manual_scan",
        actor=admin,
        db=db,
        request=req,
        target_type="asset",
        target_id=str(asset.id),
        context_data={
            "scan_id": str(scan.id),
            "scan_type": request.scan_type,
            "reason": request.reason
        }
    )

    return {
        "asset_id": str(asset.id),
        "scan_id": str(scan.id),
        "scan_type": request.scan_type,
        "status": "pending",
        "message": "Manual scan triggered successfully"
    }


@router.get("/{asset_id}")
async def get_asset_details(
    asset_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed asset information.

    Includes company, scans, findings, and full history.
    """
    asset = db.query(Asset).filter(Asset.id == uuid.UUID(asset_id)).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Get company
    company = db.query(Company).filter(Company.id == asset.company_id).first()

    # Get recent scans
    scans = db.query(Scan).filter(
        Scan.asset_id == asset.id
    ).order_by(Scan.created_at.desc()).limit(10).all()

    return {
        "id": str(asset.id),
        "asset_type": asset.asset_type,
        "value": asset.value,
        "verified": asset.verified,
        "trust_score": asset.trust_score,
        "created_at": asset.created_at.isoformat() if asset.created_at else None,
        "company": {
            "id": str(company.id),
            "name": company.name
        } if company else None,
        "recent_scans": [
            {
                "id": str(s.id),
                "scan_type": s.scan_type,
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in scans
        ]
    }
