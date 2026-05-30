"""Dựng lại toàn bộ schema (drop + create). Dùng khi đổi cấu trúc bảng.

Chạy: python -m app.rebuild
Sau đó: python -m app.seed  và  python -m app.crawler.ingest --reset
"""
from app.core.database import Base, engine
import app.models  # noqa: F401  (đăng ký tất cả model vào metadata)


def run() -> None:
    print("Xoa toan bo bang...")
    Base.metadata.drop_all(bind=engine)
    print("Tao lai bang...")
    Base.metadata.create_all(bind=engine)
    print("Rebuild xong.")


if __name__ == "__main__":
    run()
