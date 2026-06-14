"""Automatically fix existing users - Give them STARTER trial"""
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timezone, timedelta

print("="*80)
print("AUTO-FIX EXISTING USERS - STARTER TRIAL ACTIVATION")
print("="*80)

# Get database URL from environment
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("\n[WARNING]  DATABASE_URL not found in environment")
    print("Please set it:")
    print('  $env:DATABASE_URL="postgresql://user:pass@host:5432/dbname"')
    print("\nOr enter it now:")
    database_url = input("Database URL: ").strip()

if not database_url:
    print("[ERROR] No database URL provided. Exiting.")
    exit(1)

# Fix postgres:// to postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"\n[CONNECT] Connecting to database...")
print(f"   Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'hidden'}")

try:
    # Create engine
    engine = create_engine(database_url)

    # Connect and run update
    with engine.connect() as conn:
        # First, check current users
        print("\n[STATUS] Current users status:")
        result = conn.execute(text("""
            SELECT email, name, account_type, trial_status, trial_started_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 10
        """))

        users = result.fetchall()
        for user in users:
            print(f"  - {user[0]}: account_type={user[2]}, trial_status={user[3]}")

        # Count users needing update
        count_result = conn.execute(text("""
            SELECT COUNT(*) FROM users WHERE trial_started_at IS NULL
        """))
        count = count_result.fetchone()[0]

        if count == 0:
            print("\n[OK] All users already have trials activated!")
        else:
            print(f"\n[FIX] Found {count} users needing STARTER trial...")

            # Run the update
            update_result = conn.execute(text("""
                UPDATE users
                SET
                    account_type = 'starter',
                    trial_started_at = NOW(),
                    trial_ends_at = NOW() + INTERVAL '14 days',
                    trial_status = 'active'
                WHERE trial_started_at IS NULL
            """))

            conn.commit()

            print(f"[OK] Updated {count} users to STARTER tier!")

            # Show updated users
            print("\n[LIST] Updated users:")
            result = conn.execute(text("""
                SELECT email, name, account_type, trial_status,
                       trial_ends_at AT TIME ZONE 'UTC' as trial_ends
                FROM users
                WHERE account_type = 'starter'
                ORDER BY trial_started_at DESC
            """))

            updated_users = result.fetchall()
            for user in updated_users:
                print(f"  OK {user[0]}")
                print(f"    Plan: {user[2].upper()}")
                print(f"    Status: {user[3]}")
                print(f"    Trial ends: {user[4]}")
                print()

    print("="*80)
    print("[SUCCESS] SUCCESS! All users now have STARTER trial activated!")
    print("="*80)

except Exception as e:
    print(f"\n[ERROR] ERROR: {e}")
    print(f"\nFull error details:")
    import traceback
    traceback.print_exc()
    exit(1)
