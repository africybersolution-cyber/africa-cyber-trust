"""Database models for breach monitoring."""
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base


class BreachCheck(Base):
    """Record of a breach check performed on an email/domain."""

    __tablename__ = "breach_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    # What was checked
    check_type = Column(String(20), nullable=False)  # 'email', 'domain', 'password'
    target = Column(String(255), nullable=False, index=True)  # Email or domain checked

    # Results
    breaches_found = Column(Integer, default=0)
    pastes_found = Column(Integer, default=0)
    total_pwn_count = Column(Integer, default=0)  # Total accounts affected across all breaches
    highest_severity = Column(String(20))  # 'critical', 'high', 'medium', 'low', 'none'

    # Status
    status = Column(String(20), default="pending")  # 'pending', 'completed', 'failed'
    error_message = Column(Text)

    # Timestamps
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    breaches = relationship("BreachResult", back_populates="check", cascade="all, delete-orphan")


class BreachResult(Base):
    """Individual breach found for an email/domain."""

    __tablename__ = "breach_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    breach_check_id = Column(UUID(as_uuid=True), ForeignKey("breach_checks.id", ondelete="CASCADE"), nullable=False, index=True)

    # Breach details (from HaveIBeenPwned)
    breach_name = Column(String(100), nullable=False, index=True)
    title = Column(String(255))
    domain = Column(String(255))
    breach_date = Column(String(20))  # YYYY-MM-DD from API
    added_date = Column(DateTime)
    modified_date = Column(DateTime)

    # Impact
    pwn_count = Column(Integer, default=0)  # How many accounts affected
    data_classes = Column(JSON)  # What data was leaked: ["Emails", "Passwords", etc.]
    description = Column(Text)

    # Classification
    is_verified = Column(Boolean, default=False)
    is_fabricated = Column(Boolean, default=False)
    is_sensitive = Column(Boolean, default=False)
    is_retired = Column(Boolean, default=False)
    is_spam_list = Column(Boolean, default=False)

    # Severity (calculated)
    severity = Column(String(20))  # 'critical', 'high', 'medium', 'low'

    # UI
    logo_path = Column(String(500))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    check = relationship("BreachCheck", back_populates="breaches")


class PasteExposure(Base):
    """Paste exposure record (from Pastebin, etc.)."""

    __tablename__ = "paste_exposures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    breach_check_id = Column(UUID(as_uuid=True), ForeignKey("breach_checks.id", ondelete="CASCADE"), nullable=False, index=True)

    # Paste details
    source = Column(String(50))  # 'Pastebin', 'Pastie', etc.
    paste_id = Column(String(100))
    title = Column(String(500))
    date = Column(DateTime)
    email_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
