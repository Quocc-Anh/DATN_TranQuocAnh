from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text, default="")
    content = Column(Text, default="")
    video_url = Column(String(1000), default="")
    source_url = Column(String(1000), default="")
    duration_minutes = Column(Integer, default=10)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="lessons")
