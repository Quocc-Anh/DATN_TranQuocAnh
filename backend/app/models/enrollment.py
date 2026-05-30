from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint

from app.core.database import Base


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "classroom_id", name="uq_user_classroom"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    classroom_id = Column(
        Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False
    )
    enrolled_at = Column(DateTime, default=datetime.utcnow)
