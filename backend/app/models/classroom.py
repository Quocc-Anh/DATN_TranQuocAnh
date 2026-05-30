from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    subject_name = Column(String(255), default="")
    description = Column(Text, default="")
    color = Column(String(16), default="#42A5F5")
    max_students = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User")
    lessons = relationship(
        "Lesson",
        back_populates="classroom",
        cascade="all, delete-orphan",
        order_by="Lesson.order_index",
    )
