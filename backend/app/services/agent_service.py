"""Agent and commission management service."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.agent import Agent, Commission, AgentPayout, AgentMonthlySales
from app.models.subscription import Payment
from app.models.user import User
import uuid


class AgentService:
    """Service for managing agents and commissions."""

    @staticmethod
    def create_agent(
        db: Session,
        user_id: uuid.UUID,
        country: str,
        parent_referral_code: Optional[str] = None
    ) -> Agent:
        """
        Create a new agent application.

        Args:
            user_id: User who is applying to be an agent
            country: ISO country code (e.g., "RW" for Rwanda)
            parent_referral_code: Optional referral code of parent agent (for MLM)

        Returns:
            Created Agent object with status='pending'
        """
        # Generate unique referral code
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Use first 8 chars of name + random number
        base_code = user.name[:3].upper().replace(" ", "") + str(uuid.uuid4())[:5].upper()
        referral_code = base_code

        # Find parent agent if code provided
        parent_agent = None
        if parent_referral_code:
            parent_agent = db.query(Agent).filter(
                Agent.referral_code == parent_referral_code.upper()
            ).first()

        # Create agent
        agent = Agent(
            user_id=user_id,
            referral_code=referral_code,
            country=country.upper(),
            status="pending",
            tier="bronze",
            parent_agent_id=parent_agent.id if parent_agent else None
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        return agent

    @staticmethod
    def calculate_commission(
        db: Session,
        payment: Payment,
        agent: Agent,
        commission_type: str = "direct"
    ) -> Optional[Commission]:
        """
        Calculate and create commission for an agent.

        Args:
            payment: Payment object that triggered the commission
            agent: Agent who earns the commission
            commission_type: Type of commission (direct, override, country_manager_bonus)

        Returns:
            Created Commission object
        """
        # Get commission rate based on type and tier
        if commission_type == "direct":
            rate = agent.get_commission_rate()
        elif commission_type == "override":
            rate = 0.05  # 5% override for parent agent
        elif commission_type == "country_manager_bonus":
            rate = 0.03  # 3% for country manager
        else:
            raise ValueError(f"Unknown commission type: {commission_type}")

        commission_amount = Decimal(str(payment.amount)) * Decimal(str(rate))

        # Check if commission already exists (idempotency)
        existing = db.query(Commission).filter(
            Commission.payment_id == payment.id,
            Commission.agent_id == agent.id,
            Commission.commission_type == commission_type
        ).first()

        if existing:
            return existing

        # Create commission
        commission = Commission(
            agent_id=agent.id,
            payment_id=payment.id,
            customer_user_id=payment.user_id,
            amount=payment.amount,
            commission_rate=Decimal(str(rate * 100)),  # Store as percentage
            commission_amount=commission_amount,
            tier=agent.tier,
            commission_type=commission_type,
            status="pending"
        )

        db.add(commission)

        # Update agent totals
        agent.total_commissions = (agent.total_commissions or Decimal(0)) + commission_amount
        agent.monthly_sales = (agent.monthly_sales or Decimal(0)) + Decimal(str(payment.amount))
        agent.total_sales = (agent.total_sales or Decimal(0)) + Decimal(str(payment.amount))

        # Update tier if needed
        new_tier = agent.calculate_tier()
        if new_tier != agent.tier:
            agent.tier = new_tier

        db.commit()
        db.refresh(commission)

        return commission

    @staticmethod
    def process_payment_commissions(db: Session, payment: Payment) -> List[Commission]:
        """
        Process all commissions for a payment.

        Creates commissions for:
        1. Direct agent (if customer was referred)
        2. Parent agent (5% override if agent has parent)
        3. Country manager (3% if exists for the country)

        Args:
            payment: Completed payment

        Returns:
            List of created Commission objects
        """
        commissions = []

        # Get customer
        customer = db.query(User).filter(User.id == payment.user_id).first()
        if not customer or not customer.agent_referred_by:
            return commissions  # No agent referral

        # Find referring agent
        agent = db.query(Agent).filter(
            Agent.referral_code == customer.agent_referred_by,
            Agent.status == "approved"
        ).first()

        if not agent:
            return commissions

        # 1. Direct commission
        direct_commission = AgentService.calculate_commission(
            db, payment, agent, "direct"
        )
        if direct_commission:
            commissions.append(direct_commission)

        # 2. Override commission (for parent agent)
        if agent.parent_agent:
            parent = db.query(Agent).filter(
                Agent.id == agent.parent_agent_id,
                Agent.status == "approved"
            ).first()
            if parent:
                override_commission = AgentService.calculate_commission(
                    db, payment, parent, "override"
                )
                if override_commission:
                    commissions.append(override_commission)

        # 3. Country manager bonus
        country_manager = db.query(Agent).filter(
            Agent.country == payment.country,
            Agent.is_country_manager == True,
            Agent.status == "approved"
        ).first()

        if country_manager and country_manager.id != agent.id:
            cm_commission = AgentService.calculate_commission(
                db, payment, country_manager, "country_manager_bonus"
            )
            if cm_commission:
                commissions.append(cm_commission)

        return commissions

    @staticmethod
    def get_agent_stats(db: Session, agent_id: uuid.UUID) -> dict:
        """Get statistics for an agent."""
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return {}

        # Total commissions by type
        commissions_by_type = db.query(
            Commission.commission_type,
            func.sum(Commission.commission_amount).label("total"),
            func.count(Commission.id).label("count")
        ).filter(
            Commission.agent_id == agent_id
        ).group_by(Commission.commission_type).all()

        # Pending commissions
        pending_amount = db.query(
            func.sum(Commission.commission_amount)
        ).filter(
            Commission.agent_id == agent_id,
            Commission.status == "pending"
        ).scalar() or Decimal(0)

        # Paid commissions
        paid_amount = db.query(
            func.sum(Commission.commission_amount)
        ).filter(
            Commission.agent_id == agent_id,
            Commission.status == "paid"
        ).scalar() or Decimal(0)

        # Total customers referred
        total_customers = db.query(func.count(User.id)).filter(
            User.agent_referred_by == agent.referral_code
        ).scalar() or 0

        # Sub-agents
        sub_agents_count = db.query(func.count(Agent.id)).filter(
            Agent.parent_agent_id == agent_id,
            Agent.status == "approved"
        ).scalar() or 0

        return {
            "agent_id": str(agent_id),
            "referral_code": agent.referral_code,
            "tier": agent.tier,
            "commission_rate": agent.get_commission_rate(),
            "total_sales": float(agent.total_sales or 0),
            "monthly_sales": float(agent.monthly_sales or 0),
            "total_commissions": float(agent.total_commissions or 0),
            "pending_commissions": float(pending_amount),
            "paid_commissions": float(paid_amount),
            "total_customers": total_customers,
            "sub_agents": sub_agents_count,
            "demo_scans_remaining": agent.demo_scans_remaining,
            "commissions_by_type": [
                {
                    "type": row.commission_type,
                    "total": float(row.total or 0),
                    "count": row.count
                }
                for row in commissions_by_type
            ]
        }

    @staticmethod
    def reset_monthly_sales(db: Session):
        """
        Reset monthly sales for all agents at end of month.

        Called by a scheduled job at the start of each month.
        """
        current_month = datetime.utcnow().strftime("%Y-%m")

        # Get all agents
        agents = db.query(Agent).all()

        for agent in agents:
            # Save to history
            monthly_record = AgentMonthlySales(
                agent_id=agent.id,
                month_year=current_month,
                total_sales=agent.monthly_sales or Decimal(0),
                total_commissions=agent.total_commissions or Decimal(0),
                tier_at_month_end=agent.tier
            )
            db.add(monthly_record)

            # Reset monthly sales
            agent.monthly_sales = Decimal(0)

            # Recalculate tier (will drop to bronze if no sales)
            agent.tier = agent.calculate_tier()

        db.commit()
        print(f"Reset monthly sales for {len(agents)} agents")
