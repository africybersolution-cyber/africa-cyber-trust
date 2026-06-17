"""User model."""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role enum."""
    NORMAL_USER = "normal_user"
    COMPANY_OWNER = "company_owner"
    COMPANY_ADMIN = "company_admin"
    COMPANY_ANALYST = "company_analyst"
    COMPANY_DEVELOPER = "company_developer"
    COMPANY_VIEWER = "company_viewer"
    PLATFORM_ADMIN = "platform_admin"
    SECURITY_ANALYST = "security_analyst"
    SUPER_ADMIN = "super_admin"  # For admin panel access


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)  # For WhatsApp notifications
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.NORMAL_USER, index=True)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)

    # Trial system fields (Everyone starts with STARTER trial)
    account_type = Column(String(20), default='starter')  # 'starter', 'professional', 'enterprise'
    trial_started_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    trial_status = Column(String(20), default='active')  # 'active', 'expired', 'converted'

    # Password reset fields
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Admin & affiliate fields
    totp_secret = Column(String(64), nullable=True)  # 2FA for admins
    referred_by_code = Column(String(20), nullable=True, index=True)  # Agent referral code
    granted_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Manual grants

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    public_checks = relationship("PublicCheck", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"
