"""Pipeline: tải dữ liệu từ nguồn, ghi vào PostgreSQL dưới dạng các lớp học.

Mỗi "môn" trong sources.py trở thành một lớp học của giáo viên demo.

Chạy bằng: python -m app.crawler.ingest
Tuỳ chọn:
    --reset       : xoá lớp cũ của giáo viên demo trước khi ghi
    --subject X   : chỉ chạy cho slug X (ngu-van, lich-su, dia-ly, sinh-hoc)
"""
import argparse
import sys
import time
from typing import Optional

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.crawler.fetcher import fetch
from app.crawler.sources import SOURCES, SourceSubject
from app.models import Classroom, Lesson, User

DEMO_TEACHER_EMAIL = "teacher@elearning.app"


def _ensure_teacher(db) -> User:
    teacher = db.query(User).filter(User.email == DEMO_TEACHER_EMAIL).first()
    if teacher is None:
        teacher = User(
            email=DEMO_TEACHER_EMAIL,
            full_name="Cô Lan",
            hashed_password=hash_password("Teacher@123"),
            role="teacher",
        )
        db.add(teacher)
        db.flush()
    return teacher


def _ensure_classroom(db, teacher: User, src: SourceSubject) -> Classroom:
    c = (
        db.query(Classroom)
        .filter(Classroom.teacher_id == teacher.id, Classroom.title == src["name"])
        .first()
    )
    if c is None:
        c = Classroom(
            teacher_id=teacher.id,
            title=src["name"],
            subject_name=src["name"],
            description=src["description"],
            color=src["color"],
            max_students=50,
        )
        db.add(c)
        db.flush()
    else:
        c.subject_name = src["name"]
        c.description = src["description"]
        c.color = src["color"]
    return c


def _ingest_subject(db, teacher: User, src: SourceSubject) -> int:
    classroom = _ensure_classroom(db, teacher, src)
    saved = 0
    for idx, item in enumerate(src["lessons"]):
        url = item["url"]
        try:
            data = fetch(url, fallback_title=item["title"])
        except Exception as exc:  # noqa: BLE001
            print(f"  [BO QUA] {url} -> {exc}")
            continue

        lesson = (
            db.query(Lesson)
            .filter(Lesson.classroom_id == classroom.id, Lesson.source_url == url)
            .first()
        )
        if lesson is None:
            lesson = Lesson(classroom_id=classroom.id, source_url=url)
            db.add(lesson)
        lesson.title = item["title"]
        lesson.summary = data.summary
        lesson.content = data.content
        lesson.duration_minutes = item["duration"]
        lesson.order_index = idx
        db.flush()
        saved += 1
        print(f"  [OK] ({len(data.content)} ky tu) {lesson.title}")
    return saved


def run(reset: bool = False, only_slug: Optional[str] = None) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        teacher = _ensure_teacher(db)
        db.commit()

        sources = SOURCES if only_slug is None else [s for s in SOURCES if s["slug"] == only_slug]
        if not sources:
            print(f"Khong co nguon cho slug: {only_slug}")
            return

        if reset:
            print("Xoa lop cu cua giao vien demo...")
            names = [s["name"] for s in sources]
            olds = (
                db.query(Classroom)
                .filter(Classroom.teacher_id == teacher.id, Classroom.title.in_(names))
                .all()
            )
            for c in olds:
                db.delete(c)
            db.commit()

        total = 0
        for src in sources:
            print(f"\n=== {src['name']} ({src['slug']}) ===")
            t0 = time.time()
            n = _ingest_subject(db, teacher, src)
            db.commit()
            print(f"  -> {n} bai trong {time.time() - t0:.1f}s")
            total += n
        print(f"\nXong. Tong cong {total} bai da ghi vao database.")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--subject", default=None)
    args = parser.parse_args()
    run(reset=args.reset, only_slug=args.subject)


if __name__ == "__main__":
    sys.exit(main() or 0)
