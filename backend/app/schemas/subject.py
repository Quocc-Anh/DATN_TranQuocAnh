from typing import List, Optional

from pydantic import BaseModel


class LessonBrief(BaseModel):
    id: int
    title: str
    summary: str
    duration_minutes: int
    order_index: int
    progress_percent: int = 0
    completed: bool = False

    class Config:
        orm_mode = True


class SubjectOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    icon: str
    color: str
    grade_level: str
    lesson_count: int = 0
    completed_lesson_count: int = 0
    progress_percent: int = 0

    class Config:
        orm_mode = True


class SubjectDetail(SubjectOut):
    lessons: List[LessonBrief] = []
