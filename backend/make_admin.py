"""
Make a user super admin by email.

Usage: python make_admin.py
"""
from app.db.database import get_engine
from sqlalchemy import text

def make_admin(email: str):
    """Make a user super admin."""
    engine = get_engine()

    if not engine:
        print("ERROR: Could not connect to database")
        return False

    try:
        with engine.connect() as conn:
            # Check if user exists
            result = conn.execute(
                text("SELECT id, email, role FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()

            if not user:
                print(f"ERROR: User with email '{email}' not found")
                return False

            print(f"Found user: {user.email} (current role: {user.role})")

            # Update to super_admin (uppercase for enum)
            conn.execute(
                text("""
                    UPDATE users
                    SET role = 'SUPER_ADMIN',
                        is_active = true
                    WHERE email = :email
                """),
                {"email": email}
            )
            conn.commit()

            print(f"SUCCESS: {email} is now a SUPER ADMIN")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    # Make africybersolution@gmail.com super admin
    make_admin("africybersolution@gmail.com")
