from typing import Dict, List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_teacher, get_current_user
from app.models import (
    Classroom,
    Enrollment,
    Lesson,
    LessonProgress,
    Rating,
    User,
)
from app.schemas.classroom import (
    ClassroomCreate,
    ClassroomDetail,
    ClassroomOut,
    ClassroomUpdate,
    ContinueLearning,
    LessonBrief,
    StudentProgressRow,
    StudentStats,
    TeacherClassStats,
)

router = APIRouter(prefix="/api/classrooms", tags=["classrooms"])


# ---------- helpers ----------

def _enrolled_ids(db: Session, user_id: int) -> Set[int]:
    rows = db.query(Enrollment.classroom_id).filter(Enrollment.user_id == user_id).all()
    return {r[0] for r in rows}


def _progress_map(db: Session, user_id: int, classroom_id: int) -> Dict[int, int]:
    rows = (
        db.query(LessonProgress)
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .filter(Lesson.classroom_id == classroom_id, LessonProgress.user_id == user_id)
        .all()
    )
    return {r.lesson_id: r.progress_percent for r in rows}


def _rating_summary(db: Session, classroom_id: int):
    row = (
        db.query(func.avg(Rating.stars), func.count(Rating.id))
        .filter(Rating.classroom_id == classroom_id)
        .first()
    )
    avg = round(float(row[0]), 1) if row and row[0] is not None else 0.0
    count = int(row[1]) if row and row[1] is not None else 0
    return avg, count


def _to_out(c: Classroom, db: Session, user_id: int, enrolled_ids: Set[int]) -> ClassroomOut:
    total = db.query(Lesson).filter(Lesson.classroom_id == c.id).count()
    enrolled_count = db.query(Enrollment).filter(Enrollment.classroom_id == c.id).count()
    progress = _progress_map(db, user_id, c.id)
    completed = sum(1 for p in progress.values() if p >= 100)
    percent = 0 if total == 0 else round(completed * 100 / total)
    avg, rcount = _rating_summary(db, c.id)
    return ClassroomOut(
        id=c.id,
        title=c.title,
        subject_name=c.subject_name or "",
        description=c.description or "",
        color=c.color or "#42A5F5",
        max_students=c.max_students,
        teacher_id=c.teacher_id,
        teacher_name=c.teacher.full_name if c.teacher else "",
        lesson_count=total,
        enrolled_count=enrolled_count,
        completed_lesson_count=completed,
        progress_percent=percent,
        is_enrolled=c.id in enrolled_ids,
        average_rating=avg,
        rating_count=rcount,
    )


# ---------- teacher: list own classes with stats ----------

@router.get("/mine", response_model=List[TeacherClassStats])
def my_classes(
    db: Session = Depends(get_db), teacher: User = Depends(get_current_teacher)
):
    classes = (
        db.query(Classroom)
        .filter(Classroom.teacher_id == teacher.id)
        .order_by(Classroom.id.desc())
        .all()
    )
    result = []
    for c in classes:
        lessons = list(c.lessons)
        lesson_ids = [l.id for l in lessons]
        dur_by_id = {l.id: l.duration_minutes for l in lessons}
        total_lessons = len(lesson_ids)
        enrolled = (
            db.query(Enrollment).filter(Enrollment.classroom_id == c.id).all()
        )
        completed_count = 0
        learned_minutes = 0
        for e in enrolled:
            if total_lessons == 0:
                continue
            done_rows = (
                db.query(LessonProgress.lesson_id)
                .filter(
                    LessonProgress.user_id == e.user_id,
                    LessonProgress.lesson_id.in_(lesson_ids),
                    LessonProgress.progress_percent >= 100,
                )
                .all()
            )
            done_ids = [r[0] for r in done_rows]
            learned_minutes += sum(dur_by_id.get(i, 0) for i in done_ids)
            if len(done_ids) >= total_lessons:
                completed_count += 1
        result.append(
            TeacherClassStats(
                classroom_id=c.id,
                title=c.title,
                subject_name=c.subject_name or "",
                color=c.color or "#42A5F5",
                max_students=c.max_students,
                enrolled_count=len(enrolled),
                completed_count=completed_count,
                not_completed_count=len(enrolled) - completed_count,
                lesson_count=total_lessons,
                learned_minutes=learned_minutes,
            )
        )
    return result


@router.get("/me/stats", response_model=StudentStats)
def my_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enrolled_count = (
        db.query(Enrollment).filter(Enrollment.user_id == user.id).count()
    )
    done = (
        db.query(Lesson.duration_minutes)
        .join(LessonProgress, LessonProgress.lesson_id == Lesson.id)
        .filter(
            LessonProgress.user_id == user.id,
            LessonProgress.progress_percent >= 100,
        )
        .all()
    )
    return StudentStats(
        enrolled_count=enrolled_count,
        completed_lessons=len(done),
        learned_minutes=sum(r[0] or 0 for r in done),
    )


