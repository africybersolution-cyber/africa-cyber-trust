"""
Verification system models for tracking verification attempts, tokens, and audit logs.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.database import Base


class VerificationHistoryStatus(str, enum.Enum):
    """Status of a verification attempt."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"


class VerificationHistoryMethod(str, enum.Enum):
    """Method used for verification."""
    DNS_TXT = "dns_txt"
    HTML_FILE = "html_file"
    ADMIN_EMAIL = "admin_email"
    META_TAG = "meta_tag"
    CNAME = "cname"


class AuditAction(str, enum.Enum):
    """Actions that can be logged in audit trail."""
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_COMPLETED = "verification_completed"
    VERIFICATION_FAILED = "verification_failed"
    TOKEN_GENERATED = "token_generated"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_USED = "token_used"
    MANUAL_APPROVAL = "manual_approval"
    MANUAL_REJECTION = "manual_rejection"
    RE_VERIFICATION_REQUIRED = "re_verification_required"


class VerificationHistory(Base):
    """
    Track all verification attempts for complete audit trail.

    Records every verification attempt whether successful or not,
    including method used, timing, and any error details.
    """
    __tablename__ = "verification_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    method = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)
    attempted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(100), nullable=True)
    user_agent = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    verification_data = Column(JSONB, nullable=True)  # Store proof of verification

    # Relationships
    asset = relationship("Asset", back_populates="verification_history")

    def __repr__(self):
        return f"<VerificationHistory {self.method.value} - {self.status.value} for asset {self.asset_id}>"


class VerificationToken(Base):
    """
    Manage verification tokens with expiration and usage tracking.

    Each token is single-use and has a 48-hour expiration by default.
    Tokens are invalidated after use or expiration.
    """
    __tablename__ = "verification_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    method = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    is_valid = Column(Boolean, nullable=False, default=True, index=True)

    # Relationships
    asset = relationship("Asset", back_populates="verification_tokens")

    def is_expired(self) -> bool:
        """Check if token has expired."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        return now > self.expires_at

    def mark_used(self):
        """Mark token as used."""
        from datetime import timezone
        self.used_at = datetime.now(timezone.utc)
        self.is_valid = False

    def __repr__(self):
        return f"<VerificationToken {self.token[:8]}... for asset {self.asset_id}>"


class AuditLog(Base):
    """
    Complete audit trail of all verification and security activities.

    Logs all significant events for compliance, debugging, and security monitoring.
    Includes IP address and user agent for security analysis.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(100), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    asset = relationship("Asset", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action.value} at {self.created_at}>"
