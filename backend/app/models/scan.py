"""Scan and Finding models for security scanning."""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.database import Base


class Scan(Base):
    """Security scan record."""
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    score = Column(Integer, nullable=True)
    started_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    scan_type = Column(String(50), nullable=False, default="full")
    findings_count = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    scan_data = Column(JSONB, nullable=True)

    # Relationships
    asset = relationship("Asset", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")

    def calculate_score(self) -> int:
        """
        Calculate security score based on findings.

        Score formula:
        - Start at 100
        - Critical: -20 points each
        - High: -10 points each
        - Medium: -5 points each
        - Low: -2 points each
        - Minimum score: 0
        """
        score = 100
        score -= self.critical_count * 20
        score -= self.high_count * 10
        score -= self.medium_count * 5
        score -= self.low_count * 2
        return max(0, min(100, score))


class Finding(Base):
    """Security finding/issue discovered during scan."""
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    cve_id = Column(String(50), nullable=True)
    found_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Legacy fields (kept for backward compatibility)
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Remediation tracking
    status = Column(String(20), default="open", nullable=False, index=True)
    # Status values: 'open', 'in_progress', 'resolved', 'verified', 'false_positive', 'ignored'

    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    marked_resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(TIMESTAMP(timezone=True), nullable=True)
    status_changed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    status_changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    finding_data = Column(JSONB, nullable=True)

    # Relationships
    scan = relationship("Scan", back_populates="findings")
    asset = relationship("Asset", back_populates="findings")
