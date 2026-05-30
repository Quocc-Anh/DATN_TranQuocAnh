"""Dịch vụ gia sư AI.

Ưu tiên gọi AI service riêng (RAG hybrid + LangGraph). Nếu service không
sẵn sàng thì gọi thẳng Gemini REST. Nếu vẫn không có thì trả về nội dung
trích từ bài học để app vẫn dùng được.
"""
import re
from typing import List, Optional

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import ChatMessage, Classroom, Lesson

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-flash-latest:generateContent"
)

# AI service riêng (RAG + Qdrant + LangGraph) chạy Python 3.11
AI_SERVICE_URL = settings.AI_SERVICE_URL


def _call_ai_service(
    db: Session, user_id: int, message: str, lesson_id: Optional[int]
) -> Optional[str]:
    """Gọi AI service RAG. Trả None nếu service không sẵn sàng (để fallback)."""
    if not AI_SERVICE_URL:
        return None
    classroom_id = None
    if lesson_id is not None:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if lesson:
            classroom_id = lesson.classroom_id
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.id.desc())
        .limit(6)
        .all()
    )
    history.reverse()
    payload = {
        "question": message,
        "lesson_id": lesson_id,
        "classroom_id": classroom_id,
        "history": [{"role": m.role, "content": m.content} for m in history],
    }
    try:
        resp = requests.post(
            AI_SERVICE_URL.rstrip("/") + "/rag/answer",
            json=payload,
            timeout=45,
        )
        if resp.status_code != 200:
            return None
        ans = (resp.json() or {}).get("answer")
        return ans.strip() if ans else None
    except requests.RequestException:
        return None

SYSTEM_PROMPT = (
    "Bạn là 'Gia sư ảo' của một ứng dụng học trực tuyến cho học sinh phổ thông Việt Nam. "
    "Trả lời ngắn gọn, rõ ràng, đúng trọng tâm bằng tiếng Việt, dưới dạng VĂN BẢN THƯỜNG. "
    "TUYỆT ĐỐI KHÔNG dùng cú pháp Markdown hay LaTeX. "
    "Không dùng các ký tự định dạng: $, $$, **, *, #, _, ` , \\frac, \\sqrt, \\(, \\), \\[, \\]. "
    "Khi viết công thức toán, dùng ký hiệu thông thường trên một dòng "
    "(ví dụ: x = 8/2 = 4; diện tích = a x b; x^2; căn bậc hai viết là √). "
    "Nếu liệt kê các bước, dùng '1.', '2.', '3.' và xuống dòng bình thường, không in đậm. "
    "Khi có ngữ cảnh bài học, hãy ưu tiên dùng nội dung đó để trả lời. "
    "Nếu không biết, hãy nói thẳng là chưa rõ và gợi ý học sinh đọc lại bài tương ứng."
)


def _clean_markdown(text: str) -> str:
    """Loại bỏ cú pháp Markdown/LaTeX còn sót để hiển thị văn bản gọn gàng."""
    if not text:
        return text
    t = text
    # \frac{a}{b} -> a/b ; \sqrt{x} -> √(x)
    t = re.sub(r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"\1/\2", t)
    t = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"√(\1)", t)
    # các lệnh LaTeX phổ biến
    replacements = {
        "\\times": "×", "\\cdot": "·", "\\div": "÷",
        "\\le": "≤", "\\ge": "≥", "\\neq": "≠", "\\pm": "±",
        "\\(": "", "\\)": "", "\\[": "", "\\]": "", "\\,": " ",
    }
    for k, v in replacements.items():
        t = t.replace(k, v)
    # bỏ ký hiệu toán inline/đậm/nghiêng/heading/code
    t = t.replace("$$", "").replace("$", "")
    t = t.replace("**", "").replace("__", "")
    t = t.replace("`", "")
    t = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", t)   # heading markdown
    t = re.sub(r"(?m)^\s*\*\s+", "- ", t)          # bullet '* ' -> '- '
    t = re.sub(r"\\(?=[a-zA-Z])", "", t)            # backslash thừa trước chữ
    t = re.sub(r"\n{3,}", "\n\n", t)               # gom dòng trống
    return t.strip()


def _build_context(db: Session, lesson_id: Optional[int]) -> str:
    if lesson_id is None:
        return ""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        return ""
    classroom = db.query(Classroom).filter(Classroom.id == lesson.classroom_id).first()
    subject_name = ""
    if classroom:
        subject_name = classroom.subject_name or classroom.title
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
    # Ưu tiên AI service (RAG hybrid + LangGraph). Lỗi/không bật -> fallback bên dưới.
    ai_reply = _call_ai_service(db, user_id, message, lesson_id)
    if ai_reply:
        return ai_reply

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
        return _clean_markdown(reply)
    return _fallback_reply(message, context)
