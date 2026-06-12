"""Asset model."""
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class AssetType(str, enum.Enum):
    """Asset type enum."""
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    API_ENDPOINT = "api_endpoint"
    MOBILE_APP = "mobile_app"
    IP_ADDRESS = "ip_address"
    IP_RANGE = "ip_range"


class VerificationStatus(str, enum.Enum):
    """Verification status enum."""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class VerificationMethod(str, enum.Enum):
    """Verification method enum."""
    DNS_TXT = "dns_txt"
    HTML_FILE = "html_file"
    ADMIN_EMAIL = "admin_email"
    SIGNED_AUTHORIZATION = "signed_authorization"
    MANUAL_APPROVAL = "manual_approval"


class Asset(Base):
    """Asset model for company-owned digital assets."""

    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # Friendly name
    type = Column(Enum(AssetType), nullable=False, index=True)
    value = Column(Text, nullable=False)  # Domain, IP, app package name, etc.
    description = Column(Text, nullable=True)

    # Verification
    verification_status = Column(Enum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING, index=True)
    verification_method = Column(Enum(VerificationMethod), nullable=True)
    verification_token = Column(String(255), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Monitoring
    scan_enabled = Column(Boolean, default=True)
    scan_interval = Column(String(50), default="24h")  # Scan frequency
    status = Column(String(50), default="pending")  # healthy, warning, critical
    score = Column(String(50), nullable=True)  # Security score
    alerts_enabled = Column(Boolean, default=True)
    last_scanned_at = Column(DateTime(timezone=True), nullable=True)
    next_scan_at = Column(DateTime(timezone=True), nullable=True)

    # Security scanning results
    security_score = Column(Integer, nullable=True, default=0)
    findings_count = Column(Integer, nullable=True, default=0)

    # Mobile app specific fields
    app_file_path = Column(String(500), nullable=True)  # Path to uploaded APK/IPA
    app_package_name = Column(String(255), nullable=True)  # com.example.app
    app_version = Column(String(50), nullable=True)  # 1.0.0
    app_version_code = Column(Integer, nullable=True)  # 1
    app_size_mb = Column(Integer, nullable=True)  # File size in MB
    app_platform = Column(String(20), nullable=True)  # android or ios

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="assets")
    scan_jobs = relationship("ScanJob", back_populates="asset")
    scans = relationship("Scan", back_populates="asset", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="asset")
    verification_history = relationship("VerificationHistory", back_populates="asset", cascade="all, delete-orphan")
    verification_tokens = relationship("VerificationToken", back_populates="asset", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="asset")

    def __repr__(self):
        return f"<Asset {self.type.value}: {self.value}>"
