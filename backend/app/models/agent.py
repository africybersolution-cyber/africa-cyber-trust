"""Agent and commission models for affiliate system."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Agent(Base):
    """
    Affiliate agent who refers customers and earns commissions.

    Commission tiers:
    - Bronze: 15% ($0-$500/month)
    - Silver: 20% ($501-$2,000/month)
    - Gold: 25% ($2,001+/month)
    """

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    referral_code = Column(String(20), nullable=False, unique=True, index=True)
    country = Column(String(2), nullable=False, index=True)  # ISO country code
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, approved, rejected, suspended
    tier = Column(String(20), nullable=False, default="bronze")  # bronze, silver, gold

    # Sales & earnings tracking
    total_sales = Column(Numeric(10, 2), nullable=False, default=0)
    total_commissions = Column(Numeric(10, 2), nullable=False, default=0)
    monthly_sales = Column(Numeric(10, 2), nullable=False, default=0)  # Current month

    # Special roles
    is_country_manager = Column(Boolean, nullable=False, default=False)

    # Approval tracking
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Demo account
    demo_scans_remaining = Column(Integer, nullable=False, default=5)

    # Multi-level marketing (MLM)
    parent_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="agent_profile")
    parent_agent = relationship("Agent", remote_side=[id], backref="sub_agents")
    commissions = relationship("Commission", back_populates="agent", cascade="all, delete-orphan")
    payouts = relationship("AgentPayout", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agent {self.referral_code} - {self.tier.upper()} - {self.status}>"

    def get_commission_rate(self) -> float:
        """Get commission rate based on tier."""
        rates = {
            "bronze": 0.15,  # 15%
            "silver": 0.20,  # 20%
            "gold": 0.25     # 25%
        }
        return rates.get(self.tier, 0.15)

    def calculate_tier(self) -> str:
        """Calculate tier based on monthly sales."""
        if self.monthly_sales >= 2001:
            return "gold"
        elif self.monthly_sales >= 501:
            return "silver"
        else:
            return "bronze"


class Commission(Base):
    """
    Commission record for agent earnings.

    Types:
    - direct: Commission from customer they referred
    - override: 5% override from sub-agent's sale
    - country_manager_bonus: 3% from all sales in country
    """

    __tablename__ = "commissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False, index=True)
    customer_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Commission details
    amount = Column(Numeric(10, 2), nullable=False)  # Original payment amount
    commission_rate = Column(Numeric(5, 2), nullable=False)  # e.g., 15.00 for 15%
    commission_amount = Column(Numeric(10, 2), nullable=False)  # Actual commission earned
    tier = Column(String(20), nullable=False)  # Tier at time of commission
    commission_type = Column(String(20), nullable=False)  # direct, override, country_manager_bonus

    # Payment status
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, paid
    paid_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="commissions")

    def __repr__(self):
        return f"<Commission ${self.commission_amount} - {self.commission_type} - {self.status}>"


class AgentPayout(Base):
    """
    Payout request from agent.

    Methods:
    - mobile_money: PawaPay withdrawal
    - crypto: USDT/USDC to wallet
    """

    __tablename__ = "agent_payouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)

    # Payout details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    method = Column(String(20), nullable=False)  # mobile_money, crypto
    destination = Column(Text, nullable=False)  # Phone number or wallet address

    # Status tracking
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, approved, rejected, paid
    requested_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    transaction_reference = Column(Text, nullable=True)  # External transaction ID

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="payouts")

    def __repr__(self):
        return f"<AgentPayout ${self.amount} - {self.method} - {self.status}>"


class AgentMonthlySales(Base):
    """
    Monthly sales tracking for tier calculation.

    Used to calculate agent tier at end of each month.
    """

    __tablename__ = "agent_monthly_sales"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    month_year = Column(String(7), nullable=False)  # Format: "2026-06"
    total_sales = Column(Numeric(10, 2), nullable=False, default=0)
    total_commissions = Column(Numeric(10, 2), nullable=False, default=0)
    tier_at_month_end = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AgentMonthlySales {self.month_year} - ${self.total_sales}>"
