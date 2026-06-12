#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not found")
    exit(1)

conn = psycopg2.connect(database_url)
cur = conn.cursor()

# Count before
cur.execute("SELECT COUNT(*) FROM findings")
before_count = cur.fetchone()[0]
print(f"Findings before delete: {before_count}")

# Delete ALL findings
cur.execute("DELETE FROM findings")
conn.commit()

# Count after
cur.execute("SELECT COUNT(*) FROM findings")
after_count = cur.fetchone()[0]
print(f"Findings after delete: {after_count}")
print(f"Deleted {before_count - after_count} findings")

# Also reset scan counts
cur.execute("UPDATE scans SET findings_count = 0, critical_count = 0, high_count = 0, medium_count = 0, low_count = 0")
conn.commit()
print("Reset all scan counts to 0")

cur.close()
conn.close()
print("\nDone! Database is clean. Run a fresh scan now.")
