"""Admin API - Training Course Management"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.core.admin_deps import require_admin, require_super_admin, log_admin_action
from app.models.user import User
from app.models.training import TrainingCourse, CourseCompletion


router = APIRouter(prefix="/api/admin/training", tags=["Admin - Training"])


# ===== REQUEST MODELS =====

class CreateCourseRequest(BaseModel):
    """Create new training course."""
    title: str
    description: Optional[str] = None
    category: str  # onboarding, sales, compliance, advanced
    difficulty: str = "beginner"
    content_type: str  # video, document, quiz, mixed
    video_url: Optional[str] = None
    document_url: Optional[str] = None
    content_html: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_required: bool = False
    is_published: bool = False
    pass_score: Optional[int] = None
    quiz_questions: Optional[dict] = None


class UpdateCourseRequest(BaseModel):
    """Update existing course."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    content_type: Optional[str] = None
    video_url: Optional[str] = None
    document_url: Optional[str] = None
    content_html: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_required: Optional[bool] = None
    is_published: Optional[bool] = None
    pass_score: Optional[int] = None
    quiz_questions: Optional[dict] = None


# ===== ENDPOINTS =====

@router.get("/courses")
async def list_courses(
    category: Optional[str] = None,
    published_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all training courses.

    Filters: category, published_only
    """
    query = db.query(TrainingCourse)

    if category:
        query = query.filter(TrainingCourse.category == category)

    if published_only:
        query = query.filter(TrainingCourse.is_published == True)

    total = query.count()
    courses = query.order_by(TrainingCourse.order_index, TrainingCourse.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "courses": [
            {
                "id": str(c.id),
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "difficulty": c.difficulty,
                "content_type": c.content_type,
                "duration_minutes": c.duration_minutes,
                "is_required": c.is_required,
                "is_published": c.is_published,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in courses
        ]
    }


@router.post("/courses")
async def create_course(
    request: CreateCourseRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Create new training course.

    Only super admins can create courses.
    """
    # Validate category
    valid_categories = ["onboarding", "sales", "compliance", "advanced"]
    if request.category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}")

    # Validate content_type
    valid_types = ["video", "document", "quiz", "mixed"]
    if request.content_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid content_type. Must be one of: {', '.join(valid_types)}")

    # Create course
    course = TrainingCourse(
        title=request.title,
        description=request.description,
        category=request.category,
        difficulty=request.difficulty,
        content_type=request.content_type,
        video_url=request.video_url,
        document_url=request.document_url,
        content_html=request.content_html,
        duration_minutes=request.duration_minutes,
        is_required=request.is_required,
        is_published=request.is_published,
        pass_score=request.pass_score,
        quiz_questions=request.quiz_questions,
        created_by=admin.id
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    # Audit log
    await log_admin_action(
        action="create_training_course",
        actor=admin,
        db=db,
        request=req,
        target_type="course",
        target_id=str(course.id),
        context_data={
            "title": course.title,
            "category": course.category,
            "is_required": course.is_required
        }
    )

    return {
        "success": True,
        "course_id": str(course.id),
        "message": "Training course created successfully"
    }


@router.get("/courses/{course_id}")
async def get_course(
    course_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get course details."""
    course = db.query(TrainingCourse).filter(TrainingCourse.id == uuid.UUID(course_id)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get completion stats
    total_completions = db.query(CourseCompletion).filter(
        CourseCompletion.course_id == course.id,
        CourseCompletion.status == "completed"
    ).count()

    in_progress = db.query(CourseCompletion).filter(
        CourseCompletion.course_id == course.id,
        CourseCompletion.status == "in_progress"
    ).count()

    return {
        "id": str(course.id),
        "title": course.title,
        "description": course.description,
        "category": course.category,
        "difficulty": course.difficulty,
        "content_type": course.content_type,
        "video_url": course.video_url,
        "document_url": course.document_url,
        "content_html": course.content_html,
        "duration_minutes": course.duration_minutes,
        "is_required": course.is_required,
        "is_published": course.is_published,
        "pass_score": course.pass_score,
        "quiz_questions": course.quiz_questions,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "stats": {
            "total_completions": total_completions,
            "in_progress": in_progress
        }
    }


@router.put("/courses/{course_id}")
async def update_course(
    course_id: str,
    request: UpdateCourseRequest,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Update training course."""
    course = db.query(TrainingCourse).filter(TrainingCourse.id == uuid.UUID(course_id)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Update fields
    if request.title is not None:
        course.title = request.title
    if request.description is not None:
        course.description = request.description
    if request.category is not None:
        course.category = request.category
    if request.difficulty is not None:
        course.difficulty = request.difficulty
    if request.content_type is not None:
        course.content_type = request.content_type
    if request.video_url is not None:
        course.video_url = request.video_url
    if request.document_url is not None:
        course.document_url = request.document_url
    if request.content_html is not None:
        course.content_html = request.content_html
    if request.duration_minutes is not None:
        course.duration_minutes = request.duration_minutes
    if request.is_required is not None:
        course.is_required = request.is_required
    if request.is_published is not None:
        course.is_published = request.is_published
    if request.pass_score is not None:
        course.pass_score = request.pass_score
    if request.quiz_questions is not None:
        course.quiz_questions = request.quiz_questions

    course.updated_at = datetime.utcnow()

    db.commit()

    # Audit log
    await log_admin_action(
        action="update_training_course",
        actor=admin,
        db=db,
        request=req,
        target_type="course",
        target_id=str(course.id),
        context_data={"title": course.title}
    )

    return {
        "success": True,
        "message": "Course updated successfully"
    }


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: str,
    req: Request,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Delete training course."""
    course = db.query(TrainingCourse).filter(TrainingCourse.id == uuid.UUID(course_id)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_title = course.title

    db.delete(course)
    db.commit()

    # Audit log
    await log_admin_action(
        action="delete_training_course",
        actor=admin,
        db=db,
        request=req,
        target_type="course",
        target_id=course_id,
        context_data={"title": course_title}
    )

    return {
        "success": True,
        "message": "Course deleted successfully"
    }


@router.get("/stats")
async def get_training_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get overall training statistics."""
    total_courses = db.query(TrainingCourse).count()
    published_courses = db.query(TrainingCourse).filter(TrainingCourse.is_published == True).count()
    required_courses = db.query(TrainingCourse).filter(TrainingCourse.is_required == True).count()

    total_completions = db.query(CourseCompletion).filter(CourseCompletion.status == "completed").count()
    in_progress = db.query(CourseCompletion).filter(CourseCompletion.status == "in_progress").count()

    return {
        "total_courses": total_courses,
        "published_courses": published_courses,
        "required_courses": required_courses,
        "total_completions": total_completions,
        "in_progress": in_progress
    }
