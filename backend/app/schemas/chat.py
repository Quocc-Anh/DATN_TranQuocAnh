from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    lesson_id: Optional[int] = None


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    lesson_id: Optional[int] = None

    class Config:
        orm_mode = True


class ChatResponse(BaseModel):
    reply: ChatMessageOut
    history: List[ChatMessageOut] = []
