"""Migration nhỏ: thêm cột mới và bảng mới cho phiên bản 2.

An toàn khi chạy lại — mỗi bước đều kiểm tra tồn tại trước.
"""
from sqlalchemy import inspect, text

from app.core.database import Base, engine


def _has_column(insp, table: str, column: str) -> bool:
    try:
        cols = {c["name"] for c in insp.get_columns(table)}
    except Exception:  # noqa: BLE001
        return False
    return column in cols


def run() -> None:
    Base.metadata.create_all(bind=engine)
    insp = inspect(engine)

    with engine.begin() as conn:
        if not _has_column(insp, "users", "avatar_url"):
            print("ALTER users ADD avatar_url")
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500) DEFAULT ''"
            ))

    print("Migration xong.")


if __name__ == "__main__":
    run()
