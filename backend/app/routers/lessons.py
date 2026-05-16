from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Lesson, LessonProgress, User
from app.schemas.lesson import LessonOut, ProgressOut, ProgressUpdate

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài học")
    prog = (
        db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id)
        .first()
    )
    return LessonOut(
        id=lesson.id,
        subject_id=lesson.subject_id,
        title=lesson.title,
        summary=lesson.summary or "",
        content=lesson.content or "",
        video_url=lesson.video_url or "",
        source_url=lesson.source_url or "",
        duration_minutes=lesson.duration_minutes,
        order_index=lesson.order_index,
        progress_percent=prog.progress_percent if prog else 0,
    )


@router.post("/{lesson_id}/progress", response_model=ProgressOut)
def update_progress(
    lesson_id: int,
    payload: ProgressUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài học")
    pct = max(0, min(100, int(payload.progress_percent)))
    record = (
        db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id)
        .first()
    )
    if not record:
        record = LessonProgress(user_id=user.id, lesson_id=lesson_id, progress_percent=pct)
        db.add(record)
    else:
        record.progress_percent = pct
    record.completed_at = datetime.utcnow() if pct >= 100 else None
    db.commit()
    db.refresh(record)
    return record


@router.get("/progress/me", response_model=List[ProgressOut])
def my_progress(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return (
        db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id)
        .order_by(LessonProgress.updated_at.desc())
        .all()
    )
