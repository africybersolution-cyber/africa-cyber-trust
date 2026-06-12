"""
TEST #2: Verify SQLAlchemy models work correctly with new tables
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.models.verification import (
    VerificationHistory,
    VerificationHistoryStatus,
    VerificationHistoryMethod,
    VerificationToken,
    AuditLog,
    AuditAction
)
from app.models.asset import Asset


def test_models():
    """Test all verification models."""
    print("=" * 60)
    print("TEST #2: SQLALCHEMY MODELS")
    print("=" * 60)
    print()

    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # STEP 1: Find an existing asset to test with
        print("STEP 1: Finding test asset...")
        asset = db.query(Asset).first()

        if not asset:
            print("[ERROR] No assets found in database!")
            print("Please add an asset first through the UI")
            return False

        print(f"[OK] Using asset: {asset.name} (ID: {asset.id})")
        print()

        # STEP 2: Test VerificationToken model
        print("STEP 2: Testing VerificationToken model...")
        token = VerificationToken(
            asset_id=asset.id,
            token="test-token-12345678",
            method=VerificationHistoryMethod.DNS_TXT.value,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=48),
            is_valid=True
        )
        db.add(token)
        db.commit()
        print(f"[OK] Created token: {token.id}")
        print(f"    - Token: {token.token}")
        print(f"    - Expires: {token.expires_at}")
        print(f"    - Is expired: {token.is_expired()}")
        print()

        # STEP 3: Test VerificationHistory model
        print("STEP 3: Testing VerificationHistory model...")
        history = VerificationHistory(
            asset_id=asset.id,
            method=VerificationHistoryMethod.DNS_TXT.value,
            status=VerificationHistoryStatus.PENDING.value,
            attempted_at=datetime.now(timezone.utc),
            ip_address="127.0.0.1",
            user_agent="Test Agent",
            verification_data={"test": "data", "record": "_acti-verify"}
        )
        db.add(history)
        db.commit()
        print(f"[OK] Created verification history: {history.id}")
        print(f"    - Method: {history.method}")
        print(f"    - Status: {history.status}")
        print(f"    - Data: {history.verification_data}")
        print()

        # STEP 4: Test AuditLog model
        print("STEP 4: Testing AuditLog model...")

        # Find a user
        from app.models.user import User
        user = db.query(User).first()

        audit = AuditLog(
            asset_id=asset.id,
            user_id=user.id if user else None,
            action=AuditAction.VERIFICATION_STARTED.value,
            details={"method": "dns_txt", "test": True},
            ip_address="127.0.0.1",
            user_agent="Test Agent",
            created_at=datetime.now(timezone.utc)
        )
        db.add(audit)
        db.commit()
        print(f"[OK] Created audit log: {audit.id}")
        print(f"    - Action: {audit.action}")
        print(f"    - User: {user.email if user else 'None'}")
        print(f"    - Details: {audit.details}")
        print()

        # STEP 5: Test relationships
        print("STEP 5: Testing relationships...")

        # Refresh asset to load relationships
        db.refresh(asset)

        print(f"[OK] Asset has {len(asset.verification_history)} verification history records")
        print(f"[OK] Asset has {len(asset.verification_tokens)} verification tokens")
        print(f"[OK] Asset has {len(asset.audit_logs)} audit log entries")

        if len(asset.verification_history) > 0:
            print(f"    - Latest history: {asset.verification_history[-1].status}")
        if len(asset.verification_tokens) > 0:
            print(f"    - Latest token: {asset.verification_tokens[-1].token[:20]}...")
        if len(asset.audit_logs) > 0:
            print(f"    - Latest audit: {asset.audit_logs[-1].action}")
        print()

        # STEP 6: Test token methods
        print("STEP 6: Testing token methods...")
        print(f"[OK] Token is_expired(): {token.is_expired()}")
        print(f"    - Before mark_used: is_valid={token.is_valid}, used_at={token.used_at}")

        token.mark_used()
        db.commit()

        print(f"    - After mark_used: is_valid={token.is_valid}, used_at={token.used_at}")
        print()

        # STEP 7: Test queries
        print("STEP 7: Testing queries...")

        # Query by status
        pending_count = db.query(VerificationHistory).filter(
            VerificationHistory.status == VerificationHistoryStatus.PENDING.value
        ).count()
        print(f"[OK] Found {pending_count} pending verification attempts")

        # Query valid tokens
        valid_tokens = db.query(VerificationToken).filter(
            VerificationToken.is_valid == True
        ).count()
        print(f"[OK] Found {valid_tokens} valid tokens")

        # Query recent audits
        recent_audits = db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).limit(5).all()
        print(f"[OK] Found {len(recent_audits)} recent audit logs")
        print()

        # STEP 8: Cleanup test data
        print("STEP 8: Cleaning up test data...")
        db.delete(token)
        db.delete(history)
        db.delete(audit)
        db.commit()
        print("[OK] Test data cleaned up")
        print()

        print("=" * 60)
        print("TEST #2 PASSED - ALL MODELS WORKING CORRECTLY!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1)
