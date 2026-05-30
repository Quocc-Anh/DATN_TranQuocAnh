from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_teacher, get_current_user
from app.models import Classroom, Lesson, LessonProgress, User
from app.schemas.lesson import (
    LessonCreate,
    LessonOut,
    LessonUpdate,
    ProgressOut,
    ProgressUpdate,
)

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


def _lesson_out(lesson: Lesson, progress_percent: int = 0) -> LessonOut:
    return LessonOut(
        id=lesson.id,
        classroom_id=lesson.classroom_id,
        title=lesson.title,
        summary=lesson.summary or "",
        content=lesson.content or "",
        video_url=lesson.video_url or "",
        source_url=lesson.source_url or "",
        duration_minutes=lesson.duration_minutes,
        order_index=lesson.order_index,
        progress_percent=progress_percent,
    )


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
    return _lesson_out(lesson, prog.progress_percent if prog else 0)


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


# ---------- teacher: lesson CRUD within own classroom ----------

def _owned_classroom(db: Session, classroom_id: int, teacher: User) -> Classroom:
    c = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    if c.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Không phải lớp của bạn")
    return c


@router.post("/classroom/{classroom_id}", response_model=LessonOut)
def add_lesson(
    classroom_id: int,
    payload: LessonCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    _owned_classroom(db, classroom_id, teacher)
    max_order = (
        db.query(func.max(Lesson.order_index))
        .filter(Lesson.classroom_id == classroom_id)
        .scalar()
    )
    next_order = 0 if max_order is None else max_order + 1
    lesson = Lesson(
        classroom_id=classroom_id,
        title=payload.title.strip(),
        summary=payload.summary,
        content=payload.content,
        video_url=payload.video_url,
        duration_minutes=max(1, payload.duration_minutes),
        order_index=next_order,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return _lesson_out(lesson)


@router.patch("/{lesson_id}/edit", response_model=LessonOut)
def edit_lesson(
    lesson_id: int,
    payload: LessonUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài học")
    _owned_classroom(db, lesson.classroom_id, teacher)
    if payload.title is not None:
        lesson.title = payload.title.strip()
    if payload.summary is not None:
        lesson.summary = payload.summary
    if payload.content is not None:
        lesson.content = payload.content
    if payload.video_url is not None:
        lesson.video_url = payload.video_url
    if payload.duration_minutes is not None:
        lesson.duration_minutes = max(1, payload.duration_minutes)
    if payload.order_index is not None:
        lesson.order_index = payload.order_index
    db.commit()
    db.refresh(lesson)
    return _lesson_out(lesson)


@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài học")
    _owned_classroom(db, lesson.classroom_id, teacher)
    db.delete(lesson)
    db.commit()
    return {"status": "deleted"}


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
