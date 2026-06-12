"""Pydantic schemas for AI verification requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AIPhotoVerifyRequest(BaseModel):
    """Request schema for AI photo verification."""
    image_url: Optional[str] = Field(None, description="URL of the image to verify")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data")

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/photo.jpg"
            }
        }


class AIVideoVerifyRequest(BaseModel):
    """Request schema for AI video verification."""
    video_url: Optional[str] = Field(None, description="URL of the video to verify")
    video_base64: Optional[str] = Field(None, description="Base64 encoded video data")

    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://example.com/video.mp4"
            }
        }


class AIVerifyResponse(BaseModel):
    """Response schema for AI verification results."""
    id: str = Field(..., description="Verification ID")
    verification_type: str = Field(..., description="Type: 'photo' or 'video'")
    is_ai_generated: bool = Field(..., description="True if content is AI-generated")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    authenticity_score: int = Field(..., ge=0, le=100, description="Authenticity score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")

    # Detection results
    deepfake_detected: bool = Field(..., description="Deepfake detected")
    manipulation_detected: bool = Field(..., description="Manipulation detected")

    # Analysis details
    analysis: Dict[str, Any] = Field(..., description="Detailed analysis results")
    explanation: str = Field(..., description="AI-generated explanation")
    safety_advice: str = Field(..., description="Recommended actions")

    # Metadata
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(..., description="Verification timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "ver_abc123",
                "verification_type": "photo",
                "is_ai_generated": False,
                "confidence": 0.92,
                "authenticity_score": 92,
                "risk_level": "low",
                "deepfake_detected": False,
                "manipulation_detected": False,
                "analysis": {
                    "metadata_consistent": True,
                    "pixel_artifacts": False,
                    "gan_fingerprint": False
                },
                "explanation": "This image appears to be authentic based on metadata analysis and pixel-level examination.",
                "safety_advice": "Image shows strong authenticity indicators. Safe to trust.",
                "processing_time_ms": 1250,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
