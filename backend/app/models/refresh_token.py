"""Refresh token model for secure token management."""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base


class RefreshToken(Base):
    """Model for storing refresh tokens with revocation support."""
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)

    # Relationship
    user = relationship("User", back_populates="refresh_tokens")

    def is_valid(self) -> bool:
        """Check if refresh token is still valid."""
        return (
            not self.is_revoked
            and self.expires_at > datetime.utcnow()
        )

    def revoke(self):
        """Revoke this refresh token."""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()

    @staticmethod
    def create_token_string() -> str:
        """Generate a secure random token string."""
        import secrets
        return secrets.token_urlsafe(48)
