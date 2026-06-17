"""Migration 008: Agent Training System

Creates tables for training courses and completion tracking.
"""
from sqlalchemy import text


def upgrade(db_connection):
    """Add training system tables."""

    # Create training_courses table
    db_connection.execute(text("""
        CREATE TABLE IF NOT EXISTS training_courses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(50) NOT NULL,
            difficulty VARCHAR(20) NOT NULL DEFAULT 'beginner',
            content_type VARCHAR(20) NOT NULL,
            video_url VARCHAR(500),
            document_url VARCHAR(500),
            content_html TEXT,
            duration_minutes INTEGER,
            is_required BOOLEAN NOT NULL DEFAULT false,
            is_published BOOLEAN NOT NULL DEFAULT false,
            order_index INTEGER NOT NULL DEFAULT 0,
            pass_score INTEGER,
            quiz_questions JSONB,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            created_by UUID REFERENCES users(id)
        );
    """))

    db_connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_training_category ON training_courses(category);
        CREATE INDEX IF NOT EXISTS idx_training_published ON training_courses(is_published);
        CREATE INDEX IF NOT EXISTS idx_training_order ON training_courses(order_index);
    """))

    # Create course_completions table
    db_connection.execute(text("""
        CREATE TABLE IF NOT EXISTS course_completions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            course_id UUID NOT NULL REFERENCES training_courses(id) ON DELETE CASCADE,
            status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
            progress_percent INTEGER NOT NULL DEFAULT 0,
            score INTEGER,
            started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            certificate_url VARCHAR(500),
            extra_data JSONB,
            UNIQUE(agent_id, course_id)
        );
    """))

    db_connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_completion_agent ON course_completions(agent_id, status);
        CREATE INDEX IF NOT EXISTS idx_completion_course ON course_completions(course_id);
    """))

    db_connection.commit()


def downgrade(db_connection):
    """Remove training system tables."""
    db_connection.execute(text("DROP TABLE IF EXISTS course_completions CASCADE;"))
    db_connection.execute(text("DROP TABLE IF EXISTS training_courses CASCADE;"))
    db_connection.commit()
