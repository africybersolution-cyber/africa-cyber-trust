"""Admin audit log model - tracks all admin actions."""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class AdminAuditLog(Base):
    """
    Append-only audit trail for all admin actions.

    Never update or delete records - this is for compliance and security.
    """

    __tablename__ = "admin_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(60), nullable=False, index=True)  # create_user, grant_plan, impersonate, etc
    target_type = Column(String(40), nullable=True)  # user, asset, payment, agent, etc
    target_id = Column(Text, nullable=True)  # UUID or identifier of the target
    metadata = Column(JSONB, nullable=True)  # Additional context (plan_name, duration, etc)
    ip_address = Column(INET, nullable=True)  # IP address of the admin
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    actor = relationship("User", foreign_keys=[actor_id])

    def __repr__(self):
        return f"<AdminAuditLog {self.action} by {self.actor_id} on {self.created_at}>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "actor_id": str(self.actor_id),
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "metadata": self.metadata,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
