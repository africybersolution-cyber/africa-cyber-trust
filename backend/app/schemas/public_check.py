"""Pydantic schemas for public check requests and responses."""
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


class PublicCheckURLRequest(BaseModel):
    """Request schema for URL background check."""
    url: str = Field(..., description="URL to check (website, payment link, etc.)")

    @validator("url")
    def validate_url(cls, v):
        """Ensure URL has a scheme."""
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"
        return v


class PublicCheckAppRequest(BaseModel):
    """Request schema for app background check."""
    app_identifier: str = Field(..., description="App store link or package name")
    apk_url: Optional[str] = Field(None, description="Optional: Direct APK download URL for analysis")


class PublicCheckCompanyRequest(BaseModel):
    """Request schema for company background check."""
    company_name: str = Field(..., description="Company or fintech name")
    website: Optional[str] = Field(None, description="Optional: Company website")
    country: Optional[str] = Field(None, description="Optional: Country of operation")


class RedFlag(BaseModel):
    """A single red flag/warning."""
    severity: str = Field(..., description="low, medium, high, critical")
    category: str = Field(..., description="Category of issue")
    message: str = Field(..., description="Human-readable warning message")
    evidence: Optional[str] = Field(None, description="Evidence or details")


class PublicCheckResponse(BaseModel):
    """Response schema for public background checks."""
    id: str = Field(..., description="Check ID for reference")
    input_type: str = Field(..., description="url, app, company, payment_link")
    input_value: str = Field(..., description="The checked value")
    score: int = Field(..., ge=0, le=100, description="Trust score (0-100)")
    risk_level: str = Field(..., description="low, medium, high, critical, unknown")
    summary: str = Field(..., description="Brief summary of the check result")
    red_flags: List[Dict[str, Any]] = Field(default_factory=list, description="List of warning flags")
    ai_explanation: str = Field(..., description="AI-generated explanation of the results")
    safety_advice: str = Field(..., description="Recommended actions for the user")
    created_at: datetime = Field(..., description="Timestamp of the check")

    class Config:
        from_attributes = True


class ScamReportRequest(BaseModel):
    """Request schema for reporting a scam."""
    target_value: str = Field(..., description="URL/app/company being reported")
    reason: str = Field(..., min_length=10, description="Reason for the report")
    reporter_contact: Optional[str] = Field(None, description="Optional contact for follow-up")
    evidence_url: Optional[str] = Field(None, description="Optional screenshot/proof URL")


class ScamReportResponse(BaseModel):
    """Response schema for scam report submission."""
    id: str = Field(..., description="Report ID")
    status: str = Field(..., description="pending, in_review, verified, dismissed")
    message: str = Field(..., description="Confirmation message")
    created_at: datetime

    class Config:
        from_attributes = True
