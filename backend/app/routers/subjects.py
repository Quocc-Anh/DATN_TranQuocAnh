from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Lesson, LessonProgress, Subject, User
from app.schemas.subject import LessonBrief, SubjectDetail, SubjectOut

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


def _progress_map(db: Session, user_id: int, subject_id: int) -> Dict[int, int]:
    rows = (
        db.query(LessonProgress)
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .filter(Lesson.subject_id == subject_id, LessonProgress.user_id == user_id)
        .all()
    )
    return {r.lesson_id: r.progress_percent for r in rows}


def _subject_stats(progress: Dict[int, int], total: int) -> Dict[str, int]:
    completed = sum(1 for p in progress.values() if p >= 100)
    percent = 0 if total == 0 else round(completed * 100 / total)
    return {"completed_lesson_count": completed, "progress_percent": percent}


def _to_out(subject: Subject, db: Session, user_id: int) -> SubjectOut:
    total = db.query(Lesson).filter(Lesson.subject_id == subject.id).count()
    progress = _progress_map(db, user_id, subject.id)
    stats = _subject_stats(progress, total)
    return SubjectOut(
        id=subject.id,
        name=subject.name,
        slug=subject.slug,
        description=subject.description or "",
        icon=subject.icon or "",
        color=subject.color or "#3F51B5",
        grade_level=subject.grade_level or "",
        lesson_count=total,
        completed_lesson_count=stats["completed_lesson_count"],
        progress_percent=stats["progress_percent"],
    )


@router.get("", response_model=List[SubjectOut])
def list_subjects(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    subjects = db.query(Subject).order_by(Subject.id).all()
    return [_to_out(s, db, user.id) for s in subjects]


@router.get("/{subject_id}", response_model=SubjectDetail)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    base = _to_out(subject, db, user.id).dict()
    progress = _progress_map(db, user.id, subject.id)
    base["lessons"] = [
        LessonBrief(
            id=l.id,
            title=l.title,
            summary=l.summary or "",
            duration_minutes=l.duration_minutes,
            order_index=l.order_index,
            progress_percent=progress.get(l.id, 0),
            completed=progress.get(l.id, 0) >= 100,
        )
        for l in subject.lessons
    ]
    return base
