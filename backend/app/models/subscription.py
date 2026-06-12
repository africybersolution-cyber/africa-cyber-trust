"""Subscription models."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.database import Base


class Subscription(Base):
    """User subscription (time-based, not credit-based)."""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_name = Column(String(50), nullable=False)  # personal, business
    status = Column(String(20), nullable=False, default="active")  # active, expired, cancelled
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=True)

    # Manual access grant fields
    manual_grant = Column(Boolean, default=False)
    granted_by = Column(String(255), nullable=True)
    grant_reason = Column(String, nullable=True)
    custom_price = Column(DECIMAL(10, 2), nullable=True)
    custom_currency = Column(String(3), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Payment(Base):
    """Payment transactions."""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)  # USD, KES, RWF, etc.
    payment_method = Column(String(50), nullable=False)  # mobile_money, card, bank
    provider = Column(String(50), nullable=True)  # MTN, Airtel, Vodacom, etc.
    phone_number = Column(String(20), nullable=True)
    country = Column(String(2), nullable=True)  # KE, RW, UG, etc.
    transaction_id = Column(String(255), nullable=True)  # Our internal ID
    external_reference = Column(String(255), nullable=True)  # PawaPay reference
    status = Column(String(20), nullable=False, default="pending")  # pending, completed, failed, cancelled
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CompanyReport(Base):
    """Company verification reports."""
    __tablename__ = "company_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(255), nullable=False)
    company_tin = Column(String(100), nullable=True)  # Tax ID
    country = Column(String(2), nullable=False)
    report_type = Column(String(50), nullable=False)  # basic, detailed, full_due_diligence
    status = Column(String(20), nullable=False, default="processing")  # processing, completed, failed
    credits_used = Column(Integer, nullable=False, default=1)
    risk_score = Column(Integer, nullable=True)  # 0-100
    report_data = Column(String, nullable=True)  # JSON data
    pdf_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ServiceUsage(Base):
    """Track all service usage for billing."""
    __tablename__ = "service_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    service_type = Column(String(50), nullable=False)  # company_verification, deepfake_detection, etc.
    credits_used = Column(Integer, nullable=False, default=1)
    resource_id = Column(UUID(as_uuid=True), nullable=True)  # ID of the report/scan
    extra_data = Column(String, nullable=True)  # Additional info as JSON
    created_at = Column(DateTime, server_default=func.now())


class ManualAccessGrant(Base):
    """Track manual subscription grants by admin."""
    __tablename__ = "manual_access_grants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    admin_email = Column(String(255), nullable=False)
    plan_name = Column(String(50), nullable=False)
    duration_days = Column(Integer, nullable=False)
    custom_price = Column(DECIMAL(10, 2), nullable=True)
    currency = Column(String(3), nullable=True)
    reason = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
