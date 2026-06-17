"""Training course models."""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base


class TrainingCourse(Base):
    """Training course for agents."""
    __tablename__ = "training_courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # onboarding, sales, compliance, advanced
    difficulty = Column(String(20), nullable=False, default="beginner")  # beginner, intermediate, advanced

    # Content
    content_type = Column(String(20), nullable=False)  # video, document, quiz, mixed
    video_url = Column(String(500), nullable=True)
    document_url = Column(String(500), nullable=True)
    content_html = Column(Text, nullable=True)

    # Metadata
    duration_minutes = Column(Integer, nullable=True)
    is_required = Column(Boolean, nullable=False, default=False)
    is_published = Column(Boolean, nullable=False, default=False)
    order_index = Column(Integer, nullable=False, default=0)

    # Completion
    pass_score = Column(Integer, nullable=True)  # For quizzes (percentage)
    quiz_questions = Column(JSONB, nullable=True)  # Quiz questions and answers

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


class CourseCompletion(Base):
    """Agent course completion tracking."""
    __tablename__ = "course_completions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("training_courses.id", ondelete="CASCADE"), nullable=False)

    status = Column(String(20), nullable=False, default="in_progress")  # in_progress, completed, failed
    progress_percent = Column(Integer, nullable=False, default=0)
    score = Column(Integer, nullable=True)  # For quizzes

    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    certificate_url = Column(String(500), nullable=True)

    # For tracking video watch time or quiz attempts
    metadata = Column(JSONB, nullable=True)
