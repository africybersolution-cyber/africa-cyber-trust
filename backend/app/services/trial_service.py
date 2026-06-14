"""Trial management service."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.subscription import Subscription


class TrialService:
    """Manage free trials for users (14 days for all paid tiers)."""

    # Trial periods per plan
    TRIAL_DAYS = {
        'starter': 14,
        'professional': 14,
        'enterprise': 14
    }

    @staticmethod
    def start_trial(user: User, db: Session, plan_name: str = 'starter'):
        """Start trial for new user based on selected plan."""
        trial_days = TrialService.TRIAL_DAYS.get(plan_name, 14)

        user.trial_started_at = datetime.now(timezone.utc)
        user.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=trial_days)
        user.trial_status = 'active'
        user.account_type = plan_name  # Set account type
        db.commit()
        print(f"[TRIAL] Started {trial_days}-day trial for user {user.email} ({plan_name} plan) - ends {user.trial_ends_at}")

    @staticmethod
    def check_trial_active(user: User, db: Session) -> bool:
        """Check if user's trial is still active."""
        # If already marked expired
        if user.trial_status == 'expired':
            return False

        # If no trial end date, no trial
        if not user.trial_ends_at:
            return False

        # Check if trial has expired
        if user.trial_ends_at < datetime.now(timezone.utc):
            user.trial_status = 'expired'
            db.commit()
            print(f"[TRIAL] Expired for user {user.email}")
            return False

        return True

    @staticmethod
    def days_remaining(user: User) -> int:
        """Get days remaining in trial."""
        if not user.trial_ends_at:
            return 0

        delta = user.trial_ends_at - datetime.now(timezone.utc)
        return max(0, delta.days)

    @staticmethod
    def has_active_subscription(user_id, db: Session) -> bool:
        """Check if user has active paid subscription."""
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == 'active',
            Subscription.expires_at > datetime.now(timezone.utc)
        ).first()

        return subscription is not None

    @staticmethod
    def can_use_services(user: User, db: Session) -> bool:
        """Check if user can use services (trial active OR paid subscription)."""
        # Check trial
        if TrialService.check_trial_active(user, db):
            return True

        # Check subscription
        if TrialService.has_active_subscription(user.id, db):
            return True

        return False

    @staticmethod
    def get_trial_days(plan_name: str) -> int:
        """Get trial period for a plan."""
        return TrialService.TRIAL_DAYS.get(plan_name, 14)
