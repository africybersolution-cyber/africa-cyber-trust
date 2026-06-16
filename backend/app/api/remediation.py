"""Remediation tracking API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.scan import Finding
from app.models.asset import Asset


router = APIRouter(prefix="/api/remediation", tags=["Remediation"])


class UpdateFindingStatusRequest(BaseModel):
    """Request to update finding status."""
    status: str  # 'open', 'in_progress', 'resolved', 'verified', 'false_positive', 'ignored'
    notes: Optional[str] = None
    assignee_id: Optional[str] = None


class MarkResolvedRequest(BaseModel):
    """Request to mark finding as resolved."""
    resolution_notes: str
    request_verification: bool = False  # Request re-scan to verify fix


class VerifyFixRequest(BaseModel):
    """Request to verify a fix."""
    verified: bool  # True = confirmed fixed, False = still vulnerable
    notes: Optional[str] = None


@router.put("/findings/{finding_id}/status")
async def update_finding_status(
    finding_id: str,
    request: UpdateFindingStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update status of a security finding.

    Valid statuses:
    - open: Newly discovered, not yet addressed
    - in_progress: Team is working on fixing it
    - resolved: Fix has been applied
    - verified: Fix has been confirmed by re-scan
    - false_positive: Not actually a vulnerability
    - ignored: Acknowledged but won't fix (risk accepted)
    """
    # Get finding
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Check access (must be from same company)
    asset = db.query(Asset).filter(Asset.id == finding.asset_id).first()
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Validate status
    valid_statuses = ['open', 'in_progress', 'resolved', 'verified', 'false_positive', 'ignored']
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    # Update status
    old_status = finding.status
    finding.status = request.status
    finding.status_changed_at = datetime.now(timezone.utc)
    finding.status_changed_by = current_user.id

    # Update legacy resolved field for backward compatibility
    finding.resolved = request.status in ['resolved', 'verified']
    if finding.resolved and not finding.resolved_at:
        finding.resolved_at = datetime.now(timezone.utc)

    # Update assignee if provided
    if request.assignee_id:
        finding.assignee_id = request.assignee_id

    # Add notes to resolution_notes if provided
    if request.notes:
        if finding.resolution_notes:
            finding.resolution_notes += f"\n\n[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} - Status: {old_status} → {request.status}]\n{request.notes}"
        else:
            finding.resolution_notes = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} - Status: {old_status} → {request.status}]\n{request.notes}"

    db.commit()
    db.refresh(finding)

    return {
        "id": str(finding.id),
        "status": finding.status,
        "previous_status": old_status,
        "changed_at": finding.status_changed_at,
        "changed_by": str(finding.status_changed_by)
    }


