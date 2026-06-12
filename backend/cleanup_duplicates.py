#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup duplicate findings from the database.
This script removes duplicate findings that were created before the deduplication fix.
"""

from app.db.database import get_session_local
from app.models.scan import Finding
from sqlalchemy import func
from datetime import datetime

def cleanup_duplicate_findings():
    """Remove duplicate findings from database, keeping only the first occurrence."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        print("Searching for duplicate findings...")

        # Get all findings grouped by (scan_id, title, severity, category)
        # to find duplicates
        findings = db.query(Finding).order_by(Finding.created_at).all()

        # Track unique findings per scan
        seen = {}
        duplicates_to_delete = []

        for finding in findings:
            key = f"{finding.scan_id}_{finding.title}_{finding.severity}"

            if key in seen:
                # This is a duplicate - mark for deletion
                duplicates_to_delete.append(finding.id)
                print(f"  Found duplicate: {finding.title} (scan {finding.scan_id})")
            else:
                # First occurrence - keep it
                seen[key] = finding.id

        if duplicates_to_delete:
            print(f"\nDeleting {len(duplicates_to_delete)} duplicate findings...")

            # Delete duplicates
            for finding_id in duplicates_to_delete:
                finding = db.query(Finding).filter(Finding.id == finding_id).first()
                if finding:
                    db.delete(finding)

            db.commit()
            print(f"SUCCESS: Deleted {len(duplicates_to_delete)} duplicate findings!")
        else:
            print("No duplicates found!")

        # Show summary
        total_findings = db.query(Finding).count()
        print(f"\nTotal findings in database: {total_findings}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("  DUPLICATE FINDINGS CLEANUP")
    print("=" * 50)
    print()
    cleanup_duplicate_findings()
    print()
    print("=" * 50)
    print("  CLEANUP COMPLETE")
    print("=" * 50)
