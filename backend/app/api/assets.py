"""Asset management endpoints for business accounts."""
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.asset import Asset, AssetType
from app.services.access_control_service import AccessControlService

router = APIRouter()


# Pydantic schemas
class AssetCreateRequest(BaseModel):
    """Create asset request."""
    name: str = Field(..., min_length=1)
    asset_type: str = Field(..., pattern="^(domain|subdomain|api_endpoint|mobile_app)$")
    value: str = Field(..., min_length=1)
    description: str = None


class AssetUpdateRequest(BaseModel):
    """Update asset request."""
    name: str = None
    value: str = None
    scan_enabled: bool = None
    alerts_enabled: bool = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_asset(
    request: AssetCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new asset for monitoring."""
    print(f"[CREATE ASSET] User: {current_user.email}")
    print(f"  Name: {request.name}")
    print(f"  Type: {request.asset_type}")
    print(f"  Value: {request.value}")
    print(f"  Company ID: {current_user.company_id}")

    # Check if user has a company
    if not current_user.company_id:
        print(f"[ERROR] User {current_user.email} has no company_id!")
        raise HTTPException(
            status_code=400,
            detail="Only business accounts can add assets. Please create a company first."
        )

    # Check asset limit based on subscription tier
    asset_check = AccessControlService.can_add_asset(current_user, db)
    if not asset_check["can_add"]:
        print(f"[ERROR] Asset limit reached for {current_user.email}")
        print(f"  Current: {asset_check['current_count']}/{asset_check['limit']}")
        raise HTTPException(
            status_code=403,
            detail=asset_check["message"]
        )

    print(f"[ASSET LIMIT] OK - {asset_check['current_count']}/{asset_check['limit']} assets used")

    try:
        # Create asset
        asset = Asset(
            company_id=current_user.company_id,
            name=request.name,
            type=AssetType(request.asset_type.lower()),
            value=request.value,
            description=request.description,
            status="pending",
            score="0",
            scan_enabled=True,
            alerts_enabled=True,
            scan_interval="24h",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        asset.next_scan_at = datetime.utcnow() + timedelta(hours=24)

        db.add(asset)
        db.commit()
        db.refresh(asset)

        print(f"[SUCCESS] Asset created: {asset.id}")
    except Exception as e:
        print(f"[ERROR] Error creating asset: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create asset: {str(e)}")

    return {
        "id": str(asset.id),
        "name": asset.name,
        "type": asset.type.value,
        "value": asset.value,
        "description": asset.description,
        "status": asset.status,
        "score": asset.score,
        "scan_enabled": asset.scan_enabled,
        "alerts_enabled": asset.alerts_enabled,
        "last_scanned_at": asset.last_scanned_at.isoformat() if asset.last_scanned_at else None,
        "created_at": asset.created_at.isoformat(),
        # NEW FIELDS
        "verification_status": asset.verification_status.value if asset.verification_status else "PENDING",
        "verified_at": asset.verified_at.isoformat() if asset.verified_at else None,
        "security_score": asset.security_score if hasattr(asset, 'security_score') else 0,
        "findings_count": asset.findings_count if hasattr(asset, 'findings_count') else 0
    }


@router.get("")
async def list_assets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assets for the current user's company."""
    if not current_user.company_id:
        return []

    assets = db.query(Asset).filter(
        Asset.company_id == current_user.company_id
    ).order_by(Asset.created_at.desc()).all()

    return [
        {
            "id": str(asset.id),
            "name": asset.name,
            "type": asset.type.value,
            "value": asset.value,
            "description": asset.description,
            "status": asset.status,
            "score": asset.score,
            "scan_enabled": asset.scan_enabled,
            "alerts_enabled": asset.alerts_enabled,
            "last_scanned_at": asset.last_scanned_at.isoformat() if asset.last_scanned_at else None,
            "next_scan_at": asset.next_scan_at.isoformat() if asset.next_scan_at else None,
            "created_at": asset.created_at.isoformat(),
            # NEW FIELDS - Verification & Security
            "verification_status": asset.verification_status.value if asset.verification_status else "PENDING",
            "verification_method": asset.verification_method.value if asset.verification_method else None,
            "verified_at": asset.verified_at.isoformat() if asset.verified_at else None,
            "security_score": asset.security_score if hasattr(asset, 'security_score') else 0,
            "findings_count": asset.findings_count if hasattr(asset, 'findings_count') else 0,
            "last_scan_at": asset.last_scan_at.isoformat() if hasattr(asset, 'last_scan_at') and asset.last_scan_at else None
        }
        for asset in assets
    ]


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Check ownership
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(asset)
    db.commit()

    return None


@router.post("/{asset_id}/scan")
async def scan_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger an immediate scan of an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Check ownership
    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    from app.services.security_scanner_service import security_scanner

    try:
        if asset.type.value in ["domain", "subdomain", "api_endpoint"]:
            scan_results = await security_scanner.scan_website(asset.value)

            asset.status = "healthy" if scan_results["score"] >= 80 else "warning" if scan_results["score"] >= 60 else "critical"
            asset.score = str(scan_results["score"])
            asset.last_scanned_at = datetime.utcnow()
            asset.next_scan_at = datetime.utcnow() + timedelta(hours=24)
            asset.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(asset)

            return {
                "asset_id": str(asset.id),
                "status": asset.status,
                "score": asset.score,
                "scan_results": scan_results,
                "scanned_at": asset.last_scanned_at.isoformat()
            }
        else:
            raise HTTPException(status_code=501, detail="Mobile app scanning not yet implemented")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/{asset_id}/verify/start")
async def start_verification(
    asset_id: str,
    method: str = "dns_txt",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Start domain verification process.

    Creates a new verification token and returns instructions for all verification methods.
    Uses the new token service with rate limiting and audit logging.
    """
    # Verify asset exists and user has access
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Import services
    from app.services.verification_service import verification_service
    from app.services.token_service import token_service

    # Get IP address for audit
    ip_address = request.client.host if request else None

    # Create new verification token using token service
    success, token_obj, message = token_service.create_verification_token(
        db=db,
        asset_id=asset_id,
        method=method,
        user_id=str(current_user.id),
        ip_address=ip_address
    )

    if not success:
        raise HTTPException(status_code=429, detail=message)

    # Extract clean domain from URL
    domain = asset.value
    if "://" in domain:
        domain = domain.split("://")[1]
    domain = domain.rstrip("/").split("/")[0]

    # Get verification instructions
    instructions = verification_service.get_verification_instructions(domain, token_obj.token)

    return {
        "asset_id": str(asset.id),
        "domain": domain,
        "token": token_obj.token,
        "token_expires_at": token_obj.expires_at.isoformat(),
        "instructions": instructions,
        "rate_limit_info": {
            "max_attempts_per_hour": 10,
            "token_valid_hours": 48 if method == "dns_txt" else 24
        }
    }


@router.post("/{asset_id}/verify/check")
async def check_verification(
    asset_id: str,
    method: str = "auto",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Check if domain verification is complete.

    Validates the token, performs verification check, logs attempt,
    and updates asset status if successful.
    """
    # Verify asset exists and user has access
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Import services and models
    from app.services.verification_service import verification_service
    from app.services.token_service import token_service
    from app.models.asset import VerificationStatus, VerificationMethod
    from app.models.verification import VerificationHistory, VerificationHistoryStatus

    # Get IP address
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None

    # Get active token for this asset
    active_tokens = token_service.get_asset_tokens(db, asset_id, include_expired=False)

    if not active_tokens:
        raise HTTPException(status_code=400, detail="No active verification token found. Please start verification first.")

    token_obj = active_tokens[0]  # Get most recent active token

    # Extract clean domain
    domain = asset.value
    if "://" in domain:
        domain = domain.split("://")[1]
    domain = domain.rstrip("/").split("/")[0]

    # Create verification history record
    history = VerificationHistory(
        asset_id=asset_id,
        method=method if method != "auto" else "dns_txt",
        status="pending",
        attempted_at=datetime.now(timezone.utc),
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    try:
        # Perform verification check
        success, message, method_used = verification_service.verify_domain(
            domain, token_obj.token, method
        )

        if success:
            # Mark token as used
            token_obj.mark_used()

            # Update asset verification status
            asset.verification_status = VerificationStatus.VERIFIED
            asset.verified_at = datetime.now(timezone.utc)
            asset.verification_method = VerificationMethod.DNS_TXT if method_used == "dns_txt" else VerificationMethod.HTML_FILE
            asset.updated_at = datetime.now(timezone.utc)

            # Update history record
            history.status = "success"
            history.completed_at = datetime.now(timezone.utc)
            history.verification_data = {
                "method": method_used,
                "token": token_obj.token[:8] + "...",
                "message": message
            }

            db.commit()
            db.refresh(asset)

            return {
                "verified": True,
                "message": message,
                "method": method_used,
                "verified_at": asset.verified_at.isoformat(),
                "history_id": str(history.id)
            }
        else:
            # Verification failed
            history.status = "failed"
            history.completed_at = datetime.now(timezone.utc)
            history.error_message = message
            history.verification_data = {
                "method": method_used,
                "attempted_method": method,
                "message": message
            }
            db.commit()

            return {
                "verified": False,
                "message": message,
                "method": method_used,
                "history_id": str(history.id)
            }

    except Exception as e:
        # Log error in history
        history.status = "failed"
        history.completed_at = datetime.now(timezone.utc)
        history.error_message = str(e)
        db.commit()

        raise HTTPException(status_code=500, detail=f"Verification check failed: {str(e)}")


@router.post("/{asset_id}/verify/email/send")
async def send_verification_email(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send domain verification email."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    from app.services.verification_service import verification_service
    from app.services.email_service import email_service

    # Generate verification token if not exists
    if not asset.verification_token:
        token = verification_service.generate_verification_token()
        asset.verification_token = token
        asset.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(asset)
    else:
        token = asset.verification_token

    # Generate verification link
    verification_link = f"http://localhost:3001/verify?asset={asset_id}&token={token}"

    # Determine email address - extract clean domain from URL
    domain = asset.value
    # Remove protocol if present
    if "://" in domain:
        domain = domain.split("://")[1]
    # Remove trailing slash if present
    domain = domain.rstrip("/")
    # Remove path if present
    domain = domain.split("/")[0]

    email_address = f"admin@{domain}"

    # Send email
    success = email_service.send_verification_email(
        to_email=email_address,
        domain=domain,
        verification_link=verification_link
    )

    if success:
        return {
            "sent": True,
            "email": email_address,
            "message": f"Verification email sent to {email_address}"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send verification email"
        )


@router.get("/verify/{asset_id}/{token}")
async def verify_via_email_link(
    asset_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Verify domain via email link (public endpoint, no auth required)."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Check if token matches
    if not asset.verification_token:
        raise HTTPException(status_code=400, detail="Verification not started")

    if asset.verification_token != token:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    from app.models.asset import VerificationStatus, VerificationMethod

    # Mark as verified
    asset.verification_status = VerificationStatus.VERIFIED
    asset.verified_at = datetime.utcnow()
    asset.verification_method = VerificationMethod.ADMIN_EMAIL
    asset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(asset)

    return {
        "verified": True,
        "message": "Domain verified successfully via email",
        "asset_id": str(asset.id),
        "domain": asset.value,
        "verified_at": asset.verified_at.isoformat()
    }


@router.patch("/{asset_id}")
async def update_asset_settings(
    asset_id: str,
    settings: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update asset settings (scan_enabled, scan_interval, etc.)."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update allowed fields
    if 'scan_enabled' in settings:
        asset.scan_enabled = settings['scan_enabled']

    if 'scan_interval' in settings:
        asset.scan_interval = settings['scan_interval']

        # Recalculate next_scan_at based on new interval
        if asset.last_scanned_at:
            from datetime import timedelta
            interval_map = {
                '1h': timedelta(hours=1),
                '6h': timedelta(hours=6),
                '12h': timedelta(hours=12),
                '24h': timedelta(hours=24),
                'daily': timedelta(days=1),
                'weekly': timedelta(weeks=1),
                'monthly': timedelta(days=30)
            }
            interval = interval_map.get(asset.scan_interval, timedelta(days=1))
            asset.next_scan_at = asset.last_scanned_at + interval

    asset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(asset)

    return {
        "message": "Asset settings updated",
        "asset_id": str(asset.id),
        "scan_enabled": asset.scan_enabled,
        "scan_interval": asset.scan_interval,
        "next_scan_at": asset.next_scan_at.isoformat() if asset.next_scan_at else None
    }


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an asset.

    Cascades to delete all related:
    - Scans
    - Findings
    - Verification history
    - Verification tokens
    - Audit logs (SET NULL)
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Store asset info for response
    asset_name = asset.name
    asset_value = asset.value

    # Delete asset (cascade will handle related records)
    db.delete(asset)
    db.commit()

    return {
        "message": "Asset deleted successfully",
        "asset_name": asset_name,
        "asset_value": asset_value,
        "deleted_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/mobile-app/upload")
async def upload_mobile_app(
    file: UploadFile = File(...),
    name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and scan a mobile app (APK or IPA file).

    Args:
        file: APK or IPA file
        name: Asset name
    """
    # Validate file type
    if not file.filename.endswith(('.apk', '.ipa')):
        raise HTTPException(
            status_code=400,
            detail="Only APK (Android) or IPA (iOS) files are supported"
        )

    # Check file size (max 500MB)
    file.file.seek(0, 2)
    file_size_bytes = file.file.tell()
    file.file.seek(0)

    if file_size_bytes > 500 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 500MB"
        )

    file_size_mb = file_size_bytes / (1024 * 1024)

    try:
        # Create uploads directory
        upload_dir = "uploads/mobile_apps"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        import uuid as uuid_lib
        file_id = str(uuid_lib.uuid4())
        file_extension = file.filename.split('.')[-1]
        safe_filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(upload_dir, safe_filename)

        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Determine platform
        platform = "android" if file.filename.endswith('.apk') else "ios"

        # Create asset
        asset = Asset(
            company_id=current_user.company_id,
            name=name,
            type=AssetType.MOBILE_APP,
            value=file.filename,
            app_file_path=file_path,
            app_size_mb=int(file_size_mb),
            app_platform=platform,
            scan_enabled=True
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        # Trigger scan for APK (async)
        if platform == "android":
            from app.services.mobile_scan_service import get_mobile_scanner
            import asyncio

            async def run_scan():
                scanner = get_mobile_scanner(db)
                await scanner.scan_apk(str(asset.id))

            # Run scan in background
            asyncio.create_task(run_scan())

            return {
                "asset_id": str(asset.id),
                "message": "APK uploaded successfully! Security scan started.",
                "file_size_mb": round(file_size_mb, 2),
                "platform": platform
            }
        else:
            return {
                "asset_id": str(asset.id),
                "message": "IPA uploaded successfully! iOS scanning coming soon.",
                "file_size_mb": round(file_size_mb, 2),
                "platform": platform
            }

    except Exception as e:
        # Cleanup file if asset creation failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload mobile app: {str(e)}"
        )
