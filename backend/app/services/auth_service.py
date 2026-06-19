"""Authentication service for user management and JWT tokens."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.company import Company
from app.core.config import settings
import secrets


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes for security
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days


class AuthService:
    """Authentication service for user login, signup, and token management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            print(f"JWT Verification Error: {type(e).__name__}: {str(e)}")
            print(f"Token (first 50 chars): {token[:50]}...")
            return None

    @staticmethod
    def create_refresh_token(db: Session, user_id: str, ip_address: str = None, user_agent: str = None) -> str:
        """Create a new refresh token for a user."""
        from app.models.refresh_token import RefreshToken

        token_string = RefreshToken.create_token_string()
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token_string,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(refresh_token)
        db.commit()

        return token_string

    @staticmethod
    def verify_refresh_token(db: Session, token: str) -> Optional[User]:
        """Verify a refresh token and return the associated user if valid."""
        from app.models.refresh_token import RefreshToken

        refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()

        if not refresh_token or not refresh_token.is_valid():
            return None

        user = db.query(User).filter(User.id == refresh_token.user_id).first()
        return user

    @staticmethod
    def revoke_refresh_token(db: Session, token: str):
        """Revoke a refresh token (for logout)."""
        from app.models.refresh_token import RefreshToken

        refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()

        if refresh_token:
            refresh_token.revoke()
            db.commit()

    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: str):
        """Revoke all refresh tokens for a user (for logout all devices)."""
        from app.models.refresh_token import RefreshToken

        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).all()

        for token in tokens:
            token.revoke()

        db.commit()

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = db.query(User).filter(User.email == email).first()

        # Always perform a dummy bcrypt verify to prevent timing attacks
        dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbYtkHxnye"  # bcrypt hash of "dummy"

        if not user:
            # Perform dummy verification to maintain constant time
            AuthService.verify_password(password, dummy_hash)
            return None

        # Check if user has a hashed_password field
        if not hasattr(user, 'hashed_password') or not user.hashed_password:
            # Perform dummy verification to maintain constant time
            AuthService.verify_password(password, dummy_hash)
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        name: str,
        company_id: Optional[str] = None,
        role: str = "normal_user",
        referred_by_code: Optional[str] = None
    ) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("User with this email already exists")

        # Normalize and validate referral code (agent referral codes are stored uppercase)
        normalized_ref = referred_by_code.strip().upper() if referred_by_code else None

        # Validate referral code if provided - only accept approved agents
        if normalized_ref:
            from app.models.agent import Agent
            referring_agent = db.query(Agent).filter(
                Agent.referral_code == normalized_ref,
                Agent.status == "approved"
            ).first()

            # If invalid/unapproved code, clear it (don't silently lose customer's referral)
            if not referring_agent:
                print(f"[SIGNUP] Invalid/unapproved referral code: {normalized_ref} - clearing")
                normalized_ref = None
            else:
                # 🚨 SECURITY: Block self-referral (agent can't refer themselves)
                agent_user = db.query(User).filter(User.id == referring_agent.user_id).first()
                if agent_user:
                    # Direct self-referral: same email
                    if agent_user.email.lower() == email.lower():
                        print(f"[SIGNUP BLOCKED] Self-referral attempt: {email}")
                        raise ValueError("You cannot use your own referral code")

                    # Sock-puppet detection: same email domain (for obvious cases like agent@company.com → agent2@company.com)
                    signup_domain = email.split('@')[1].lower() if '@' in email else ''
                    agent_domain = agent_user.email.split('@')[1].lower() if '@' in agent_user.email else ''

                    # Only block non-common domains (allow gmail.com, yahoo.com, etc. which are legitimate)
                    common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 'protonmail.com']
                    if signup_domain == agent_domain and signup_domain not in common_domains:
                        print(f"[SIGNUP BLOCKED] Suspicious self-referral: same domain {signup_domain}")
                        raise ValueError("Suspicious referral pattern detected. Please contact support if this is an error.")

        # Create user
        hashed_password = AuthService.hash_password(password)
        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,  # Will need to add this field to model
            role=role,
            email_verified=False,
            is_active=True,
            referred_by_code=normalized_ref,  # Links customer to referring agent
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Auto-create personal company for all users
        if not company_id:
            from app.models.company import Company
            personal_company = Company(
                name=f"{name}'s Account",
                country="Unknown",
                plan_id="free",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(personal_company)
            db.flush()  # Get the company ID
            user.company_id = personal_company.id
        else:
            user.company_id = company_id

        db.add(user)
        db.commit()
        db.refresh(user)

        # Automatically start STARTER trial for all new users
        from app.services.trial_service import TrialService
        TrialService.start_trial(user, db, plan_name='starter')

        return user

    @staticmethod
    def create_company(
        db: Session,
        company_name: str,
        email: str,
        country: str,
        domain: Optional[str] = None,
        phone: Optional[str] = None,
        size: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Company:
        """Create a new company/organization."""
        company = Company(
            name=company_name,
            country=country,
            plan_id="free",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Add additional fields if model supports them
        if domain and hasattr(company, 'domain'):
            company.domain = domain
        if phone and hasattr(company, 'phone'):
            company.phone = phone
        if email and hasattr(company, 'email'):
            company.email = email
        if size and hasattr(company, 'size'):
            company.size = size
        if industry and hasattr(company, 'industry'):
            company.industry = industry

        db.add(company)
        db.commit()
        db.refresh(company)

        return company

    @staticmethod
    def register_business(
        db: Session,
        company_name: str,
        email: str,
        password: str,
        name: str,
        country: str,
        domain: Optional[str] = None,
        phone: Optional[str] = None,
        size: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new business with owner user."""
        # Create company
        company = AuthService.create_company(
            db=db,
            company_name=company_name,
            email=email,
            country=country,
            domain=domain,
            phone=phone,
            size=size,
            industry=industry
        )

        # Create owner user
        user = AuthService.create_user(
            db=db,
            email=email,
            password=password,
            name=name,
            company_id=str(company.id),
            role="company_owner"
        )

        # Generate access token (include company_id so company-scoped
        # queries work immediately after signup, matching the /login token).
        access_token = AuthService.create_access_token(
            data={
                "sub": user.email,
                "user_id": str(user.id),
                "role": user.role,
                "company_id": str(company.id),
                "account_type": getattr(user, "account_type", None),
            }
        )

        return {
            "user": user,
            "company": company,
            "access_token": access_token,
            "token_type": "bearer"
        }

    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        payload = AuthService.verify_token(token)
        if not payload:
            print("[GET_CURRENT_USER] Token verification failed!")
            return None

        email = payload.get("sub")
        if not email:
            print("[GET_CURRENT_USER] No email in token payload!")
            return None

        print(f"[GET_CURRENT_USER] Token payload: {payload}")

        user = db.query(User).filter(User.email == email).first()

        if user:
            print(f"[GET_CURRENT_USER] Loaded user from DB:")
            print(f"  Email: {user.email}")
            print(f"  Company ID: {user.company_id}")
            print(f"  Company ID type: {type(user.company_id)}")
            print(f"  Has company: {user.company_id is not None}")
        else:
            print(f"[GET_CURRENT_USER] User not found in DB for email: {email}")

        return user
