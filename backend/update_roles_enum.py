"""
Update UserRole enum to include admin roles.
"""
from app.db.database import get_engine
from sqlalchemy import text

def update_enum():
    """Add new role values to the userrole enum."""
    engine = get_engine()

    if not engine:
        print("Could not connect to database")
        return False

    try:
        with engine.connect() as conn:
            # Check current enum values
            result = conn.execute(text("""
                SELECT enumlabel FROM pg_enum
                WHERE enumtypid = 'userrole'::regtype
                ORDER BY enumsortorder;
            """))
            current_values = [row[0] for row in result.fetchall()]
            print(f"Current enum values: {current_values}")

            # Add new values if they don't exist
            new_values = ['SUPER_ADMIN', 'PLATFORM_ADMIN', 'AGENT', 'SUPPORT_ADMIN']

            for value in new_values:
                if value not in current_values:
                    print(f"Adding enum value: {value}")
                    conn.execute(text(f"ALTER TYPE userrole ADD VALUE '{value}'"))
                    conn.commit()
                else:
                    print(f"Enum value already exists: {value}")

            print("Enum updated successfully!")
            return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    update_enum()
