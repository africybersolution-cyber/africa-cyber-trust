"""
Reset password for a user.

Usage: python reset_password.py
"""
from app.db.database import get_engine
from sqlalchemy import text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_password(email: str, new_password: str):
    """Reset a user's password."""
    engine = get_engine()

    if not engine:
        print("ERROR: Could not connect to database")
        return False

    try:
        with engine.connect() as conn:
            # Check if user exists
            result = conn.execute(
                text("SELECT id, email FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()

            if not user:
                print(f"ERROR: User with email '{email}' not found")
                return False

            print(f"Found user: {user.email}")

            # Hash the new password
            hashed_password = pwd_context.hash(new_password)
            print(f"New password hashed")

            # Update password
            conn.execute(
                text("""
                    UPDATE users
                    SET hashed_password = :password
                    WHERE email = :email
                """),
                {"password": hashed_password, "email": email}
            )
            conn.commit()

            print(f"SUCCESS: Password updated for {email}")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    # Reset password for africybersolution@gmail.com
    reset_password("africybersolution@gmail.com", "Africyber@2024")
