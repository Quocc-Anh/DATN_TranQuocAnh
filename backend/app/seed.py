"""Khởi tạo schema và các tài khoản mặc định (admin, giáo viên demo, học sinh demo).

Dữ liệu lớp học + bài giảng được ghi từ crawler:
    python -m app.crawler.ingest --reset
"""
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import User


DEFAULT_USERS = [
    {
        "email": "admin@elearning.app",
        "full_name": "Administrator",
        "password": "Admin@123",
        "role": "teacher",
        "is_admin": True,
    },
    {
        "email": "teacher@elearning.app",
        "full_name": "Cô Lan",
        "password": "Teacher@123",
        "role": "teacher",
        "is_admin": False,
    },
    {
        "email": "student@elearning.app",
        "full_name": "Học sinh demo",
        "password": "Student@123",
        "role": "student",
        "is_admin": False,
    },
]


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for u in DEFAULT_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                existing.role = u["role"]
                continue
            db.add(
                User(
                    email=u["email"],
                    full_name=u["full_name"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                    is_admin=u["is_admin"],
                )
            )
        db.commit()
        print("Seed users xong.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
