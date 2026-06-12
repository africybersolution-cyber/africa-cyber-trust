"""Database connection and session management with lazy initialization."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Create base class for models
Base = declarative_base()

# Global variables for lazy initialization
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        from app.core.config import settings
        if settings.DATABASE_URL:
            _engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=settings.DEBUG,
            )
    return _engine


def get_session_local():
    """Get or create session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        if engine:
            _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


def get_db() -> Generator:
    """Dependency for database sessions."""
    SessionLocal = get_session_local()
    if SessionLocal is None:
        # No database configured
        yield None
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


# For backwards compatibility
engine = property(lambda self: get_engine())
SessionLocal = property(lambda self: get_session_local())
