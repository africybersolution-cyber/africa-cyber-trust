#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple duplicate findings cleanup using raw SQL.
Avoids ORM model import issues.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def cleanup_duplicates():
    """Remove duplicate findings using raw SQL."""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment")
        return

    print("Connecting to database...")

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        print("Searching for duplicate findings...")

        # Find duplicates: same scan_id + title + severity
        cur.execute("""
            SELECT scan_id, title, severity, COUNT(*) as count
            FROM findings
            GROUP BY scan_id, title, severity
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)

        duplicates = cur.fetchall()

        if not duplicates:
            print("No duplicates found!")
            conn.close()
            return

        print(f"\nFound {len(duplicates)} groups of duplicates:")
        for scan_id, title, severity, count in duplicates:
            print(f"  - {title} (scan {scan_id}): {count} copies")

        total_to_delete = 0

        # For each duplicate group, keep the oldest (first created) and delete the rest
        for scan_id, title, severity, count in duplicates:
            print(f"\nProcessing: {title} (scan {scan_id})...")

            # Get all IDs for this duplicate group, ordered by created_at
            cur.execute("""
                SELECT id, created_at
                FROM findings
                WHERE scan_id = %s AND title = %s AND severity = %s
                ORDER BY created_at ASC
            """, (scan_id, title, severity))

            ids = cur.fetchall()

            # Keep the first one, delete the rest
            if len(ids) > 1:
                keep_id = ids[0][0]
                delete_ids = [row[0] for row in ids[1:]]

                print(f"  Keeping: {keep_id} (created at {ids[0][1]})")
                print(f"  Deleting: {len(delete_ids)} duplicates")

                # Delete duplicates
                cur.execute("""
                    DELETE FROM findings
                    WHERE id = ANY(%s)
                """, (delete_ids,))

                total_to_delete += len(delete_ids)

        # Commit changes
        conn.commit()

        print(f"\n✓ SUCCESS: Deleted {total_to_delete} duplicate findings!")

        # Show final count
        cur.execute("SELECT COUNT(*) FROM findings")
        total_findings = cur.fetchone()[0]
        print(f"\nTotal findings remaining: {total_findings}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("  DUPLICATE FINDINGS CLEANUP (SQL)")
    print("=" * 50)
    print()
    cleanup_duplicates()
    print()
    print("=" * 50)
    print("  CLEANUP COMPLETE")
    print("=" * 50)
