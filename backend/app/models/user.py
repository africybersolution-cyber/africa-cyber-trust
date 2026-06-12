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
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.NORMAL_USER, index=True)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)

    # Trial system fields
    account_type = Column(String(20), default='personal')  # 'personal' or 'business'
    trial_started_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    trial_status = Column(String(20), default='active')  # 'active', 'expired', 'converted'

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    public_checks = relationship("PublicCheck", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"
