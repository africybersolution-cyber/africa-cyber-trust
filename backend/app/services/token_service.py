"""
Token Management Service for Domain Verification

Handles all token-related operations including generation, validation,
expiration checking, and cleanup.
"""
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.verification import (
    VerificationToken,
    VerificationHistory,
    VerificationHistoryStatus,
    VerificationHistoryMethod,
    AuditLog,
    AuditAction
)
from app.models.asset import Asset


class TokenConfig:
    """Token configuration constants."""
    # Default expiration times for each method (in hours)
    EXPIRATION_TIMES = {
        "dns_txt": 48,      # 2 days
        "html_file": 48,    # 2 days
        "admin_email": 24,  # 1 day
        "meta_tag": 48,     # 2 days
        "cname": 72,        # 3 days
    }

    # Token length
    TOKEN_LENGTH = 16

    # Characters allowed in token (alphanumeric lowercase)
    TOKEN_CHARS = string.ascii_lowercase + string.digits

    # Rate limiting (max attempts per asset per hour)
    MAX_ATTEMPTS_PER_HOUR = 10


class TokenService:
    """Service for managing verification tokens."""

    @staticmethod
    def generate_token(length: int = TokenConfig.TOKEN_LENGTH) -> str:
        """
        Generate a cryptographically secure random token.

        Args:
            length: Length of token (default 16)

        Returns:
            Random alphanumeric token
        """
        return ''.join(
            secrets.choice(TokenConfig.TOKEN_CHARS)
            for _ in range(length)
        )

    @staticmethod
    def create_verification_token(
        db: Session,
        asset_id: str,
        method: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        custom_expiration_hours: Optional[int] = None
    ) -> Tuple[bool, Optional[VerificationToken], str]:
        """
        Create a new verification token for an asset.

        Args:
            db: Database session
            asset_id: Asset ID to verify
            method: Verification method (dns_txt, html_file, admin_email, etc.)
            user_id: User requesting verification (for audit)
            ip_address: IP address of requester (for audit)
            custom_expiration_hours: Custom expiration time (overrides default)

        Returns:
            Tuple of (success: bool, token: VerificationToken or None, message: str)
        """
        # Check if asset exists
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return False, None, "Asset not found"

        # Check rate limiting
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_attempts = db.query(VerificationToken).filter(
            and_(
                VerificationToken.asset_id == asset_id,
                VerificationToken.created_at >= one_hour_ago
            )
        ).count()

        if recent_attempts >= TokenConfig.MAX_ATTEMPTS_PER_HOUR:
            # Log rate limit hit
            TokenService._log_audit(
                db, asset_id, user_id, ip_address,
                AuditAction.TOKEN_GENERATED.value,
                {"error": "rate_limit_exceeded", "attempts": recent_attempts}
            )
            return False, None, f"Rate limit exceeded. Maximum {TokenConfig.MAX_ATTEMPTS_PER_HOUR} attempts per hour."

        # Invalidate any existing valid tokens for this asset
        TokenService._invalidate_existing_tokens(db, asset_id)

        # Calculate expiration
        expiration_hours = custom_expiration_hours or TokenConfig.EXPIRATION_TIMES.get(method, 48)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)

        # Generate unique token
        max_attempts = 10
        for attempt in range(max_attempts):
            token_string = TokenService.generate_token()

            # Check if token already exists
            existing = db.query(VerificationToken).filter(
                VerificationToken.token == token_string
            ).first()

            if not existing:
                break

            if attempt == max_attempts - 1:
                return False, None, "Failed to generate unique token"

        # Create token
        token = VerificationToken(
            asset_id=asset_id,
            token=token_string,
            method=method,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            is_valid=True
        )

        db.add(token)
        db.commit()
        db.refresh(token)

        # Log token generation
        TokenService._log_audit(
            db, asset_id, user_id, ip_address,
            AuditAction.TOKEN_GENERATED.value,
            {
                "method": method,
                "token_id": str(token.id),
                "expires_at": expires_at.isoformat(),
                "expiration_hours": expiration_hours
            }
        )

        return True, token, "Token created successfully"

    @staticmethod
    def validate_token(
        db: Session,
        asset_id: str,
        token_string: str,
        mark_as_used: bool = False,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, str, Optional[VerificationToken]]:
        """
        Validate a verification token.

        Args:
            db: Database session
            asset_id: Asset ID being verified
            token_string: Token to validate
            mark_as_used: Whether to mark token as used after validation
            user_id: User performing validation (for audit)
            ip_address: IP address (for audit)

        Returns:
            Tuple of (is_valid: bool, message: str, token: VerificationToken or None)
        """
        # Find token
        token = db.query(VerificationToken).filter(
            and_(
                VerificationToken.asset_id == asset_id,
                VerificationToken.token == token_string
            )
        ).first()

        if not token:
            TokenService._log_audit(
                db, asset_id, user_id, ip_address,
                AuditAction.TOKEN_USED.value,
                {"error": "token_not_found", "token": token_string[:8] + "..."}
            )
            return False, "Token not found", None

        # Check if already used
        if not token.is_valid:
            TokenService._log_audit(
                db, asset_id, user_id, ip_address,
                AuditAction.TOKEN_USED.value,
                {"error": "token_already_used", "token_id": str(token.id)}
            )
            return False, "Token has already been used", token

        # Check expiration
        if token.is_expired():
            # Mark as expired
            token.is_valid = False
            db.commit()

            TokenService._log_audit(
                db, asset_id, user_id, ip_address,
                AuditAction.TOKEN_EXPIRED.value,
                {"token_id": str(token.id), "expired_at": token.expires_at.isoformat()}
            )
            return False, "Token has expired", token

        # Token is valid
        if mark_as_used:
            token.mark_used()
            db.commit()

            TokenService._log_audit(
                db, asset_id, user_id, ip_address,
                AuditAction.TOKEN_USED.value,
                {"token_id": str(token.id), "success": True}
            )

        return True, "Token is valid", token

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> Dict[str, int]:
        """
        Remove expired and used tokens from database.

        Args:
            db: Database session

        Returns:
            Dict with cleanup statistics
        """
        now = datetime.now(timezone.utc)

        # Find expired tokens
        expired_tokens = db.query(VerificationToken).filter(
            or_(
                VerificationToken.expires_at < now,
                and_(
                    VerificationToken.is_valid == False,
                    VerificationToken.used_at.isnot(None)
                )
            )
        ).all()

        expired_count = len(expired_tokens)

        # Delete expired tokens
        for token in expired_tokens:
            db.delete(token)

        db.commit()

        return {
            "expired_removed": expired_count,
            "timestamp": now.isoformat()
        }

    @staticmethod
    def get_asset_tokens(
        db: Session,
        asset_id: str,
        include_expired: bool = False
    ) -> List[VerificationToken]:
        """
        Get all tokens for an asset.

        Args:
            db: Database session
            asset_id: Asset ID
            include_expired: Include expired/used tokens

        Returns:
            List of tokens
        """
        query = db.query(VerificationToken).filter(
            VerificationToken.asset_id == asset_id
        )

        if not include_expired:
            query = query.filter(
                and_(
                    VerificationToken.is_valid == True,
                    VerificationToken.expires_at > datetime.now(timezone.utc)
                )
            )

        return query.order_by(VerificationToken.created_at.desc()).all()

    @staticmethod
    def _invalidate_existing_tokens(db: Session, asset_id: str):
        """Invalidate all existing valid tokens for an asset."""
        existing_tokens = db.query(VerificationToken).filter(
            and_(
                VerificationToken.asset_id == asset_id,
                VerificationToken.is_valid == True
            )
        ).all()

        for token in existing_tokens:
            token.is_valid = False

        if existing_tokens:
            db.commit()

    @staticmethod
    def _log_audit(
        db: Session,
        asset_id: str,
        user_id: Optional[str],
        ip_address: Optional[str],
        action: str,
        details: Dict
    ):
        """Create an audit log entry."""
        audit = AuditLog(
            asset_id=asset_id,
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc)
        )
        db.add(audit)
        db.commit()


# Singleton instance
token_service = TokenService()
