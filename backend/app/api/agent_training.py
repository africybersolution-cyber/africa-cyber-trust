"""Agent Training API - Course access for agents"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.agent import Agent
from app.models.training import TrainingCourse, CourseCompletion


router = APIRouter(prefix="/api/agent/training", tags=["Agent Training"])


# ===== REQUEST MODELS =====

class StartCourseRequest(BaseModel):
    """Start a course."""
    course_id: str


class UpdateProgressRequest(BaseModel):
    """Update course progress."""
    progress_percent: int
    extra_data: Optional[dict] = None


class CompleteCourseRequest(BaseModel):
    """Mark course as completed."""
    score: Optional[int] = None


# ===== ENDPOINTS =====

@router.get("/courses")
async def list_available_courses(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all published training courses.

    Shows completion status for current agent.
    """
    # Get agent profile
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    # Get published courses
    query = db.query(TrainingCourse).filter(TrainingCourse.is_published == True)

    if category:
        query = query.filter(TrainingCourse.category == category)

    courses = query.order_by(TrainingCourse.order_index, TrainingCourse.created_at).all()

    # Get completion status for each course
    results = []
    for course in courses:
        completion = db.query(CourseCompletion).filter(
            CourseCompletion.agent_id == agent.id,
            CourseCompletion.course_id == course.id
        ).first()

        results.append({
            "id": str(course.id),
            "title": course.title,
            "description": course.description,
            "category": course.category,
            "difficulty": course.difficulty,
            "content_type": course.content_type,
            "duration_minutes": course.duration_minutes,
            "is_required": course.is_required,
            "completion": {
                "status": completion.status if completion else "not_started",
                "progress_percent": completion.progress_percent if completion else 0,
                "score": completion.score if completion else None,
                "completed_at": completion.completed_at.isoformat() if completion and completion.completed_at else None
            }
        })

    return {
        "courses": results,
        "total": len(results)
    }


@router.get("/courses/{course_id}")
async def get_course_details(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full course details including content.

    Returns video URL, document URL, or HTML content.
    """
    # Get agent profile
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    # Get course
    course = db.query(TrainingCourse).filter(
        TrainingCourse.id == uuid.UUID(course_id),
        TrainingCourse.is_published == True
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get completion status
    completion = db.query(CourseCompletion).filter(
        CourseCompletion.agent_id == agent.id,
        CourseCompletion.course_id == course.id
    ).first()

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
        "pass_score": course.pass_score,
        "quiz_questions": course.quiz_questions,
        "completion": {
            "id": str(completion.id) if completion else None,
            "status": completion.status if completion else "not_started",
            "progress_percent": completion.progress_percent if completion else 0,
            "score": completion.score if completion else None,
            "started_at": completion.started_at.isoformat() if completion else None,
            "completed_at": completion.completed_at.isoformat() if completion and completion.completed_at else None,
            "certificate_url": completion.certificate_url if completion else None
        }
    }


@router.post("/courses/{course_id}/start")
async def start_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a course (or resume if already started).
    """
    # Get agent profile
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    # Get course
    course = db.query(TrainingCourse).filter(
        TrainingCourse.id == uuid.UUID(course_id),
        TrainingCourse.is_published == True
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if already started
    completion = db.query(CourseCompletion).filter(
        CourseCompletion.agent_id == agent.id,
        CourseCompletion.course_id == course.id
    ).first()

    if completion:
        return {
            "message": "Course already started",
            "completion_id": str(completion.id),
            "status": completion.status,
            "progress_percent": completion.progress_percent
        }

    # Create new completion record
    completion = CourseCompletion(
        agent_id=agent.id,
        course_id=course.id,
        status="in_progress",
        progress_percent=0
    )

    db.add(completion)
    db.commit()
    db.refresh(completion)

    return {
        "message": "Course started",
        "completion_id": str(completion.id),
        "status": completion.status,
        "progress_percent": 0
    }


@router.patch("/courses/{course_id}/progress")
async def update_course_progress(
    course_id: str,
    request: UpdateProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update progress on a course.

    Used for tracking video watch time or document reading.
    """
    # Get agent profile
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    # Get completion record
    completion = db.query(CourseCompletion).filter(
        CourseCompletion.agent_id == agent.id,
        CourseCompletion.course_id == uuid.UUID(course_id)
    ).first()

    if not completion:
        raise HTTPException(status_code=404, detail="Course not started. Call /start first.")

    # Update progress
    completion.progress_percent = min(100, max(0, request.progress_percent))

    if request.extra_data:
        completion.extra_data = request.extra_data

    db.commit()

    return {
        "message": "Progress updated",
        "progress_percent": completion.progress_percent,
        "status": completion.status
    }


@router.post("/courses/{course_id}/complete")
async def complete_course(
    course_id: str,
    request: CompleteCourseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark course as completed.

    For quizzes, include score. For other types, just mark complete.
    """
    # Get agent profile
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    # Get course
    course = db.query(TrainingCourse).filter(
        TrainingCourse.id == uuid.UUID(course_id)
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get completion record
    completion = db.query(CourseCompletion).filter(
        CourseCompletion.agent_id == agent.id,
        CourseCompletion.course_id == course.id
    ).first()

    if not completion:
        raise HTTPException(status_code=404, detail="Course not started. Call /start first.")

    # Check if already completed
    if completion.status == "completed":
        return {
            "message": "Course already completed",
            "completion_id": str(completion.id),
            "completed_at": completion.completed_at.isoformat() if completion.completed_at else None
        }

    # For quizzes, check pass score
    if course.content_type == "quiz" and course.pass_score:
        if not request.score:
            raise HTTPException(status_code=400, detail="Score is required for quiz completion")

        completion.score = request.score

        if request.score < course.pass_score:
            completion.status = "failed"
            db.commit()
            return {
                "message": f"Quiz failed. Pass score is {course.pass_score}%",
                "score": request.score,
                "pass_score": course.pass_score,
                "status": "failed"
            }

    # Mark as completed
    completion.status = "completed"
    completion.progress_percent = 100
    completion.completed_at = datetime.utcnow()

    if request.score:
        completion.score = request.score

    db.commit()
    db.refresh(completion)

    return {
        "message": "Course completed successfully!",
        "completion_id": str(completion.id),
        "completed_at": completion.completed_at.isoformat(),
        "certificate_url": completion.certificate_url,
        "score": completion.score
    }


@router.get("/my-progress")
async def get_my_training_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get agent's overall training progress.

    Shows completed courses, in-progress courses, and required courses not started.
    """
    # Get agent profile
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="You are not an agent")

    # Get all completions
    completions = db.query(CourseCompletion).filter(
        CourseCompletion.agent_id == agent.id
    ).all()

    # Get all published courses
    all_courses = db.query(TrainingCourse).filter(
        TrainingCourse.is_published == True
    ).all()

    # Calculate stats
    completed_count = len([c for c in completions if c.status == "completed"])
    in_progress_count = len([c for c in completions if c.status == "in_progress"])

    required_courses = [c for c in all_courses if c.is_required]
    required_completed = len([
        c for c in completions
        if c.status == "completed" and any(rc.id == c.course_id for rc in required_courses)
    ])

    return {
        "total_courses": len(all_courses),
        "completed": completed_count,
        "in_progress": in_progress_count,
        "not_started": len(all_courses) - len(completions),
        "required_courses": len(required_courses),
        "required_completed": required_completed,
        "completion_rate": round((completed_count / len(all_courses) * 100) if all_courses else 0, 1)
    }
