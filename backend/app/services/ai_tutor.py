"""AI tutor service.

Uses Gemini REST API when GEMINI_API_KEY is set. Otherwise falls back to a
keyword-based retrieval-only response from the lesson content so the app
remains usable without external credentials.
"""
from typing import List, Optional

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import ChatMessage, Lesson, Subject

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-flash-latest:generateContent"
)

SYSTEM_PROMPT = (
    "Bạn là 'Gia sư ảo' của một ứng dụng học trực tuyến cho học sinh phổ thông Việt Nam. "
    "Trả lời ngắn gọn, rõ ràng, đúng trọng tâm bằng tiếng Việt. "
    "Khi có ngữ cảnh bài học, hãy ưu tiên dùng nội dung đó để trả lời. "
    "Nếu không biết, hãy nói thẳng là chưa rõ và gợi ý học sinh đọc lại bài tương ứng."
)


def _build_context(db: Session, lesson_id: Optional[int]) -> str:
    if lesson_id is None:
        return ""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        return ""
    subject = db.query(Subject).filter(Subject.id == lesson.subject_id).first()
    subject_name = subject.name if subject else ""
    return (
        f"Môn học: {subject_name}\n"
        f"Bài học: {lesson.title}\n"
        f"Tóm tắt: {lesson.summary}\n"
        f"Nội dung bài học:\n{lesson.content}\n"
    )


def _fallback_reply(question: str, context: str) -> str:
    if context:
        snippet = context.strip()
        if len(snippet) > 900:
            snippet = snippet[:900] + "..."
        return (
            "Hệ thống tạm thời chưa trả lời được câu hỏi của bạn. "
            "Bạn xem phần nội dung liên quan trong bài học bên dưới để tham khảo nhé:\n\n"
            f"{snippet}\n\n"
            "Sau đó thử trả lời câu hỏi: \"" + question.strip() + "\"."
        )
    return (
        "Hệ thống tạm thời chưa trả lời được câu hỏi. "
        "Vui lòng mở một bài học cụ thể rồi đặt câu hỏi liên quan đến bài đó."
    )


def _call_gemini(messages: List[dict]) -> Optional[str]:
    if not settings.GEMINI_API_KEY:
        return None
    try:
        resp = requests.post(
            GEMINI_URL,
            params={"key": settings.GEMINI_API_KEY},
            json={"contents": messages},
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        return text or None
    except requests.RequestException:
        return None


def generate_reply(
    db: Session, user_id: int, message: str, lesson_id: Optional[int]
) -> str:
    context = _build_context(db, lesson_id)
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.id.desc())
        .limit(6)
        .all()
    )
    history.reverse()

    contents: List[dict] = []
    prelude = SYSTEM_PROMPT
    if context:
        prelude += "\n\nNgữ cảnh bài học hiện tại:\n" + context
    contents.append({"role": "user", "parts": [{"text": prelude}]})
    contents.append(
        {"role": "model", "parts": [{"text": "Đã hiểu. Mình sẵn sàng giúp bạn học."}]}
    )

    for m in history:
        role = "user" if m.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.content}]})
    contents.append({"role": "user", "parts": [{"text": message}]})

    reply = _call_gemini(contents)
    if reply:
        return reply
    return _fallback_reply(message, context)
