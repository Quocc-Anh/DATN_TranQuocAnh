from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LessonOut(BaseModel):
    id: int
    subject_id: int
    title: str
    summary: str
    content: str
    video_url: str
    duration_minutes: int
    order_index: int
    progress_percent: int = 0

    class Config:
        orm_mode = True


class ProgressUpdate(BaseModel):
    progress_percent: int


class ProgressOut(BaseModel):
    lesson_id: int
    progress_percent: int
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True
