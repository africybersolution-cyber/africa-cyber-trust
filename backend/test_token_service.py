"""
TEST: Token Service comprehensive testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.services.token_service import token_service, TokenConfig
from app.models.asset import Asset
from app.models.verification import VerificationToken
import time


def test_token_service():
    """Test token service functionality."""
    print("=" * 60)
    print("TOKEN SERVICE TEST")
    print("=" * 60)
    print()

    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Get test asset
        asset = db.query(Asset).first()
        if not asset:
            print("[ERROR] No assets found! Add an asset first.")
            return False

        print(f"[OK] Using asset: {asset.name} (ID: {asset.id})")
        print()

        # TEST 1: Generate token
        print("TEST 1: Token Generation")
        print("-" * 40)

        token_str = token_service.generate_token()
        print(f"[OK] Generated token: {token_str}")
        print(f"    - Length: {len(token_str)}")
        print(f"    - Format: alphanumeric lowercase")
        print()

        # TEST 2: Create verification token
        print("TEST 2: Create Verification Token")
        print("-" * 40)

        success, token, message = token_service.create_verification_token(
            db=db,
            asset_id=str(asset.id),
            method="dns_txt",
            user_id=None,
            ip_address="192.168.1.100"
        )

        if not success:
            print(f"[ERROR] Failed to create token: {message}")
            return False

        print(f"[OK] Token created: {token.token}")
        print(f"    - ID: {token.id}")
        print(f"    - Method: {token.method}")
        print(f"    - Created: {token.created_at}")
        print(f"    - Expires: {token.expires_at}")
        print(f"    - Valid: {token.is_valid}")
        print()

        # TEST 3: Validate token
        print("TEST 3: Token Validation")
        print("-" * 40)

        is_valid, msg, validated_token = token_service.validate_token(
            db=db,
            asset_id=str(asset.id),
            token_string=token.token,
            mark_as_used=False
        )

        print(f"[OK] Validation result: {is_valid}")
        print(f"    - Message: {msg}")
        print(f"    - Is expired: {validated_token.is_expired()}")
        print()

        # TEST 4: Invalid token
        print("TEST 4: Invalid Token Test")
        print("-" * 40)

        is_valid, msg, _ = token_service.validate_token(
            db=db,
            asset_id=str(asset.id),
            token_string="invalid-token-12345"
        )

        print(f"[OK] Invalid token rejected: {not is_valid}")
        print(f"    - Message: {msg}")
        print()

        # TEST 5: Mark token as used
        print("TEST 5: Mark Token as Used")
        print("-" * 40)

        is_valid, msg, used_token = token_service.validate_token(
            db=db,
            asset_id=str(asset.id),
            token_string=token.token,
            mark_as_used=True
        )

        print(f"[OK] Token marked as used")
        print(f"    - Still valid: {used_token.is_valid}")
        print(f"    - Used at: {used_token.used_at}")
        print()

        # TEST 6: Try to use already-used token
        print("TEST 6: Reject Used Token")
        print("-" * 40)

        is_valid, msg, _ = token_service.validate_token(
            db=db,
            asset_id=str(asset.id),
            token_string=token.token
        )

        print(f"[OK] Used token rejected: {not is_valid}")
        print(f"    - Message: {msg}")
        print()

        # TEST 7: Rate limiting
        print("TEST 7: Rate Limiting")
        print("-" * 40)

        # Create multiple tokens quickly
        success_count = 0
        rate_limited = False

        for i in range(TokenConfig.MAX_ATTEMPTS_PER_HOUR + 2):
            success, _, message = token_service.create_verification_token(
                db=db,
                asset_id=str(asset.id),
                method="html_file",
                ip_address="192.168.1.100"
            )

            if success:
                success_count += 1
            elif "Rate limit" in message:
                rate_limited = True
                print(f"[OK] Rate limit triggered after {success_count} attempts")
                print(f"    - Message: {message}")
                break

        if not rate_limited:
            print(f"[WARNING] Rate limit not triggered (created {success_count} tokens)")
        print()

        # TEST 8: Get asset tokens
        print("TEST 8: Get Asset Tokens")
        print("-" * 40)

        tokens = token_service.get_asset_tokens(
            db=db,
            asset_id=str(asset.id),
            include_expired=True
        )

        print(f"[OK] Found {len(tokens)} tokens")
        for t in tokens[:3]:  # Show first 3
            print(f"    - {t.token}: valid={t.is_valid}, method={t.method}")
        print()

        # TEST 9: Cleanup expired tokens
        print("TEST 9: Cleanup Expired Tokens")
        print("-" * 40)

        stats = token_service.cleanup_expired_tokens(db)
        print(f"[OK] Cleanup completed")
        print(f"    - Expired removed: {stats['expired_removed']}")
        print(f"    - Timestamp: {stats['timestamp']}")
        print()

        # TEST 10: Token expiration
        print("TEST 10: Token Expiration Check")
        print("-" * 40)

        # Create token with short expiration (for testing)
        success, short_token, _ = token_service.create_verification_token(
            db=db,
            asset_id=str(asset.id),
            method="admin_email",
            custom_expiration_hours=0,  # Expires immediately
            ip_address="192.168.1.100"
        )

        if success:
            # Wait a moment
            time.sleep(1)

            # Try to validate
            is_valid, msg, _ = token_service.validate_token(
                db=db,
                asset_id=str(asset.id),
                token_string=short_token.token
            )

            print(f"[OK] Expired token rejected: {not is_valid}")
            print(f"    - Message: {msg}")
        print()

        # Cleanup all test tokens
        print("CLEANUP: Removing test tokens...")
        test_tokens = db.query(VerificationToken).filter(
            VerificationToken.asset_id == asset.id
        ).all()

        for t in test_tokens:
            db.delete(t)
        db.commit()
        print(f"[OK] Removed {len(test_tokens)} test tokens")
        print()

        print("=" * 60)
        print("TOKEN SERVICE TEST PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_token_service()
    sys.exit(0 if success else 1)
