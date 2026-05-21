from typing import Dict, List, Set

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Enrollment, Lesson, LessonProgress, Subject, User
from app.schemas.subject import (
    ContinueLearning,
    LessonBrief,
    SubjectDetail,
    SubjectOut,
)

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


def _enrolled_ids(db: Session, user_id: int) -> Set[int]:
    rows = db.query(Enrollment.subject_id).filter(Enrollment.user_id == user_id).all()
    return {r[0] for r in rows}


def _progress_map(db: Session, user_id: int, subject_id: int) -> Dict[int, int]:
    rows = (
        db.query(LessonProgress)
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .filter(Lesson.subject_id == subject_id, LessonProgress.user_id == user_id)
        .all()
    )
    return {r.lesson_id: r.progress_percent for r in rows}


def _to_out(subject: Subject, db: Session, user_id: int, enrolled_ids: Set[int]) -> SubjectOut:
    total = db.query(Lesson).filter(Lesson.subject_id == subject.id).count()
    progress = _progress_map(db, user_id, subject.id)
    completed = sum(1 for p in progress.values() if p >= 100)
    percent = 0 if total == 0 else round(completed * 100 / total)
    return SubjectOut(
        id=subject.id,
        name=subject.name,
        slug=subject.slug,
        description=subject.description or "",
        icon=subject.icon or "",
        color=subject.color or "#42A5F5",
        grade_level=subject.grade_level or "",
        lesson_count=total,
        completed_lesson_count=completed,
        progress_percent=percent,
        is_enrolled=subject.id in enrolled_ids,
    )


@router.get("", response_model=List[SubjectOut])
def list_subjects(
    enrolled: bool = Query(default=False, description="Chỉ lấy môn đã đăng ký"),
    available: bool = Query(default=False, description="Chỉ lấy môn chưa đăng ký"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    subjects = db.query(Subject).order_by(Subject.id).all()
    ids = _enrolled_ids(db, user.id)
    out = [_to_out(s, db, user.id, ids) for s in subjects]
    if enrolled:
        out = [s for s in out if s.is_enrolled]
    elif available:
        out = [s for s in out if not s.is_enrolled]
    return out


@router.get("/{subject_id}", response_model=SubjectDetail)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    ids = _enrolled_ids(db, user.id)
    base = _to_out(subject, db, user.id, ids).dict()
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


@router.post("/{subject_id}/enroll", response_model=SubjectOut)
def enroll(
    subject_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    existing = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id, Enrollment.subject_id == subject_id)
        .first()
    )
    if existing is None:
        db.add(Enrollment(user_id=user.id, subject_id=subject_id))
        db.commit()
    return _to_out(subject, db, user.id, _enrolled_ids(db, user.id))


@router.delete("/{subject_id}/enroll", response_model=SubjectOut)
def unenroll(
    subject_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    db.query(Enrollment).filter(
        Enrollment.user_id == user.id, Enrollment.subject_id == subject_id
    ).delete()
    db.commit()
    return _to_out(subject, db, user.id, _enrolled_ids(db, user.id))


@router.get("/me/continue-learning", response_model=ContinueLearning)
def continue_learning(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """Bài học mới nhất user đã chạm vào (trong số môn đã đăng ký)."""
    row = (
        db.query(LessonProgress, Lesson, Subject)
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .join(Subject, Lesson.subject_id == Subject.id)
        .join(
            Enrollment,
            (Enrollment.user_id == user.id) & (Enrollment.subject_id == Subject.id),
        )
        .filter(LessonProgress.user_id == user.id)
        .order_by(LessonProgress.updated_at.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Chưa có bài học nào")
    progress, lesson, subject = row
    return ContinueLearning(
        subject_id=subject.id,
        subject_name=subject.name,
        subject_color=subject.color or "#42A5F5",
        subject_slug=subject.slug,
        lesson_id=lesson.id,
        lesson_title=lesson.title,
        lesson_progress_percent=progress.progress_percent,
        updated_at=progress.updated_at,
    )
