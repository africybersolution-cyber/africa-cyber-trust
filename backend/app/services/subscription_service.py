"""Subscription management (time-based, not credit-based)."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.subscription import Subscription
import uuid


class SubscriptionService:
    """Manage time-based subscriptions."""

    @staticmethod
    def create_subscription(
        db: Session,
        user_id: uuid.UUID,
        plan_name: str,
        duration_days: int = 30
    ) -> Subscription:
        """Create new subscription (30 days for monthly plan)."""
        subscription = Subscription(
            user_id=user_id,
            plan_name=plan_name,
            status="active",
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=duration_days)
        )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def get_active_subscription(db: Session, user_id: uuid.UUID):
        """Get user's active subscription."""
        return db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.expires_at > datetime.utcnow()
        ).first()

    @staticmethod
    def has_active_subscription(user_id: uuid.UUID, db: Session) -> bool:
        """Check if user has active paid subscription."""
        subscription = SubscriptionService.get_active_subscription(db, user_id)
        return subscription is not None
