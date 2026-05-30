from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Classroom, Comment, Rating, User
from app.schemas.review import (
    CommentCreate,
    CommentOut,
    RatingCreate,
    RatingSummary,
)

router = APIRouter(prefix="/api/classrooms", tags=["reviews"])


def _check_classroom(db: Session, classroom_id: int) -> Classroom:
    c = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    return c


@router.get("/{classroom_id}/comments", response_model=List[CommentOut])
def list_comments(
    classroom_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _check_classroom(db, classroom_id)
    rows = (
        db.query(Comment, User)
        .join(User, Comment.user_id == User.id)
        .filter(Comment.classroom_id == classroom_id)
        .order_by(Comment.id.asc())
        .all()
    )
    return [
        CommentOut(
            id=cm.id,
            user_id=u.id,
            user_name=u.full_name,
            user_avatar=u.avatar_url or "",
            user_role=u.role or "student",
            parent_id=cm.parent_id,
            content=cm.content,
            created_at=cm.created_at,
        )
        for cm, u in rows
    ]


@router.post("/{classroom_id}/comments", response_model=CommentOut)
def add_comment(
    classroom_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _check_classroom(db, classroom_id)
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Nội dung không được để trống")
    parent_id = payload.parent_id
    if parent_id is not None:
        parent = (
            db.query(Comment)
            .filter(Comment.id == parent_id, Comment.classroom_id == classroom_id)
            .first()
        )
        if parent is None:
            raise HTTPException(status_code=400, detail="Bình luận gốc không tồn tại")
        # chỉ cho phép 1 cấp trả lời
        if parent.parent_id is not None:
            parent_id = parent.parent_id
    cm = Comment(
        user_id=user.id,
        classroom_id=classroom_id,
        parent_id=parent_id,
        content=content,
    )
    db.add(cm)
    db.commit()
    db.refresh(cm)
    return CommentOut(
        id=cm.id,
        user_id=user.id,
        user_name=user.full_name,
        user_avatar=user.avatar_url or "",
        user_role=user.role or "student",
        parent_id=cm.parent_id,
        content=cm.content,
        created_at=cm.created_at,
    )


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cm = db.query(Comment).filter(Comment.id == comment_id).first()
    if not cm:
        raise HTTPException(status_code=404, detail="Không tìm thấy bình luận")
    if cm.user_id != user.id:
        raise HTTPException(status_code=403, detail="Không thể xoá bình luận của người khác")
    db.delete(cm)
    db.commit()
    return {"status": "deleted"}


@router.get("/{classroom_id}/rating", response_model=RatingSummary)
def get_rating(
    classroom_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _check_classroom(db, classroom_id)
    row = (
        db.query(func.avg(Rating.stars), func.count(Rating.id))
        .filter(Rating.classroom_id == classroom_id)
        .first()
    )
    avg = round(float(row[0]), 1) if row and row[0] is not None else 0.0
    count = int(row[1]) if row and row[1] is not None else 0
    mine = (
        db.query(Rating)
        .filter(Rating.user_id == user.id, Rating.classroom_id == classroom_id)
        .first()
    )
    return RatingSummary(average=avg, count=count, my_rating=mine.stars if mine else 0)


@router.post("/{classroom_id}/rating", response_model=RatingSummary)
def set_rating(
    classroom_id: int,
    payload: RatingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _check_classroom(db, classroom_id)
    mine = (
        db.query(Rating)
        .filter(Rating.user_id == user.id, Rating.classroom_id == classroom_id)
        .first()
    )
    if mine is None:
        mine = Rating(user_id=user.id, classroom_id=classroom_id, stars=payload.stars)
        db.add(mine)
    else:
        mine.stars = payload.stars
    db.commit()
    return get_rating(classroom_id, db, user)
