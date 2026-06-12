#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check current state of findings in database.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_findings():
    """Show current findings in database."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found")
        return

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    # Get total findings
    cur.execute("SELECT COUNT(*) FROM findings")
    total = cur.fetchone()[0]
    print(f"Total findings in database: {total}")

    # Get findings by scan
    cur.execute("""
        SELECT scan_id, COUNT(*) as finding_count
        FROM findings
        GROUP BY scan_id
        ORDER BY scan_id DESC
        LIMIT 10
    """)

    print("\nFindings per scan (last 10 scans):")
    for scan_id, count in cur.fetchall():
        print(f"  Scan {scan_id}: {count} findings")

    # Get most recent scan details
    cur.execute("""
        SELECT scan_id, title, severity, COUNT(*) as count
        FROM findings
        WHERE scan_id = (SELECT id FROM scans ORDER BY created_at DESC LIMIT 1)
        GROUP BY scan_id, title, severity
        ORDER BY count DESC
    """)

    print("\nMost recent scan breakdown:")
    for scan_id, title, severity, count in cur.fetchall():
        print(f"  [{severity.upper()}] {title}: {count} copies")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_findings()
