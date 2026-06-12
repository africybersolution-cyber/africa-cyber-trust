"""Alert settings and notification management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.alert import AlertSettings as AlertSettingsModel, Alert as AlertModel
from app.services.access_control_service import AccessControlService, AccessLevel
from app.services.alert_service import AlertService

router = APIRouter()


# Pydantic Models
class AlertSettings(BaseModel):
    # Notification channels
    email_enabled: bool = True
    sms_enabled: bool = False
    whatsapp_enabled: bool = False
    slack_enabled: bool = False

    # Contact details (optional overrides)
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    slack_webhook_url: Optional[str] = None

    # Alert types
    critical_issues: bool = True
    high_issues: bool = True
    medium_issues: bool = True
    low_issues: bool = False
    scan_complete: bool = True
    new_vulnerability: bool = True
    asset_offline: bool = True


class AlertSettingsResponse(BaseModel):
    user_id: str
    settings: AlertSettings
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/settings", response_model=AlertSettingsResponse)
async def get_alert_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's alert settings.

    **Access:** Professional plan or higher
    """
    # Check access level
    access_level = AccessControlService.get_user_access_level(current_user, db)

    if access_level not in [AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE]:
        raise HTTPException(
            status_code=403,
            detail="Email + SMS alerts are only available on Professional plan ($49/month) or higher. Upgrade to enable notifications."
        )

    # Get or create settings
    settings = db.query(AlertSettingsModel).filter(
        AlertSettingsModel.user_id == current_user.id
    ).first()

    if not settings:
        # Create default settings
        settings = AlertSettingsModel(
            user_id=current_user.id,
            email_address=current_user.email
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return AlertSettingsResponse(
        user_id=str(current_user.id),
        settings=AlertSettings(
            email_enabled=settings.email_enabled,
            sms_enabled=settings.sms_enabled,
            whatsapp_enabled=settings.whatsapp_enabled,
            slack_enabled=settings.slack_enabled,
            email_address=settings.email_address,
            phone_number=settings.phone_number,
            slack_webhook_url=settings.slack_webhook_url,
            critical_issues=settings.critical_issues,
            high_issues=settings.high_issues,
            medium_issues=settings.medium_issues,
            low_issues=settings.low_issues,
            scan_complete=settings.scan_complete,
            new_vulnerability=settings.new_vulnerability,
            asset_offline=settings.asset_offline
        ),
        updated_at=settings.updated_at or settings.created_at
    )


@router.post("/settings", response_model=AlertSettingsResponse)
async def save_alert_settings(
    settings: AlertSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save user's alert settings.

    **Access:** Professional plan or higher
    """
    # Check access level
    access_level = AccessControlService.get_user_access_level(current_user, db)

    if access_level not in [AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE]:
        raise HTTPException(
            status_code=403,
            detail="Email + SMS alerts are only available on Professional plan ($49/month) or higher. Upgrade to enable notifications."
        )

    # Get or create settings
    db_settings = db.query(AlertSettingsModel).filter(
        AlertSettingsModel.user_id == current_user.id
    ).first()

    if not db_settings:
        db_settings = AlertSettingsModel(user_id=current_user.id)
        db.add(db_settings)

    # Update settings
    db_settings.email_enabled = settings.email_enabled
    db_settings.sms_enabled = settings.sms_enabled
    db_settings.whatsapp_enabled = settings.whatsapp_enabled
    db_settings.slack_enabled = settings.slack_enabled

    db_settings.email_address = settings.email_address or current_user.email
    db_settings.phone_number = settings.phone_number
    db_settings.slack_webhook_url = settings.slack_webhook_url

    db_settings.critical_issues = settings.critical_issues
    db_settings.high_issues = settings.high_issues
    db_settings.medium_issues = settings.medium_issues
    db_settings.low_issues = settings.low_issues
    db_settings.scan_complete = settings.scan_complete
    db_settings.new_vulnerability = settings.new_vulnerability
    db_settings.asset_offline = settings.asset_offline

    db.commit()
    db.refresh(db_settings)

    print(f"[ALERTS] ✅ Settings saved for {current_user.email}")
    print(f"   Email: {settings.email_enabled}")
    print(f"   SMS: {settings.sms_enabled} (phone: {settings.phone_number})")
    print(f"   Slack: {settings.slack_enabled}")

    return AlertSettingsResponse(
        user_id=str(current_user.id),
        settings=settings,
        updated_at=db_settings.updated_at or datetime.utcnow()
    )


class AlertHistory(BaseModel):
    id: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    title: str
    message: str
    asset_name: Optional[str]
    timestamp: datetime
    read: bool
    email_sent: bool
    sms_sent: bool

    class Config:
        from_attributes = True


@router.get("/history", response_model=List[AlertHistory])
async def get_alert_history(
    limit: int = 50,
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent alerts for the user.

    **Access:** Professional plan or higher
    """
    # Check access level
    access_level = AccessControlService.get_user_access_level(current_user, db)

    if access_level not in [AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE]:
        raise HTTPException(
            status_code=403,
            detail="Alert history is only available on Professional plan or higher."
        )

    # Build query
    query = db.query(AlertModel).filter(AlertModel.user_id == current_user.id)

    if severity:
        query = query.filter(AlertModel.severity == severity)

    alerts = query.order_by(AlertModel.created_at.desc()).limit(limit).all()

    return [
        AlertHistory(
            id=str(alert.id),
            severity=alert.severity,
            title=alert.title,
            message=alert.message,
            asset_name=alert.asset_name,
            timestamp=alert.created_at,
            read=alert.read,
            email_sent=alert.email_sent,
            sms_sent=alert.sms_sent
        )
        for alert in alerts
    ]


@router.patch("/history/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as read."""
    alert = db.query(AlertModel).filter(
        AlertModel.id == alert_id,
        AlertModel.user_id == current_user.id
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.read = True
    alert.read_at = datetime.utcnow()
    db.commit()

    return {"success": True, "alert_id": str(alert.id), "read": True}


@router.post("/test")
async def send_test_alert(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a test alert to verify notification settings.

    **Access:** Professional plan or higher
    """
    # Check access level
    access_level = AccessControlService.get_user_access_level(current_user, db)

    if access_level not in [AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE]:
        raise HTTPException(
            status_code=403,
            detail="Alerts are only available on Professional plan or higher."
        )

    # Send test alert
    alert = await AlertService.send_alert(
        db=db,
        user=current_user,
        severity="medium",
        title="Test Alert - System Check",
        message="This is a test alert to verify your notification settings are working correctly. If you received this, your alerts are configured properly!",
        asset_name="Test Asset"
    )

    return {
        "success": True,
        "alert_id": str(alert.id),
        "email_sent": alert.email_sent,
        "sms_sent": alert.sms_sent,
        "message": "Test alert sent! Check your email/SMS."
    }
