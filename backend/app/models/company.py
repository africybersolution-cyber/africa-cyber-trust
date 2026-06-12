"""Company model."""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class SubscriptionPlan(str, enum.Enum):
    """Subscription plan enum."""
    FREE = "free"
    STARTER = "starter"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class Company(Base):
    """Company model."""

    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)  # "1-10", "11-50", etc.
    plan_id = Column(Enum(SubscriptionPlan), nullable=False, default=SubscriptionPlan.FREE, index=True)
    
    # Limits based on plan
    max_assets = Column(Integer, default=5)
    max_team_members = Column(Integer, default=1)
    max_scans_per_day = Column(Integer, default=10)
    
    # API access
    api_key = Column(String(255), unique=True, nullable=True)
    api_enabled = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assets = relationship("Asset", back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"
