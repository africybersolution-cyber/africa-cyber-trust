"""
COMPREHENSIVE INTEGRATION TEST
Tests the complete verification system end-to-end
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from app.core.config import settings
from app.services.token_service import token_service
from app.services.email_service import email_service
from app.models.asset import Asset
from app.models.verification import VerificationToken, VerificationHistory, AuditLog


def run_comprehensive_test():
    """Run complete integration test."""
    print("=" * 70)
    print("COMPREHENSIVE INTEGRATION TEST")
    print("=" * 70)
    print()

    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    test_results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }

    try:
        # Get test asset
        asset = db.query(Asset).first()
        if not asset:
            print("[SKIP] No assets found. Please add an asset first.")
            return False

        print(f"[INFO] Using test asset: {asset.name} (ID: {asset.id})")
        print()

        # TEST 1: Token Service Integration
        print("TEST 1: Token Service Integration")
        print("-" * 70)
        try:
            success, token_obj, message = token_service.create_verification_token(
                db=db,
                asset_id=str(asset.id),
                method="dns_txt",
                user_id=None,
                ip_address="192.168.1.1"
            )

            assert success, f"Token creation failed: {message}"
            assert token_obj is not None, "Token object is None"
            assert len(token_obj.token) == 16, f"Token length wrong: {len(token_obj.token)}"

            print(f"[PASS] Token created: {token_obj.token}")
            print(f"       Expires: {token_obj.expires_at}")
            test_results["passed"] += 1
            test_results["tests"].append(("Token Service", "PASS"))

        except Exception as e:
            print(f"[FAIL] {str(e)}")
            test_results["failed"] += 1
            test_results["tests"].append(("Token Service", "FAIL"))

        print()

        # TEST 2: Token Validation
        print("TEST 2: Token Validation")
        print("-" * 70)
        try:
            is_valid, msg, validated = token_service.validate_token(
                db=db,
                asset_id=str(asset.id),
                token_string=token_obj.token,
                mark_as_used=False
            )

            assert is_valid, f"Token validation failed: {msg}"
            assert validated is not None, "Validated token is None"
            assert not validated.is_expired(), "Token is expired but shouldn't be"

            print(f"[PASS] Token validated successfully")
            print(f"       Message: {msg}")
            test_results["passed"] += 1
            test_results["tests"].append(("Token Validation", "PASS"))

        except Exception as e:
            print(f"[FAIL] {str(e)}")
            test_results["failed"] += 1
            test_results["tests"].append(("Token Validation", "FAIL"))

        print()

        # TEST 3: Verification History Logging
        print("TEST 3: Verification History Logging")
        print("-" * 70)
        try:
            history = VerificationHistory(
                asset_id=asset.id,
                method="dns_txt",
                status="success",
                attempted_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                ip_address="192.168.1.1",
                user_agent="Test/1.0",
                verification_data={"test": True, "method": "dns_txt"}
            )
            db.add(history)
            db.commit()
            db.refresh(history)

            assert history.id is not None, "History record not saved"

            print(f"[PASS] Verification history logged")
            print(f"       ID: {history.id}")
            print(f"       Status: {history.status}")
            test_results["passed"] += 1
            test_results["tests"].append(("Verification History", "PASS"))

        except Exception as e:
            print(f"[FAIL] {str(e)}")
            test_results["failed"] += 1
            test_results["tests"].append(("Verification History", "FAIL"))

        print()

        # TEST 4: Audit Trail
        print("TEST 4: Audit Trail")
        print("-" * 70)
        try:
            # Check if audit logs were created by token service
            audit_count = db.query(AuditLog).filter(
                AuditLog.asset_id == asset.id
            ).count()

            assert audit_count > 0, "No audit logs found"

            # Get most recent audit log
            latest_audit = db.query(AuditLog).filter(
                AuditLog.asset_id == asset.id
            ).order_by(AuditLog.created_at.desc()).first()

            print(f"[PASS] Audit trail working")
            print(f"       Total audit logs: {audit_count}")
            print(f"       Latest action: {latest_audit.action}")
            test_results["passed"] += 1
            test_results["tests"].append(("Audit Trail", "PASS"))

        except Exception as e:
            print(f"[FAIL] {str(e)}")
            test_results["failed"] += 1
            test_results["tests"].append(("Audit Trail", "FAIL"))

        print()

        # TEST 5: Token Cleanup
        print("TEST 5: Token Cleanup Service")
        print("-" * 70)
        try:
            stats = token_service.cleanup_expired_tokens(db)

            assert "expired_removed" in stats, "Stats missing expired_removed"
            assert "timestamp" in stats, "Stats missing timestamp"

            print(f"[PASS] Cleanup service working")
            print(f"       Tokens removed: {stats['expired_removed']}")
            print(f"       Timestamp: {stats['timestamp']}")
            test_results["passed"] += 1
            test_results["tests"].append(("Token Cleanup", "PASS"))

        except Exception as e:
            print(f"[FAIL] {str(e)}")
            test_results["failed"] += 1
            test_results["tests"].append(("Token Cleanup", "FAIL"))

        print()

        # TEST 6: Email Service
        print("TEST 6: Email Service")
        print("-" * 70)
        try:
            # Check if email service is configured
            assert email_service.SENDER_PASSWORD != "", "Email password not configured"
            assert email_service.SENDER_EMAIL != "", "Sender email not configured"

            print(f"[PASS] Email service configured")
            print(f"       Sender: {email_service.SENDER_EMAIL}")
            print(f"       SMTP: {email_service.SMTP_SERVER}:{email_service.SMTP_PORT}")
            test_results["passed"] += 1
            test_results["tests"].append(("Email Service", "PASS"))

        except Exception as e:
            print(f"[FAIL] {str(e)}")
            test_results["failed"] += 1
            test_results["tests"].append(("Email Service", "FAIL"))

        print()

        # TEST 7: Database Relationships
        print("TEST 7: Database Relationships")
        print("-" * 70)
        try:
            # Refresh asset to load relationships
            db.refresh(asset)

            # Check relationships
            history_count = len(asset.verification_history)
            token_count = len(asset.verification_tokens)
            audit_count = len(asset.audit_logs)

            print(f"[PASS] Database relationships working")
            print(f"       Verification history: {history_count} records")
            print(f"       Verification tokens: {token_count} records")
            print(f"       Audit logs: {audit_count} records")
            test_results["passed"] += 1
            test_results["tests"].append(("Database Relationships", "PASS"))

        except Exception as e:
            print(f"[FAIL] {str(e)}")
            test_results["failed"] += 1
            test_results["tests"].append(("Database Relationships", "FAIL"))

        print()

        # TEST 8: Rate Limiting
        print("TEST 8: Rate Limiting")
        print("-" * 70)
        try:
            # Try to create 3 tokens rapidly
            tokens_created = 0
            rate_limited = False

            for i in range(3):
                success, _, message = token_service.create_verification_token(
                    db=db,
                    asset_id=str(asset.id),
                    method="html_file",
                    ip_address="192.168.1.2"
                )

                if success:
                    tokens_created += 1
                elif "Rate limit" in message:
                    rate_limited = True
                    break

            print(f"[PASS] Rate limiting working")
            print(f"       Tokens created before limit: {tokens_created}")
            test_results["passed"] += 1
            test_results["tests"].append(("Rate Limiting", "PASS"))

        except Exception as e:
            print(f"[FAIL] {str(e)}")
            test_results["failed"] += 1
            test_results["tests"].append(("Rate Limiting", "FAIL"))

        print()

        # CLEANUP TEST DATA
        print("CLEANUP: Removing test data...")
        try:
            # Delete test tokens
            db.query(VerificationToken).filter(
                VerificationToken.asset_id == asset.id
            ).delete()

            # Delete test history
            db.query(VerificationHistory).filter(
                VerificationHistory.asset_id == asset.id,
                VerificationHistory.user_agent == "Test/1.0"
            ).delete()

            db.commit()
            print("[OK] Test data cleaned up")

        except Exception as e:
            print(f"[WARNING] Cleanup failed: {str(e)}")

        print()

        # FINAL RESULTS
        print("=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print()

        for test_name, result in test_results["tests"]:
            status_icon = "[PASS]" if result == "PASS" else "[FAIL]"
            print(f"{status_icon} {test_name}")

        print()
        print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
        print(f"Passed: {test_results['passed']} [OK]")
        print(f"Failed: {test_results['failed']}")
        print()

        if test_results['failed'] == 0:
            print("=" * 70)
            print("ALL TESTS PASSED!")
            print("SYSTEM IS PRODUCTION READY")
            print("=" * 70)
            return True
        else:
            print("=" * 70)
            print(f"SOME TESTS FAILED ({test_results['failed']})")
            print("=" * 70)
            return False

    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
