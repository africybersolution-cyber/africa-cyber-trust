"""Scanning endpoints - Security scanning functionality."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.asset import Asset
from app.models.scan import Scan, Finding
from app.services.scan_service import get_scanner

router = APIRouter()


@router.options("/assets/{asset_id}/scan")
async def start_asset_scan_options(asset_id: str):
    """Handle OPTIONS preflight for scan endpoint."""
    return {}


@router.post("/assets/{asset_id}/scan")
async def start_asset_scan(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a security scan on an asset (runs synchronously)."""
    import traceback

    # Verify asset exists and user has access
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Run scan synchronously (takes ~10 seconds)
    scanner = get_scanner(db)
    try:
        print(f"[SCAN] Starting scan for asset {asset_id} ({asset.name})")
        scan = await scanner.scan_asset(asset_id)
        print(f"[SCAN] Scan completed for {asset_id} - Score: {scan.score}")
    except ImportError as e:
        # Missing Python package
        error_msg = f"Missing dependency: {str(e)}"
        print(f"[SCAN ERROR] ImportError: {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=error_msg)
    except TimeoutError as e:
        # Scan took too long
        error_msg = "Scan timeout - asset may be unreachable"
        print(f"[SCAN ERROR] TimeoutError: {error_msg}")
        raise HTTPException(status_code=502, detail=error_msg)
    except Exception as e:
        # Generic error - log full traceback
        error_msg = str(e)
        print(f"[SCAN ERROR] Exception during scan: {error_msg}")
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Scan failed: {error_msg[:200]}"  # Limit error length
        )

    return {
        "message": "Scan completed",
        "asset_id": asset_id,
        "asset_name": asset.name,
        "score": scan.score,
        "findings_count": scan.findings_count
    }


@router.get("/assets/{asset_id}/scans")
async def list_asset_scans(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all scans for an asset."""
    # Verify access
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get scans
    scans = db.query(Scan).filter(
        Scan.asset_id == asset_id
    ).order_by(Scan.started_at.desc()).all()

    return [{
        "id": str(scan.id),
        "status": scan.status,
        "score": scan.score,
        "findings_count": scan.findings_count,
        "critical_count": scan.critical_count,
        "high_count": scan.high_count,
        "medium_count": scan.medium_count,
        "low_count": scan.low_count,
        "started_at": scan.started_at.isoformat(),
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None
    } for scan in scans]


@router.get("/scans/{scan_id}")
async def get_scan_details(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed scan results including findings."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Verify access
    asset = db.query(Asset).filter(Asset.id == scan.asset_id).first()
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get findings
    findings = db.query(Finding).filter(
        Finding.scan_id == scan_id
    ).order_by(
        Finding.severity.desc(),
        Finding.found_at.desc()
    ).all()

    return {
        "id": str(scan.id),
        "asset_id": str(scan.asset_id),
        "status": scan.status,
        "score": scan.score,
        "findings_count": scan.findings_count,
        "critical_count": scan.critical_count,
        "high_count": scan.high_count,
        "medium_count": scan.medium_count,
        "low_count": scan.low_count,
        "started_at": scan.started_at.isoformat(),
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "findings": [{
            "id": str(f.id),
            "severity": f.severity,
            "title": f.title,
            "description": f.description,
            "recommendation": f.recommendation,
            "category": f.category,
            "resolved": f.resolved
        } for f in findings]
    }


@router.get("/assets/{asset_id}/findings")
async def list_asset_findings(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all unresolved findings for an asset from the latest scan only."""
    # Verify access
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get the latest scan for this asset
    from app.models.scan import Scan
    latest_scan = db.query(Scan).filter(
        Scan.asset_id == asset_id
    ).order_by(Scan.started_at.desc()).first()

    if not latest_scan:
        return []

    # Get unresolved findings from the latest scan only
    findings = db.query(Finding).filter(
        Finding.asset_id == asset_id,
        Finding.scan_id == latest_scan.id,
        Finding.resolved == False
    ).order_by(
        Finding.severity.desc(),
        Finding.found_at.desc()
    ).all()

    return [{
        "id": str(f.id),
        "severity": f.severity,
        "title": f.title,
        "description": f.description,
        "recommendation": f.recommendation,
        "category": f.category,
        "found_at": f.found_at.isoformat()
    } for f in findings]
