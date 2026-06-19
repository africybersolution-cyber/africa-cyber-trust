"""AI verification endpoints for photo and video authenticity."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.ai_verify import (
    AIPhotoVerifyRequest,
    AIVideoVerifyRequest,
    AIVerifyResponse,
)
from app.services.ai_verifier import AIVerifierService
from app.services.ai_verification_service import ai_verification

router = APIRouter()


@router.post("/photo")
async def verify_photo(
    request_data: AIPhotoVerifyRequest,
    db: Session = Depends(get_db),
):
    """
    Verify if a photo is AI-generated or authentic using real AI (OpenAI GPT-4 Vision).

    Checks for:
    - Deepfake detection
    - AI-generated image patterns (GANs, Stable Diffusion, Midjourney)
    - Photo manipulation (Photoshop, face swaps)
    - Synthetic content markers
    - Lighting and shadow anomalies
    - Texture inconsistencies
    """
    try:
        # Use real AI verification service
        if request_data.image_url:
            result = await ai_verification.verify_photo_url(request_data.image_url)
        else:
            raise HTTPException(status_code=400, detail="image_url is required")

        return {
            "authentic": result.get("authentic", True),
            "confidence": result.get("confidence", 85),
            "analysis": result.get("analysis", ""),
            "red_flags": result.get("red_flags", []),
            "recommendation": result.get("recommendation", ""),
            "ai_model": result.get("ai_model", "unknown"),
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Photo verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Photo verification failed. Please try again.")


@router.post("/video")
async def verify_video(
    request_data: AIVideoVerifyRequest,
    db: Session = Depends(get_db),
):
    """
    Verify if a video is AI-generated or authentic using real AI analysis.

    Checks for:
    - Deepfake video detection (facial manipulation)
    - Face swap identification
    - Lip-sync anomalies
    - Temporal consistency across frames
    - Audio-visual synchronization
    - AI generation markers

    Note: Full deepfake detection requires specialized models.
    Configure API keys for production use.
    """

    try:
        # Use real AI verification service
        if request_data.video_url:
            result = await ai_verification.verify_video_url(request_data.video_url)
        else:
            raise HTTPException(status_code=400, detail="video_url is required")

        return AIVerifyResponse(
            authentic=result.get("authentic", True),
            confidence=result.get("confidence", 80),
            analysis=result.get("analysis", ""),
            red_flags=result.get("red_flags", []),
            recommendation=result.get("recommendation", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Video verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Video verification failed. Please try again.")


@router.post("/photo/upload")
async def upload_photo_for_verification(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a photo file for AI verification.

    Accepts image files (JPEG, PNG, WebP, etc.)
    Maximum file size: 10MB
    """
    print(f"[PHOTO UPLOAD] File: {file.filename}, Content-Type: {file.content_type}")

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg", "image/gif"]
    if file.content_type not in allowed_types:
        print(f"[ERROR] Invalid content type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Only JPEG, PNG, WebP, and GIF are supported."
        )

    # Validate file size (10MB max)
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    print(f"[INFO] File size: {file_size_mb:.2f} MB")

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large ({file_size_mb:.2f}MB). Maximum size is 10MB.")

    # Process the image with real AI
    try:
        print(f"[AI VERIFY] Starting verification for {file.filename}")
        result = await ai_verification.verify_photo_file(contents, file.filename or "uploaded_image")
        print(f"[SUCCESS] AI verification complete: authentic={result.get('authentic')}, confidence={result.get('confidence')}")

        return {
            "authentic": result.get("authentic", True),
            "confidence": result.get("confidence", 85),
            "analysis": result.get("analysis", ""),
            "red_flags": result.get("red_flags", []),
            "recommendation": result.get("recommendation", ""),
            "ai_model": result.get("ai_model", "unknown"),
        }

    except Exception as e:
        print(f"[ERROR] Photo verification error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"Photo verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Photo verification failed. Please try again.")


@router.post("/video/upload")
async def upload_video_for_verification(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a video file for AI verification.

    Accepts video files (MP4, WebM, MOV, etc.)
    Maximum file size: 100MB
    """
    # Validate file type
    allowed_types = ["video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only MP4, WebM, and MOV are supported.")

    # Validate file size (100MB max)
    contents = await file.read()
    if len(contents) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB.")

    # Process the video with real AI
    try:
        result = await ai_verification.verify_video_file(contents, file.filename)

        return AIVerifyResponse(
            authentic=result.get("authentic", True),
            confidence=result.get("confidence", 80),
            analysis=result.get("analysis", ""),
            red_flags=result.get("red_flags", []),
            recommendation=result.get("recommendation", ""),
        )

    except Exception as e:
        print(f"Video verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Video verification failed. Please try again.")
