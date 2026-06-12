"""Initialize database with all tables."""
from app.db.database import Base, get_engine

def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    engine = get_engine()
    if engine:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")
        print(f"Tables created: {list(Base.metadata.tables.keys())}")
    else:
        print("ERROR: No database connection!")

if __name__ == "__main__":
    from app.models import user, company, asset, public_check, scan_job, alert
    init_database()
