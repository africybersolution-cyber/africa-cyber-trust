"""Public check model."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class RiskLevel(str, enum.Enum):
    """Risk level enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class PublicCheck(Base):
    """Public check model for background checks run by normal users."""

    __tablename__ = "public_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    input_type = Column(String(50), nullable=False, index=True)  # 'url', 'app', 'company', 'payment_link', 'photo', 'video'
    input_value = Column(Text, nullable=False)
    score = Column(Integer, nullable=True)  # 0-100
    risk_level = Column(String(20), nullable=True)
    summary = Column(Text, nullable=True)
    red_flags = Column(JSON, nullable=True)  # Array of red flag objects
    ai_explanation = Column(Text, nullable=True)
    check_data = Column(JSON, nullable=True)  # Store all check results
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="public_checks")

    def __repr__(self):
        return f"<PublicCheck {self.input_type}: {self.input_value[:50]}>"
