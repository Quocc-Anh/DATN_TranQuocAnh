from datetime import datetime
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


class ClassroomCreate(BaseModel):
    title: str
    subject_name: str = ""
    description: str = ""
    color: str = "#42A5F5"
    max_students: int = 50


class ClassroomUpdate(BaseModel):
    title: Optional[str] = None
    subject_name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    max_students: Optional[int] = None


class ClassroomOut(BaseModel):
    id: int
    title: str
    subject_name: str
    description: str
    color: str
    max_students: int
    teacher_id: int
    teacher_name: str
    lesson_count: int = 0
    enrolled_count: int = 0
    completed_lesson_count: int = 0
    progress_percent: int = 0
    is_enrolled: bool = False
    average_rating: float = 0.0
    rating_count: int = 0

    class Config:
        orm_mode = True


class ClassroomDetail(ClassroomOut):
    lessons: List[LessonBrief] = []
    my_rating: int = 0


class TeacherClassStats(BaseModel):
    classroom_id: int
    title: str
    subject_name: str
    color: str
    max_students: int
    enrolled_count: int
    completed_count: int
    not_completed_count: int
    lesson_count: int
    learned_minutes: int = 0


class StudentProgressRow(BaseModel):
    user_id: int
    full_name: str
    email: str
    avatar_url: str = ""
    completed_lessons: int
    total_lessons: int
    is_completed: bool


class StudentStats(BaseModel):
    enrolled_count: int
    completed_lessons: int
    learned_minutes: int


class ContinueLearning(BaseModel):
    classroom_id: int
    classroom_title: str
    classroom_color: str
    subject_name: str
    classroom_progress_percent: int
    lesson_id: int
    lesson_title: str
    lesson_progress_percent: int
    updated_at: Optional[datetime] = None
