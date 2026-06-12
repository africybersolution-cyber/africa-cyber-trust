"""Scan job model."""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class ScanType(str, enum.Enum):
    """Scan type enum."""
    PUBLIC_CHECK = "public_check"
    VERIFIED_WEB_SCAN = "verified_web_scan"
    API_SECURITY_SCAN = "api_security_scan"
    MOBILE_APP_SCAN = "mobile_app_scan"
    NETWORK_SCAN = "network_scan"


class ScanJobStatus(str, enum.Enum):
    """Scan job status enum."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanJob(Base):
    """Scan job model for background scanning tasks."""

    __tablename__ = "scan_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    scan_type = Column(Enum(ScanType), nullable=False)
    status = Column(Enum(ScanJobStatus), nullable=False, default=ScanJobStatus.QUEUED, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    worker_id = Column(String(255), nullable=True)  # Celery task ID
    error_message = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="scan_jobs")

    def __repr__(self):
        return f"<ScanJob {self.scan_type.value}: {self.status.value}>"