@router.put("/findings/{finding_id}/resolve")
async def mark_finding_resolved(
    finding_id: str,
    request: MarkResolvedRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a finding as resolved.

    Optionally trigger a re-scan to verify the fix.
    """
    # Get finding
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Check access
    asset = db.query(Asset).filter(Asset.id == finding.asset_id).first()
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Mark as resolved
    finding.status = "resolved"
    finding.resolved = True
    finding.resolved_at = datetime.now(timezone.utc)
    finding.marked_resolved_by = current_user.id
    finding.resolution_notes = request.resolution_notes
    finding.status_changed_at = datetime.now(timezone.utc)
    finding.status_changed_by = current_user.id

    db.commit()
    db.refresh(finding)

    response = {
        "id": str(finding.id),
        "status": "resolved",
        "resolved_at": finding.resolved_at,
        "resolved_by": str(current_user.id),
        "verification_pending": request.request_verification
    }

    # Trigger re-scan if verification requested
    if request.request_verification:
        # TODO: Trigger targeted re-scan to verify fix
        # For now, just flag it
        response["message"] = "Fix marked as resolved. Re-scan to verify the fix."

    return response


@router.put("/findings/{finding_id}/verify")
async def verify_finding_fix(
    finding_id: str,
    request: VerifyFixRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify that a finding has been fixed.

    This should be called after re-scanning to confirm the vulnerability is gone.
    """
    # Get finding
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Check access
    asset = db.query(Asset).filter(Asset.id == finding.asset_id).first()
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if request.verified:
        # Confirmed fixed
        finding.status = "verified"
        finding.verified_by = current_user.id
        finding.verified_at = datetime.now(timezone.utc)
        finding.status_changed_at = datetime.now(timezone.utc)
        finding.status_changed_by = current_user.id

        if request.notes:
            if finding.resolution_notes:
                finding.resolution_notes += f"\n\n[VERIFIED {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}]\n{request.notes}"
            else:
                finding.resolution_notes = f"[VERIFIED {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}]\n{request.notes}"
    else:
        # Still vulnerable - reopen
        finding.status = "open"
        finding.verified_by = None
        finding.verified_at = None
        finding.resolved = False
        finding.status_changed_at = datetime.now(timezone.utc)
        finding.status_changed_by = current_user.id

        if request.notes:
            if finding.resolution_notes:
                finding.resolution_notes += f"\n\n[VERIFICATION FAILED {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}]\n{request.notes}"
            else:
                finding.resolution_notes = f"[VERIFICATION FAILED {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}]\n{request.notes}"

    db.commit()
    db.refresh(finding)

    return {
        "id": str(finding.id),
        "status": finding.status,
        "verified": request.verified,
        "verified_at": finding.verified_at,
        "verified_by": str(finding.verified_by) if finding.verified_by else None
    }


@router.get("/stats")
async def get_remediation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get remediation statistics for the company.

    Returns counts by status, severity, and time-to-fix metrics.
    """
    # Get all findings for company
    findings = db.query(Finding).join(Asset).filter(
        Asset.company_id == current_user.company_id
    ).all()

    # Count by status
    status_counts = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
        "verified": 0,
        "false_positive": 0,
        "ignored": 0
    }

    # Count by severity
    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0
    }

    # Calculate metrics
    total_findings = len(findings)
    fixed_findings = 0
    avg_time_to_fix_days = 0
    fix_times = []

    for finding in findings:
        # Status count
        if finding.status in status_counts:
            status_counts[finding.status] += 1

        # Severity count
        sev = finding.severity.lower() if finding.severity else "info"
        if sev in severity_counts:
            severity_counts[sev] += 1

        # Time to fix
        if finding.resolved_at and finding.found_at:
            time_delta = finding.resolved_at - finding.found_at
            fix_times.append(time_delta.total_seconds() / 86400)  # Convert to days
            fixed_findings += 1

    if fix_times:
        avg_time_to_fix_days = sum(fix_times) / len(fix_times)

    # Calculate fix rate
    fix_rate = (fixed_findings / total_findings * 100) if total_findings > 0 else 0

    return {
        "total_findings": total_findings,
        "by_status": status_counts,
        "by_severity": severity_counts,
        "metrics": {
            "fixed_count": fixed_findings,
            "fix_rate_percent": round(fix_rate, 1),
            "avg_time_to_fix_days": round(avg_time_to_fix_days, 1),
            "critical_open": status_counts.get("open", 0),  # Simplified - should filter by severity
        }
    }


@router.get("/findings/{finding_id}/history")
async def get_finding_history(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the remediation history/timeline for a finding."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Check access
    asset = db.query(Asset).filter(Asset.id == finding.asset_id).first()
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Build timeline
    timeline = []

    # Found
    timeline.append({
        "event": "discovered",
        "timestamp": finding.found_at,
        "severity": finding.severity,
        "title": finding.title
    })

    # Status changes (parsed from resolution_notes)
    if finding.resolution_notes:
        timeline.append({
            "event": "notes_added",
            "timestamp": finding.status_changed_at,
            "notes": finding.resolution_notes
        })

    # Resolved
    if finding.resolved_at:
        timeline.append({
            "event": "marked_resolved",
            "timestamp": finding.resolved_at,
            "user_id": str(finding.marked_resolved_by) if finding.marked_resolved_by else None
        })

    # Verified
    if finding.verified_at:
        timeline.append({
            "event": "verified_fixed",
            "timestamp": finding.verified_at,
            "user_id": str(finding.verified_by) if finding.verified_by else None
        })

    # Sort by timestamp
    timeline.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min.replace(tzinfo=timezone.utc))

    return {
        "finding_id": str(finding.id),
        "current_status": finding.status,
        "timeline": timeline
    }
