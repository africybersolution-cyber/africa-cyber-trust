"""Application configuration using Pydantic settings."""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "Africa Cyber Trust Infrastructure"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database (from .env file)
    DATABASE_URL: Optional[str] = None

    # Redis (optional for demo mode)
    REDIS_URL: Optional[str] = None

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS - simple string, we'll parse it
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002"

    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # AI Services
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Scam Detection APIs
    VIRUSTOTAL_API_KEY: str = ""
    GOOGLE_SAFE_BROWSING_KEY: str = ""

    # Payment Gateway
    PAWAPAY_API_TOKEN: str = ""  # Get from https://dashboard.pawapay.cloud/

    # Email Notifications
    GMAIL_APP_PASSWORD: str = ""  # Gmail app password for SMTP

    # Africa's Talking (SMS + WhatsApp)
    AFRICASTALKING_USERNAME: str = "sandbox"  # 'sandbox' for testing, your username for production
    AFRICASTALKING_API_KEY: str = ""
    AFRICASTALKING_FROM: str = "ACTI"  # Sender ID (max 11 chars)

    # S3 Storage
    S3_ENDPOINT_URL: str = "https://s3.amazonaws.com"
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "acti-reports"
    S3_REGION: str = "us-east-1"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@africacybertrust.com"

    # SMS
    SMS_PROVIDER: str = "twilio"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # WhatsApp
    WHATSAPP_API_KEY: str = ""

    # PawaPay Mobile Money
    PAWAPAY_API_KEY: str = ""
    PAWAPAY_USE_SANDBOX: bool = True  # False for production

    # Rate Limiting
    RATE_LIMIT_PUBLIC_CHECKS_PER_HOUR: int = 10
    RATE_LIMIT_SCANS_PER_DAY: int = 5

    # Scanning Safety Controls
    BLOCK_GOVERNMENT_DOMAINS: bool = True
    BLOCK_MILITARY_DOMAINS: bool = True
    BLOCK_FINANCIAL_DOMAINS: bool = True
    REQUIRE_MANUAL_APPROVAL_FOR_CRITICAL_INFRA: bool = True

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"


settings = Settings()
