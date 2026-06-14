"""Fix existing users - Give them STARTER trial"""
import sys
sys.path.insert(0, 'backend')

from datetime import datetime, timezone, timedelta
from app.db.database import get_session_local
from app.models.user import User

SessionLocal = get_session_local()
db = SessionLocal()

try:
    # Get all users without trial
    users_without_trial = db.query(User).filter(
        User.trial_started_at == None
    ).all()

    print(f"Found {len(users_without_trial)} users without trial")

    for user in users_without_trial:
        # Start 14-day STARTER trial
        user.account_type = 'starter'
        user.trial_started_at = datetime.now(timezone.utc)
        user.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=14)
        user.trial_status = 'active'

        print(f"✅ Activated STARTER trial for: {user.email}")

    db.commit()
    print(f"\n🎉 Successfully updated {len(users_without_trial)} users!")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
