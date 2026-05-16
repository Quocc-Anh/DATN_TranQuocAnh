"""Pipeline: tải dữ liệu từ nguồn, ghi vào PostgreSQL.

Chạy bằng: python -m app.crawler.ingest
Tuỳ chọn:
    --reset       : xoá dữ liệu môn/bài cũ trước khi ghi
    --subject X   : chỉ chạy cho slug X (ngu-van, lich-su, dia-ly, sinh-hoc)
"""
import argparse
import sys
import time
from typing import Optional

from app.core.database import Base, SessionLocal, engine
from app.crawler.fetcher import fetch
from app.crawler.sources import SOURCES, SourceSubject
from app.models import Lesson, Subject


def _ensure_subject(db, src: SourceSubject) -> Subject:
    subject = db.query(Subject).filter(Subject.slug == src["slug"]).first()
    if subject is None:
        subject = Subject(
            slug=src["slug"],
            name=src["name"],
            description=src["description"],
            icon=src["icon"],
            color=src["color"],
            grade_level=src["grade_level"],
        )
        db.add(subject)
        db.flush()
    else:
        subject.name = src["name"]
        subject.description = src["description"]
        subject.icon = src["icon"]
        subject.color = src["color"]
        subject.grade_level = src["grade_level"]
    return subject


def _ingest_subject(db, src: SourceSubject) -> int:
    subject = _ensure_subject(db, src)
    saved = 0
    for idx, item in enumerate(src["lessons"]):
        url = item["url"]
        try:
            data = fetch(url, fallback_title=item["title"])
        except Exception as exc:  # noqa: BLE001
            print(f"  [BỎ QUA] {url} -> {exc}")
            continue

        lesson = (
            db.query(Lesson)
            .filter(Lesson.subject_id == subject.id, Lesson.source_url == url)
            .first()
        )
        if lesson is None:
            lesson = Lesson(subject_id=subject.id, source_url=url)
            db.add(lesson)
        lesson.title = item["title"]
        lesson.summary = data.summary
        lesson.content = data.content
        lesson.duration_minutes = item["duration"]
        lesson.order_index = idx
        db.flush()
        saved += 1
        print(f"  [OK] ({len(data.content)} ký tự) {lesson.title}")
    return saved


def run(reset: bool = False, only_slug: Optional[str] = None) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        sources = SOURCES if only_slug is None else [s for s in SOURCES if s["slug"] == only_slug]
        if not sources:
            print(f"Không có nguồn cho slug: {only_slug}")
            return

        if reset:
            print("Xoá dữ liệu môn/bài cũ...")
            for src in sources:
                subj = db.query(Subject).filter(Subject.slug == src["slug"]).first()
                if subj:
                    db.query(Lesson).filter(Lesson.subject_id == subj.id).delete()
                    db.delete(subj)
            db.commit()

        total = 0
        for src in sources:
            print(f"\n=== {src['name']} ({src['slug']}) ===")
            t0 = time.time()
            n = _ingest_subject(db, src)
            db.commit()
            print(f"  -> {n} bài được lưu trong {time.time() - t0:.1f}s")
            total += n
        print(f"\nXong. Tổng cộng {total} bài đã ghi vào database.")
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
