"""Alert models for notification system."""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class AlertSettings(Base):
    """User alert notification settings."""
    __tablename__ = "alert_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)

    # Notification Channels
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    whatsapp_enabled = Column(Boolean, default=False)
    slack_enabled = Column(Boolean, default=False)

    # Contact Details
    email_address = Column(String(255))  # Can override user email
    phone_number = Column(String(50))     # For SMS/WhatsApp
    slack_webhook_url = Column(Text)      # For Slack notifications

    # Alert Types
    critical_issues = Column(Boolean, default=True)
    high_issues = Column(Boolean, default=True)
    medium_issues = Column(Boolean, default=True)
    low_issues = Column(Boolean, default=False)
    scan_complete = Column(Boolean, default=True)
    new_vulnerability = Column(Boolean, default=True)
    asset_offline = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Alert(Base):
    """Alert notification history."""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    # Alert Details
    severity = Column(String(20), nullable=False)  # 'critical', 'high', 'medium', 'low'
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Related Resources
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'), nullable=True)
    asset_name = Column(String(255))
    scan_id = Column(UUID(as_uuid=True), nullable=True)  # No FK - scans table may not exist
    vulnerability_id = Column(String(100))

    # Notification Status
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True))
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime(timezone=True))

    # User Status
    read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
