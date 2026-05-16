"""Danh sách URL nguồn học liệu cho mỗi môn (sách Kết nối tri thức 12).

Mỗi entry gồm: subject_slug, danh sách bài (title gợi ý + url).
title gợi ý có thể bị ghi đè bằng <h1> trong trang gốc khi crawl.
"""
from typing import Any, Dict, List

SourceLesson = Dict[str, Any]
SourceSubject = Dict[str, Any]


SOURCES: List[SourceSubject] = [
    {
        "slug": "ngu-van",
        "name": "Ngữ Văn",
        "description": "Cảm thụ văn học, phân tích tác phẩm và rèn luyện kỹ năng viết.",
        "icon": "menu_book",
        "color": "#E53935",
        "grade_level": "Lớp 12",
        "lessons": [
            {
                "title": "Phân tích bài thơ Tây Tiến - Quang Dũng",
                "url": "https://vietjack.com/van-mau-lop-12/tay-tien.jsp",
                "duration": 25,
            },
            {
                "title": "Phân tích Vợ chồng A Phủ - Tô Hoài",
                "url": "https://vietjack.com/van-mau-lop-12/phan-tich-vo-chong-a-phu.jsp",
                "duration": 30,
            },
            {
                "title": "Phân tích Vợ nhặt - Kim Lân",
                "url": "https://vietjack.com/van-mau-lop-12/vo-nhat.jsp",
                "duration": 28,
            },
            {
                "title": "Phân tích Rừng xà nu - Nguyễn Trung Thành",
                "url": "https://vietjack.com/van-mau-lop-12/rung-xa-nu.jsp",
                "duration": 28,
            },
            {
                "title": "Phân tích Chiếc thuyền ngoài xa - Nguyễn Minh Châu",
                "url": "https://vietjack.com/van-mau-lop-12/chiec-thuyen-ngoai-xa.jsp",
                "duration": 30,
            },
        ],
    },
    {
        "slug": "lich-su",
        "name": "Lịch Sử",
        "description": "Các sự kiện và bài học lịch sử Việt Nam và thế giới hiện đại.",
        "icon": "history_edu",
        "color": "#6D4C41",
        "grade_level": "Lớp 12",
        "lessons": [
            {
                "title": "Bài 1: Liên hợp quốc",
                "url": "https://vietjack.com/lich-su-12-kn/bai-1-lien-hop-quoc.jsp",
                "duration": 25,
            },
            {
                "title": "Bài 2: Trật tự thế giới trong Chiến tranh lạnh",
                "url": "https://vietjack.com/lich-su-12-kn/bai-2-trat-tu-the-gioi-trong-chien-tranh-lanh.jsp",
                "duration": 25,
            },
            {
                "title": "Bài 3: Trật tự thế giới sau Chiến tranh lạnh",
                "url": "https://vietjack.com/lich-su-12-kn/bai-3-trat-tu-the-gioi-sau-chien-tranh-lanh.jsp",
                "duration": 22,
            },
            {
                "title": "Bài 6: Cách mạng tháng Tám năm 1945",
                "url": "https://vietjack.com/lich-su-12-kn/bai-6-cach-mang-thang-8-nam-1945.jsp",
                "duration": 30,
            },
            {
                "title": "Bài 7: Cuộc kháng chiến chống thực dân Pháp (1945-1954)",
                "url": "https://vietjack.com/lich-su-12-kn/bai-7-cuoc-khang-chien-chong-thuc-dan-phap.jsp",
                "duration": 30,
            },
            {
                "title": "Bài 8: Cuộc kháng chiến chống Mỹ cứu nước (1954-1975)",
                "url": "https://vietjack.com/lich-su-12-kn/bai-8-cuoc-khang-chien-chong-my-cuu-nuoc.jsp",
                "duration": 30,
            },
        ],
    },
    {
        "slug": "dia-ly",
        "name": "Địa Lý",
        "description": "Địa lí tự nhiên, dân cư và các vùng kinh tế Việt Nam.",
        "icon": "public",
        "color": "#1E88E5",
        "grade_level": "Lớp 12",
        "lessons": [
            {
                "title": "Bài 1: Vị trí địa lí và phạm vi lãnh thổ",
                "url": "https://vietjack.com/dia-li-12-kn/bai-1-vi-tri-dia-li-va-pham-vi-lanh-tho.jsp",
                "duration": 22,
            },
            {
                "title": "Bài 2: Thiên nhiên nhiệt đới ẩm gió mùa",
                "url": "https://vietjack.com/dia-li-12-kn/bai-2-thien-nhien-nhiet-doi-am-gio-mua.jsp",
                "duration": 25,
            },
            {
                "title": "Bài 3: Sự phân hoá đa dạng của thiên nhiên",
                "url": "https://vietjack.com/dia-li-12-kn/bai-3-su-phan-hoa-da-dang-cua-thien-nhien.jsp",
                "duration": 22,
            },
            {
                "title": "Bài 5: Vấn đề sử dụng hợp lí tài nguyên thiên nhiên và bảo vệ môi trường",
                "url": "https://vietjack.com/dia-li-12-kn/bai-5-van-de-su-dung-hop-li-tai-nguyen-thien-nhien-va-bao-ve-moi-truong.jsp",
                "duration": 22,
            },
            {
                "title": "Bài 6: Dân số Việt Nam",
                "url": "https://vietjack.com/dia-li-12-kn/bai-6-dan-so-viet-nam.jsp",
                "duration": 20,
            },
            {
                "title": "Bài 7: Lao động và việc làm",
                "url": "https://vietjack.com/dia-li-12-kn/bai-7-lao-dong-va-viec-lam.jsp",
                "duration": 20,
            },
            {
                "title": "Bài 8: Đô thị hoá",
                "url": "https://vietjack.com/dia-li-12-kn/bai-8-do-thi-hoa.jsp",
                "duration": 20,
            },
        ],
    },
    {
        "slug": "sinh-hoc",
        "name": "Sinh Học",
        "description": "Sinh học tế bào, di truyền và tiến hóa.",
        "icon": "biotech",
        "color": "#43A047",
        "grade_level": "Lớp 12",
        "lessons": [
            {
                "title": "Bài 1: DNA và cơ chế tái bản DNA",
                "url": "https://vietjack.com/sinh-hoc-12-kn/bai-1-dna-va-co-che-tai-ban-dna.jsp",
                "duration": 25,
            },
            {
                "title": "Bài 2: Gene, quá trình truyền đạt thông tin di truyền và hệ gene",
                "url": "https://vietjack.com/sinh-hoc-12-kn/bai-2-gene-qua-trinh-truyen-dat-thong-tin-di-truyen-va-he-gene.jsp",
                "duration": 25,
            },
            {
                "title": "Bài 3: Điều hoà biểu hiện gene",
                "url": "https://vietjack.com/sinh-hoc-12-kn/bai-3-dieu-hoa-bieu-hien-gene.jsp",
                "duration": 22,
            },
            {
                "title": "Bài 4: Đột biến gene",
                "url": "https://vietjack.com/sinh-hoc-12-kn/bai-4-dot-bien-gene.jsp",
                "duration": 22,
            },
            {
                "title": "Bài 5: Công nghệ di truyền",
                "url": "https://vietjack.com/sinh-hoc-12-kn/bai-5-cong-nghe-di-truyen.jsp",
                "duration": 22,
            },
            {
                "title": "Bài 7: Cấu trúc và chức năng của nhiễm sắc thể",
                "url": "https://vietjack.com/sinh-hoc-12-kn/bai-7-cau-truc-va-chuc-nang-cua-nhiem-sac-the.jsp",
                "duration": 22,
            },
            {
                "title": "Bài 8: Học thuyết di truyền của Mendel",
                "url": "https://vietjack.com/sinh-hoc-12-kn/bai-8-hoc-thuyet-di-truyen-cua-mendel.jsp",
                "duration": 25,
            },
        ],
    },
]


def by_slug(slug: str) -> SourceSubject:
    for s in SOURCES:
        if s["slug"] == slug:
            return s
    raise KeyError(slug)
