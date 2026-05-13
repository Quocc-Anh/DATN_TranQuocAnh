from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, default="")
    icon = Column(String(255), default="")
    color = Column(String(16), default="#3F51B5")
    grade_level = Column(String(50), default="THPT")
    created_at = Column(DateTime, default=datetime.utcnow)

    lessons = relationship(
        "Lesson",
        back_populates="subject",
        cascade="all, delete-orphan",
        order_by="Lesson.order_index",
    )
