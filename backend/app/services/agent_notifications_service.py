"""Agent notification scheduling service."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.agent import Agent, Commission
from app.models.user import User
from app.services.whatsapp_service import whatsapp_service


class AgentNotificationsService:
    """Service for scheduled agent notifications."""

    @staticmethod
    def send_monthly_summaries(db: Session) -> dict:
        """
        Send monthly performance summary to all active agents.

        Returns summary of how many notifications were sent.
        """
        # Get all approved agents
        agents = db.query(Agent).filter(Agent.status == "approved").all()

        sent = 0
        failed = 0
        skipped = 0

        for agent in agents:
            user = db.query(User).filter(User.id == agent.user_id).first()
            if not user or not user.phone_number:
                skipped += 1
                continue

            # Get this month's stats
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Monthly commissions
            monthly_commissions = db.query(
                func.sum(Commission.commission_amount)
            ).filter(
                Commission.agent_id == agent.id,
                Commission.created_at >= month_start
            ).scalar() or 0

            # Monthly customers (unique payments this month)
            monthly_customers = db.query(
                func.count(func.distinct(Commission.customer_user_id))
            ).filter(
                Commission.agent_id == agent.id,
                Commission.created_at >= month_start
            ).scalar() or 0

            # Send WhatsApp summary
            try:
                whatsapp_service.send_monthly_summary(
                    to_number=user.phone_number,
                    agent_name=user.name,
                    total_sales=float(agent.monthly_sales or 0),
                    commissions=float(monthly_commissions),
                    customers=monthly_customers
                )
                sent += 1
            except Exception as e:
                print(f"[ERROR] Monthly summary failed for agent {agent.id}: {e}")
                failed += 1

        return {
            "total_agents": len(agents),
            "sent": sent,
            "failed": failed,
            "skipped": skipped,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def send_training_reminders(db: Session) -> dict:
        """
        Send training reminders to agents with incomplete required courses.

        Returns summary of reminders sent.
        """
        from app.models.training import TrainingCourse, CourseCompletion

        # Get all required published courses
        required_courses = db.query(TrainingCourse).filter(
            TrainingCourse.is_required == True,
            TrainingCourse.is_published == True
        ).all()

        if not required_courses:
            return {
                "total_agents": 0,
                "sent": 0,
                "message": "No required courses configured"
            }

        # Get all approved agents
        agents = db.query(Agent).filter(Agent.status == "approved").all()

        sent = 0
        skipped = 0

        for agent in agents:
            user = db.query(User).filter(User.id == agent.user_id).first()
            if not user or not user.phone_number:
                skipped += 1
                continue

            # Check for incomplete required courses
            incomplete_courses = []
            for course in required_courses:
                completion = db.query(CourseCompletion).filter(
                    CourseCompletion.agent_id == agent.id,
                    CourseCompletion.course_id == course.id,
                    CourseCompletion.status == "completed"
                ).first()

                if not completion:
                    incomplete_courses.append(course)

            # Send reminder if agent has incomplete required courses
            if incomplete_courses:
                try:
                    # Send reminder for first incomplete course
                    whatsapp_service.send_training_reminder(
                        to_number=user.phone_number,
                        agent_name=user.name,
                        course_title=incomplete_courses[0].title
                    )
                    sent += 1
                except Exception as e:
                    print(f"[ERROR] Training reminder failed for agent {agent.id}: {e}")

        return {
            "total_agents": len(agents),
            "sent": sent,
            "skipped": skipped,
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
agent_notifications_service = AgentNotificationsService()
