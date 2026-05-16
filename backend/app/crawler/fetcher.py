"""Tải và bóc tách nội dung học liệu từ trang nguồn.

Logic chung:
- Tải HTML với header trình duyệt, throttle nhẹ giữa các request.
- Cắt phần thân bài (loại bỏ menu, sidebar, quảng cáo, related links).
- Trả về (title, summary, content). Content được giới hạn độ dài để hợp với app.
"""
import re
import time
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
REQUEST_TIMEOUT = 25
REQUEST_DELAY_SECONDS = 1.5  # lịch sự với máy chủ nguồn

MAX_CONTENT_CHARS = 4500
MAX_SUMMARY_CHARS = 280

# Các selector hay xuất hiện làm rác trong bài viết
NOISE_SELECTORS = [
    "script", "style", "noscript", "iframe",
    "header", "footer", "nav", "aside",
    ".breadcrumb", ".breadcrumbs", ".menu", ".menu-mobile", ".topnavcontainer",
    ".sidebar", ".banner", ".ads", ".ad", ".advertisement",
    "[class*='ads_']", "[class*='ads-']", "[id*='ads_']",
    ".share", ".social", ".tag-list", ".tags",
    ".related", ".related-post", ".related-posts",
    ".post-tag", ".post-meta", ".post-share",
    ".box-new-body", ".text-center",
    "form", "button", "input",
]

# Selector ưu tiên tìm thân bài
CONTENT_SELECTORS = [
    "div.content",
    "div#post_thread1",
    "div.cont-text",
    "article .entry-content",
    "article",
    "div.post-content",
    "div.content-detail",
    "div#content",
    "main",
]


@dataclass
class FetchedLesson:
    title: str
    summary: str
    content: str


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _strip_noise(root: Tag) -> None:
    for sel in NOISE_SELECTORS:
        for el in root.select(sel):
            el.decompose()
    # Xoá các link quảng cáo / liên kết "xem thêm" thường gặp
    for a in root.find_all("a"):
        text = (a.get_text() or "").strip().lower()
        if any(k in text for k in ("xem thêm", "xem chi tiết", "tải về", "download")):
            a.decompose()


def _pick_main(soup: BeautifulSoup) -> Optional[Tag]:
    for sel in CONTENT_SELECTORS:
        node = soup.select_one(sel)
        if node and len(node.get_text(strip=True)) > 400:
            return node
    # fallback: chọn <div> có text dài nhất trong body
    candidates = soup.find_all("div")
    best: Optional[Tag] = None
    best_len = 0
    for d in candidates:
        n = len(d.get_text(strip=True))
        if n > best_len:
            best_len = n
            best = d
    return best


def _pick_title(soup: BeautifulSoup, fallback: str) -> str:
    h1 = soup.find("h1")
    if h1:
        t = _clean_text(h1.get_text(" ", strip=True))
        if t:
            # Bỏ tiền tố quảng cáo dạng "(50+ mẫu)" hay "Top 50"
            t = re.sub(r"^\(?\d+\+?\s*(mẫu|cách)\)?\s*", "", t, flags=re.IGNORECASE).strip()
            t = re.sub(r"^\s*\(?siêu hay\)?\s*", "", t, flags=re.IGNORECASE).strip()
            if t:
                return t
    return fallback


SPAM_KEYWORDS = (
    "hot ra mắt", "ra mắt sách", "tổng hợp trên", "tổng hợp 500",
    "siêu hay", "50+ mẫu", "50 mẫu", "top 50", "top 10", "top 5",
    "từ 80k", "tài liệu vip", "vietjack đã", "vietjack.com",
    "tải về", "tải xuống", "xem thêm:", "xem thêm các",
    "lưu trữ:", "sách tổng ôn", "khoá học", "khóa học",
)


def _is_spam(line: str) -> bool:
    low = line.lower().strip()
    if not low:
        return True
    if any(k in low for k in SPAM_KEYWORDS):
        return True
    if low.startswith(("hot ", "- hot")):
        return True
    return False


def _is_toc_item(el: Tag) -> bool:
    """Một <li> chỉ chứa link điều hướng trong trang (TOC), không có nội dung."""
    text = el.get_text(" ", strip=True)
    if not text:
        return True
    links = el.find_all("a")
    if links:
        link_text = " ".join(a.get_text(" ", strip=True) for a in links).strip()
        if link_text == text or len(link_text) >= len(text) * 0.85:
            return True
    # các tên section thuần TOC
    low = text.lower()
    if any(low.startswith(p) for p in (
        "dàn ý", "sơ đồ", "phân tích bài", "phân tích nhân vật",
        "phân tích người", "phân tích đoạn", "mở bài", "kết bài",
        "bài giảng:",
    )) and len(text) < 120:
        return True
    return False


def _block_text(node: Tag) -> str:
    parts = []
    for el in node.find_all(["h2", "h3", "h4", "p", "li"], recursive=True):
        txt = el.get_text(" ", strip=True)
        if not txt or _is_spam(txt):
            continue
        if el.name == "li" and _is_toc_item(el):
            continue
        if el.name in ("h2", "h3", "h4"):
            parts.append("\n## " + txt + "\n")
        elif el.name == "li":
            parts.append("- " + txt)
        else:
            parts.append(txt)
    if not parts:
        return _clean_text(node.get_text("\n", strip=True))
    return _clean_text("\n".join(parts))


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    # cắt gọn về dấu chấm gần nhất
    last = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
    if last > limit * 0.6:
        cut = cut[: last + 1]
    return cut.rstrip() + "..."


def _summary_from(content: str, soup: BeautifulSoup) -> str:
    # ưu tiên đoạn văn dài đầu tiên trong content (đã được lọc spam)
    for line in content.split("\n"):
        line = line.strip().lstrip("-").strip()
        if line.startswith("##"):
            continue
        if len(line) > 80 and not _is_spam(line):
            return _truncate(line, MAX_SUMMARY_CHARS)
    # fallback meta description, chỉ dùng nếu không phải quảng cáo
    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        s = _clean_text(desc["content"])
        if 40 < len(s) < 400 and not _is_spam(s):
            return _truncate(s, MAX_SUMMARY_CHARS)
    return _truncate(content, MAX_SUMMARY_CHARS)


def fetch(url: str, fallback_title: str) -> FetchedLesson:
    """Tải một URL bài học, trả về tiêu đề + tóm tắt + nội dung đã làm sạch."""
    resp = requests.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "vi,en;q=0.8",
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    title = _pick_title(soup, fallback_title)
    main = _pick_main(soup)
    if main is None:
        raise ValueError(f"Không tìm thấy thân bài: {url}")
    _strip_noise(main)
    raw = _block_text(main)
    content = _truncate(raw, MAX_CONTENT_CHARS)
    summary = _summary_from(content, soup)
    time.sleep(REQUEST_DELAY_SECONDS)
    return FetchedLesson(title=title, summary=summary, content=content)
