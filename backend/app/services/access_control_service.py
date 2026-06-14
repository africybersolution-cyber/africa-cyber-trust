"""Access control service for enforcing subscription-based permissions."""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.subscription import Subscription
from app.services.trial_service import TrialService
from datetime import datetime
from typing import Optional, Dict, Any


class AccessLevel:
    """Access level constants."""
    FREE = "free"                  # No account, IP-based limit
    STARTER = "starter"             # $19/month - dashboard + vuln scanning, 5 assets
    PROFESSIONAL = "professional"   # $69/month - full features, unlimited assets, 10 team members
    ENTERPRISE = "enterprise"       # $199/month - everything, unlimited team


class AccessControlService:
    """Manage user access based on subscription tier."""

    @staticmethod
    def get_user_access_level(user: Optional[User], db: Session) -> str:
        """
        Determine user's current access level.

        Returns: 'free', 'personal', 'professional', or 'enterprise'
        """
        # No user = free tier
        if not user:
            return AccessLevel.FREE

        # Check if user has active paid subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == 'active',
            Subscription.expires_at > datetime.utcnow()
        ).first()

        if subscription:
            # User has paid subscription - return plan level
            return subscription.plan_name

        # Check if trial is active
        if TrialService.check_trial_active(user, db):
            # Trial active - give access to their selected plan
            return user.account_type or AccessLevel.STARTER

        # No subscription, expired trial = free tier (but logged in)
        return AccessLevel.FREE

    @staticmethod
    def can_access_home_scans(user: Optional[User], db: Session) -> bool:
        """
        Check if user can access home page scanning features.

        Free users: Limited to 1/day (checked elsewhere)
        Paid users (Starter+): Unlimited
        """
        access_level = AccessControlService.get_user_access_level(user, db)
        # Everyone can access home scans (free users have daily limit)
        return True

    @staticmethod
    def can_access_dashboard(user: Optional[User], db: Session) -> bool:
        """
        Check if user can access business dashboard.

        Starter: Limited dashboard (5 assets max)
        Professional/Enterprise: Full dashboard (unlimited assets)
        """
        if not user:
            return False

        access_level = AccessControlService.get_user_access_level(user, db)

        # Starter, Professional, and Enterprise all get dashboard access
        return access_level in [AccessLevel.STARTER, AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE]

    @staticmethod
    def can_access_vulnerability_scanning(user: Optional[User], db: Session) -> bool:
        """
        Check if user can access vulnerability scanning.

        All paid tiers (Starter, Professional, Enterprise).
        """
        return AccessControlService.can_access_dashboard(user, db)

    @staticmethod
    def can_access_continuous_monitoring(user: Optional[User], db: Session) -> bool:
        """
        Check if user can set up continuous monitoring.

        Only Professional and Enterprise.
        """
        return AccessControlService.can_access_dashboard(user, db)

    @staticmethod
    def can_create_team_members(user: Optional[User], db: Session) -> bool:
        """
        Check if user can add team members.

        Only Professional and Enterprise.
        """
        return AccessControlService.can_access_dashboard(user, db)

    @staticmethod
    def get_team_member_limit(user: Optional[User], db: Session) -> int:
        """
        Get maximum number of team members allowed.

        Free/Starter: 1 (just the user, no additional members)
        Professional: 10
        Enterprise: Unlimited (999)
        """
        if not user:
            return 1

        access_level = AccessControlService.get_user_access_level(user, db)

        limits = {
            AccessLevel.FREE: 1,
            AccessLevel.STARTER: 1,
            AccessLevel.PROFESSIONAL: 10,
            AccessLevel.ENTERPRISE: 999
        }

        return limits.get(access_level, 1)

    @staticmethod
    def get_user_permissions(user: Optional[User], db: Session) -> Dict[str, Any]:
        """
        Get comprehensive permission info for user.

        Useful for frontend to show/hide features.
        """
        access_level = AccessControlService.get_user_access_level(user, db)

        return {
            "access_level": access_level,
            "can_access_home_scans": True,  # Everyone
            "can_access_dashboard": access_level in [AccessLevel.STARTER, AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE],
            "can_access_vulnerability_scanning": access_level in [AccessLevel.STARTER, AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE],
            "can_access_continuous_monitoring": access_level in [AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE],
            "can_create_team_members": access_level in [AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE],
            "can_access_reports": access_level in [AccessLevel.STARTER, AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE],
            "can_access_alerts": access_level in [AccessLevel.PROFESSIONAL, AccessLevel.ENTERPRISE],
            "team_member_limit": AccessControlService.get_team_member_limit(user, db),
            "is_trial": TrialService.check_trial_active(user, db) if user else False,
            "trial_days_remaining": TrialService.days_remaining(user) if user else 0
        }

    @staticmethod
    def require_professional_or_higher(user: Optional[User], db: Session) -> bool:
        """
        Check if user has Professional or Enterprise access.

        Raises exception if not authorized.
        """
        if not AccessControlService.can_access_dashboard(user, db):
            from fastapi import HTTPException

            access_level = AccessControlService.get_user_access_level(user, db)

            if access_level == AccessLevel.STARTER:
                raise HTTPException(
                    status_code=403,
                    detail="This feature requires Professional plan. Upgrade to access unlimited assets and team features."
                )
            elif access_level == AccessLevel.FREE:
                raise HTTPException(
                    status_code=403,
                    detail="Please upgrade to Starter plan or higher to access the dashboard."
                )
            else:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied. Professional or Enterprise plan required."
                )

        return True
