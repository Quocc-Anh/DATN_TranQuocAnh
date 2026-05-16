"""Khởi tạo database schema và 2 tài khoản mặc định (admin, học sinh demo).

Dữ liệu môn học và bài giảng được ghi từ crawler:
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
        "is_admin": True,
    },
    {
        "email": "student@elearning.app",
        "full_name": "Học sinh demo",
        "password": "Student@123",
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
                continue
            db.add(
                User(
                    email=u["email"],
                    full_name=u["full_name"],
                    hashed_password=hash_password(u["password"]),
                    is_admin=u["is_admin"],
                )
            )
        db.commit()
        print("Seed users xong.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
