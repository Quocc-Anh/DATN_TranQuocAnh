from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import ChatMessage, User
from app.schemas.chat import ChatMessageOut, ChatRequest, ChatResponse
from app.services.ai_tutor import generate_reply

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_msg = ChatMessage(
        user_id=user.id,
        lesson_id=payload.lesson_id,
        role="user",
        content=payload.message.strip(),
    )
    db.add(user_msg)
    db.commit()

    reply_text = generate_reply(db, user.id, payload.message, payload.lesson_id)

    bot_msg = ChatMessage(
        user_id=user.id,
        lesson_id=payload.lesson_id,
        role="assistant",
        content=reply_text,
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.id.desc())
        .limit(20)
        .all()
    )
    history.reverse()

    return ChatResponse(
        reply=ChatMessageOut.from_orm(bot_msg),
        history=[ChatMessageOut.from_orm(m) for m in history],
    )


@router.get("/history", response_model=List[ChatMessageOut])
def history(
    lesson_id: Optional[int] = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(ChatMessage).filter(ChatMessage.user_id == user.id)
    if lesson_id is not None:
        q = q.filter(ChatMessage.lesson_id == lesson_id)
    rows = q.order_by(ChatMessage.id.desc()).limit(limit).all()
    rows.reverse()
    return rows
