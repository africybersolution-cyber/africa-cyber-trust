"""Fraud detection service for agent referral system."""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

from app.models.user import User
from app.models.agent import Agent, Commission
from app.models.subscription import Payment


class FraudFlag:
    """Fraud flag types."""
    DUPLICATE_PHONE = "duplicate_phone"
    DUPLICATE_EMAIL = "duplicate_email"
    SELF_REFERRAL = "self_referral"
    SUSPICIOUS_IP = "suspicious_ip_pattern"
    INACTIVE_REFERRALS = "inactive_referrals"
    RAPID_SIGNUPS = "rapid_signups"


class FraudDetectionService:
    """Service for detecting fraudulent agent activity."""

    @staticmethod
    def check_user_fraud(db: Session, user_id: uuid.UUID) -> List[Dict]:
        """
        Check a specific user for fraud indicators.

        Returns list of fraud flags with details.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        flags = []

        # Check 1: Duplicate phone number
        if user.phone_number:
            duplicate_phone_count = db.query(func.count(User.id)).filter(
                User.phone_number == user.phone_number,
                User.id != user.id
            ).scalar()

            if duplicate_phone_count > 0:
                flags.append({
                    "type": FraudFlag.DUPLICATE_PHONE,
                    "severity": "high",
                    "details": f"Phone number {user.phone_number} used by {duplicate_phone_count} other accounts",
                    "user_id": str(user_id)
                })

        # Check 2: Duplicate email pattern (similar emails)
        if user.email:
            email_base = user.email.split('@')[0]
            similar_emails = db.query(User).filter(
                User.email.like(f"{email_base}%"),
                User.id != user.id
            ).all()

            if len(similar_emails) > 2:  # More than 2 similar emails
                flags.append({
                    "type": FraudFlag.DUPLICATE_EMAIL,
                    "severity": "medium",
                    "details": f"Email pattern '{email_base}' used by {len(similar_emails)} other accounts",
                    "user_id": str(user_id),
                    "related_users": [str(u.id) for u in similar_emails[:5]]
                })

        # Check 3: Self-referral (user referred by their own agent code)
        if user.referred_by_code:
            agent = db.query(Agent).filter(
                Agent.referral_code == user.referred_by_code
            ).first()

            if agent and agent.user_id == user.id:
                flags.append({
                    "type": FraudFlag.SELF_REFERRAL,
                    "severity": "critical",
                    "details": "User referred by their own agent code",
                    "user_id": str(user_id),
                    "agent_id": str(agent.id)
                })

        return flags

    @staticmethod
    def check_agent_fraud(db: Session, agent_id: uuid.UUID) -> List[Dict]:
        """
        Check an agent for fraudulent activity.

        Returns list of fraud flags with details.
        """
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return []

        flags = []

        # Check 1: Inactive referrals (customers who never paid)
        referred_users = db.query(User).filter(
            User.referred_by_code == agent.referral_code
        ).all()

        if len(referred_users) > 0:
            paid_users = 0
            for user in referred_users:
                payment = db.query(Payment).filter(
                    Payment.user_id == user.id,
                    Payment.status == "completed"
                ).first()
                if payment:
                    paid_users += 1

            inactive_ratio = (len(referred_users) - paid_users) / len(referred_users)

            if len(referred_users) >= 5 and inactive_ratio > 0.8:  # 80%+ inactive
                flags.append({
                    "type": FraudFlag.INACTIVE_REFERRALS,
                    "severity": "high",
                    "details": f"{len(referred_users) - paid_users}/{len(referred_users)} referrals never made a payment",
                    "agent_id": str(agent_id),
                    "inactive_count": len(referred_users) - paid_users
                })

        # Check 2: Rapid signups (multiple referrals in short time)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_referrals = db.query(User).filter(
            User.referred_by_code == agent.referral_code,
            User.created_at >= one_hour_ago
        ).all()

        if len(recent_referrals) >= 10:  # 10+ signups in 1 hour
            flags.append({
                "type": FraudFlag.RAPID_SIGNUPS,
                "severity": "high",
                "details": f"{len(recent_referrals)} referrals in the last hour",
                "agent_id": str(agent_id),
                "count": len(recent_referrals)
            })

        # Check 3: Duplicate phone/email patterns in referrals
        duplicate_phones = db.query(
            User.phone_number,
            func.count(User.id).label("count")
        ).filter(
            User.referred_by_code == agent.referral_code,
            User.phone_number.isnot(None)
        ).group_by(User.phone_number).having(func.count(User.id) > 1).all()

        if duplicate_phones:
            flags.append({
                "type": FraudFlag.DUPLICATE_PHONE,
                "severity": "critical",
                "details": f"{len(duplicate_phones)} phone numbers used by multiple referrals",
                "agent_id": str(agent_id),
                "duplicate_count": len(duplicate_phones)
            })

        return flags

    @staticmethod
    def scan_all_agents(db: Session) -> Dict:
        """
        Scan all agents for fraud.

        Returns summary with flagged agents.
        """
        agents = db.query(Agent).filter(Agent.status == "approved").all()

        flagged_agents = []
        total_flags = 0

        for agent in agents:
            agent_flags = FraudDetectionService.check_agent_fraud(db, agent.id)

            if agent_flags:
                user = db.query(User).filter(User.id == agent.user_id).first()

                flagged_agents.append({
                    "agent_id": str(agent.id),
                    "referral_code": agent.referral_code,
                    "user": {
                        "email": user.email if user else None,
                        "name": user.name if user else None
                    },
                    "flags": agent_flags,
                    "flag_count": len(agent_flags),
                    "highest_severity": max([f["severity"] for f in agent_flags], default="low")
                })

                total_flags += len(agent_flags)

        return {
            "total_agents_scanned": len(agents),
            "flagged_agents": len(flagged_agents),
            "total_flags": total_flags,
            "agents": sorted(flagged_agents, key=lambda x: x["flag_count"], reverse=True)
        }

    @staticmethod
    def get_fraud_score(db: Session, agent_id: uuid.UUID) -> int:
        """
        Calculate fraud score (0-100) for an agent.

        Higher score = more suspicious.
        """
        flags = FraudDetectionService.check_agent_fraud(db, agent_id)

        score = 0

        for flag in flags:
            if flag["severity"] == "critical":
                score += 40
            elif flag["severity"] == "high":
                score += 25
            elif flag["severity"] == "medium":
                score += 15
            else:
                score += 5

        return min(score, 100)  # Cap at 100