@router.get("/me/continue-learning", response_model=ContinueLearning)
def continue_learning(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    row = (
        db.query(LessonProgress, Lesson, Classroom)
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .join(Classroom, Lesson.classroom_id == Classroom.id)
        .join(
            Enrollment,
            (Enrollment.user_id == user.id) & (Enrollment.classroom_id == Classroom.id),
        )
        .filter(LessonProgress.user_id == user.id)
        .order_by(LessonProgress.updated_at.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Chưa có bài học nào")
    progress, lesson, classroom = row
    total = db.query(Lesson).filter(Lesson.classroom_id == classroom.id).count()
    pmap = _progress_map(db, user.id, classroom.id)
    completed = sum(1 for p in pmap.values() if p >= 100)
    class_percent = 0 if total == 0 else round(completed * 100 / total)
    return ContinueLearning(
        classroom_id=classroom.id,
        classroom_title=classroom.title,
        classroom_color=classroom.color or "#42A5F5",
        subject_name=classroom.subject_name or "",
        classroom_progress_percent=class_percent,
        lesson_id=lesson.id,
        lesson_title=lesson.title,
        lesson_progress_percent=progress.progress_percent,
        updated_at=progress.updated_at,
    )


# ---------- teacher: create / update / delete ----------

@router.post("", response_model=ClassroomOut)
def create_classroom(
    payload: ClassroomCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    c = Classroom(
        teacher_id=teacher.id,
        title=payload.title.strip(),
        subject_name=payload.subject_name.strip(),
        description=payload.description,
        color=payload.color or "#42A5F5",
        max_students=max(1, payload.max_students),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return _to_out(c, db, teacher.id, set())


@router.patch("/{classroom_id}", response_model=ClassroomOut)
def update_classroom(
    classroom_id: int,
    payload: ClassroomUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    c = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    if c.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Không phải lớp của bạn")
    if payload.title is not None:
        c.title = payload.title.strip()
    if payload.subject_name is not None:
        c.subject_name = payload.subject_name.strip()
    if payload.description is not None:
        c.description = payload.description
    if payload.color is not None:
        c.color = payload.color
    if payload.max_students is not None:
        c.max_students = max(1, payload.max_students)
    db.commit()
    db.refresh(c)
    return _to_out(c, db, teacher.id, _enrolled_ids(db, teacher.id))


@router.delete("/{classroom_id}")
def delete_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    c = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    if c.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Không phải lớp của bạn")
    db.delete(c)
    db.commit()
    return {"status": "deleted"}


@router.get("/{classroom_id}/students", response_model=List[StudentProgressRow])
def class_students(
    classroom_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(get_current_teacher),
):
    c = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    if c.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Không phải lớp của bạn")
    lesson_ids = [l.id for l in c.lessons]
    total = len(lesson_ids)
    rows: List[StudentProgressRow] = []
    enrolled = db.query(Enrollment).filter(Enrollment.classroom_id == c.id).all()
    for e in enrolled:
        student = db.query(User).filter(User.id == e.user_id).first()
        if not student:
            continue
        done = 0
        if total > 0:
            done = (
                db.query(LessonProgress)
                .filter(
                    LessonProgress.user_id == student.id,
                    LessonProgress.lesson_id.in_(lesson_ids),
                    LessonProgress.progress_percent >= 100,
                )
                .count()
            )
        rows.append(
            StudentProgressRow(
                user_id=student.id,
                full_name=student.full_name,
                email=student.email,
                avatar_url=student.avatar_url or "",
                completed_lessons=done,
                total_lessons=total,
                is_completed=(total > 0 and done >= total),
            )
        )
    return rows


# ---------- student: browse / detail / enroll ----------

@router.get("", response_model=List[ClassroomOut])
def list_classrooms(
    enrolled: bool = Query(default=False),
    available: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    classes = db.query(Classroom).order_by(Classroom.id.desc()).all()
    ids = _enrolled_ids(db, user.id)
    out = [_to_out(c, db, user.id, ids) for c in classes]
    if enrolled:
        out = [c for c in out if c.is_enrolled]
    elif available:
        out = [c for c in out if not c.is_enrolled]
    return out


@router.get("/{classroom_id}", response_model=ClassroomDetail)
def get_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    ids = _enrolled_ids(db, user.id)
    base = _to_out(c, db, user.id, ids).dict()
    progress = _progress_map(db, user.id, c.id)
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
        for l in c.lessons
    ]
    my = (
        db.query(Rating)
        .filter(Rating.user_id == user.id, Rating.classroom_id == c.id)
        .first()
    )
    base["my_rating"] = my.stars if my else 0
    return base


@router.post("/{classroom_id}/enroll", response_model=ClassroomOut)
def enroll(
    classroom_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    existing = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id, Enrollment.classroom_id == classroom_id)
        .first()
    )
    if existing is None:
        count = db.query(Enrollment).filter(Enrollment.classroom_id == classroom_id).count()
        if count >= c.max_students:
            raise HTTPException(status_code=400, detail="Lớp học đã đầy")
        db.add(Enrollment(user_id=user.id, classroom_id=classroom_id))
        db.commit()
    return _to_out(c, db, user.id, _enrolled_ids(db, user.id))


@router.delete("/{classroom_id}/enroll", response_model=ClassroomOut)
def unenroll(
    classroom_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    db.query(Enrollment).filter(
        Enrollment.user_id == user.id, Enrollment.classroom_id == classroom_id
    ).delete()
    db.commit()
    return _to_out(c, db, user.id, _enrolled_ids(db, user.id))
