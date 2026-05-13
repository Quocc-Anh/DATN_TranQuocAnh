"""Seed initial data: 4 subjects with sample lessons and an admin user."""
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Lesson, Subject, User


SUBJECTS = [
    {
        "name": "Ngữ Văn",
        "slug": "ngu-van",
        "description": "Cảm thụ văn học, phân tích tác phẩm và rèn luyện kỹ năng viết.",
        "icon": "menu_book",
        "color": "#E53935",
        "grade_level": "Lớp 12",
        "lessons": [
            {
                "title": "Khái quát văn học Việt Nam từ Cách mạng tháng Tám 1945 đến hết thế kỉ XX",
                "summary": "Tổng quan các chặng đường phát triển, thành tựu và đặc điểm cơ bản của văn học Việt Nam giai đoạn 1945 – 2000.",
                "duration_minutes": 25,
                "content": (
                    "Văn học Việt Nam từ 1945 đến hết thế kỉ XX vận động qua ba chặng lớn: 1945-1954, "
                    "1955-1975 và sau 1975.\n\n"
                    "1) Giai đoạn 1945-1954 gắn với cuộc kháng chiến chống Pháp, văn học mang khuynh hướng "
                    "sử thi, cảm hứng yêu nước, đề cao hình tượng nhân dân và người chiến sĩ. Tác phẩm tiêu biểu: "
                    "Đôi mắt (Nam Cao), Vợ chồng A Phủ (Tô Hoài), Tây Tiến (Quang Dũng).\n\n"
                    "2) Giai đoạn 1955-1975, văn học phát triển trong điều kiện đất nước chia cắt, vừa xây dựng "
                    "chủ nghĩa xã hội ở miền Bắc, vừa chống Mĩ ở miền Nam. Khuynh hướng sử thi và cảm hứng lãng "
                    "mạn tiếp tục là dòng chủ đạo. Tác phẩm tiêu biểu: Người lái đò sông Đà (Nguyễn Tuân), "
                    "Rừng xà nu (Nguyễn Trung Thành), Đất nước (Nguyễn Khoa Điềm).\n\n"
                    "3) Sau 1975, đặc biệt từ 1986, văn học đổi mới mạnh mẽ: hướng về đời tư - thế sự, đề cao "
                    "cá nhân, đa dạng giọng điệu. Tác phẩm tiêu biểu: Chiếc thuyền ngoài xa (Nguyễn Minh Châu), "
                    "Một người Hà Nội (Nguyễn Khải).\n\n"
                    "Đặc điểm chung của cả giai đoạn: phục vụ cách mạng, gắn với vận mệnh dân tộc, mang tính "
                    "nhân dân sâu sắc và liên tục cách tân về tư tưởng - nghệ thuật."
                ),
            },
            {
                "title": "Phân tích bài thơ Tây Tiến - Quang Dũng",
                "summary": "Bút pháp lãng mạn hào hùng và hình tượng người lính Tây Tiến hào hoa, bi tráng.",
                "duration_minutes": 30,
                "content": (
                    "Bài thơ Tây Tiến (1948) của Quang Dũng khắc họa hình tượng đoàn binh Tây Tiến và thiên "
                    "nhiên miền Tây Bắc hùng vĩ, dữ dội mà thơ mộng.\n\n"
                    "- Mạch cảm xúc nỗi nhớ: 'Sông Mã xa rồi Tây Tiến ơi! / Nhớ về rừng núi nhớ chơi vơi' - "
                    "tiếng gọi tha thiết mở đầu mạch hồi tưởng.\n"
                    "- Bức tranh thiên nhiên: vừa hiểm trở ('Dốc lên khúc khuỷu dốc thăm thẳm'), vừa thơ mộng "
                    "('Nhà ai Pha Luông mưa xa khơi').\n"
                    "- Hình tượng người lính Tây Tiến: hào hoa, lãng mạn ('Đêm mơ Hà Nội dáng kiều thơm'), "
                    "đồng thời bi tráng ('Áo bào thay chiếu anh về đất / Sông Mã gầm lên khúc độc hành').\n\n"
                    "Bút pháp lãng mạn kết hợp hiện thực, ngôn ngữ giàu chất tạo hình, giọng điệu hào hùng "
                    "khiến Tây Tiến trở thành một trong những bài thơ kháng chiến tiêu biểu nhất."
                ),
            },
            {
                "title": "Phân tích nhân vật Mị trong 'Vợ chồng A Phủ' - Tô Hoài",
                "summary": "Sức sống tiềm tàng và hành trình tự giải thoát của nhân vật Mị.",
                "duration_minutes": 28,
                "content": (
                    "Mị là cô gái trẻ đẹp, hiếu thảo, bị bắt làm con dâu gạt nợ cho nhà thống lí Pá Tra. "
                    "Cuộc sống đày đọa khiến Mị tê liệt cảm xúc: 'lùi lũi như con rùa nuôi trong xó cửa'.\n\n"
                    "Tuy nhiên, sức sống tiềm tàng vẫn âm ỉ. Đêm tình mùa xuân, tiếng sáo gọi bạn tình đánh thức "
                    "khát vọng sống và tuổi trẻ trong Mị: cô lấy hũ rượu uống ực từng bát, chuẩn bị đi chơi. "
                    "Bị A Sử trói đứng, Mị vẫn 'vùng bước đi' trong tâm tưởng.\n\n"
                    "Cao trào là đêm cứu A Phủ. Nhìn dòng nước mắt của A Phủ, Mị từ thương mình đến thương người, "
                    "rồi cắt dây trói cho A Phủ và bỏ trốn theo: 'A Phủ cho tôi đi… Ở đây thì chết mất.' "
                    "Hành động giải thoát ấy thể hiện giá trị nhân đạo sâu sắc của tác phẩm: dù bị vùi dập, "
                    "khát vọng tự do và hạnh phúc của con người vẫn không thể bị dập tắt."
                ),
            },
            {
                "title": "Nghị luận xã hội: cách triển khai bài viết",
                "summary": "Bố cục, dẫn chứng và kỹ năng lập luận cho bài nghị luận xã hội.",
                "duration_minutes": 20,
                "content": (
                    "Bài nghị luận xã hội thường gồm 3 phần: mở bài (dẫn dắt và nêu vấn đề), thân bài (giải "
                    "thích - bàn luận - chứng minh - liên hệ - phản đề), kết bài (khẳng định và bài học).\n\n"
                    "Một số lưu ý:\n"
                    "- Giải thích từ khóa ngắn gọn, đi thẳng vào ý nghĩa.\n"
                    "- Bàn luận theo nhiều mặt: biểu hiện, nguyên nhân, ý nghĩa/hậu quả.\n"
                    "- Dẫn chứng nên thực tế, gần gũi, ưu tiên các nhân vật có thật và có chiều sâu.\n"
                    "- Phản đề: chỉ ra mặt trái hoặc trường hợp ngoại lệ để bài viết khách quan.\n"
                    "- Liên hệ bản thân: nêu hành động cụ thể, tránh khẩu hiệu sáo rỗng."
                ),
            },
        ],
    },
    {
        "name": "Lịch Sử",
        "slug": "lich-su",
        "description": "Các sự kiện và bài học lịch sử Việt Nam và thế giới hiện đại.",
        "icon": "history_edu",
        "color": "#6D4C41",
        "grade_level": "Lớp 12",
        "lessons": [
            {
                "title": "Cách mạng tháng Tám năm 1945",
                "summary": "Bối cảnh, diễn biến, ý nghĩa lịch sử của Cách mạng tháng Tám.",
                "duration_minutes": 25,
                "content": (
                    "Cách mạng tháng Tám 1945 nổ ra trong bối cảnh Nhật đầu hàng Đồng minh (15/8/1945), tạo "
                    "thời cơ 'ngàn năm có một' cho dân tộc Việt Nam.\n\n"
                    "Trình tự sự kiện chính:\n"
                    "- 13/8/1945: Trung ương Đảng và Tổng bộ Việt Minh thành lập Ủy ban Khởi nghĩa toàn quốc, "
                    "ra Quân lệnh số 1 phát động Tổng khởi nghĩa.\n"
                    "- 14-15/8/1945: Hội nghị toàn quốc của Đảng tại Tân Trào quyết định khởi nghĩa.\n"
                    "- 16-17/8/1945: Đại hội Quốc dân Tân Trào, thông qua 10 chính sách của Việt Minh, lập "
                    "Ủy ban Dân tộc Giải phóng Việt Nam do Hồ Chí Minh đứng đầu.\n"
                    "- 19/8/1945: Khởi nghĩa thắng lợi ở Hà Nội.\n"
                    "- 23/8 tại Huế, 25/8 tại Sài Gòn: khởi nghĩa thắng lợi.\n"
                    "- 2/9/1945: Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập, khai sinh nước Việt Nam Dân chủ "
                    "Cộng hòa.\n\n"
                    "Ý nghĩa: chấm dứt ách thống trị của thực dân Pháp gần 100 năm, lật đổ chế độ phong kiến, "
                    "mở ra kỉ nguyên độc lập - tự do và phong trào giải phóng dân tộc thuộc địa."
                ),
            },
            {
                "title": "Chiến dịch Điện Biên Phủ 1954",
                "summary": "Diễn biến và ý nghĩa của chiến thắng Điện Biên Phủ.",
                "duration_minutes": 30,
                "content": (
                    "Chiến dịch Điện Biên Phủ (13/3 - 7/5/1954) là đỉnh cao cuộc kháng chiến chống Pháp.\n\n"
                    "Pháp xây dựng Điện Biên Phủ thành tập đoàn cứ điểm mạnh nhất Đông Dương với 49 cứ điểm, "
                    "chia làm 3 phân khu. Chủ trương ta: chuyển từ phương châm 'đánh nhanh thắng nhanh' sang "
                    "'đánh chắc tiến chắc'.\n\n"
                    "Ba đợt tấn công:\n"
                    "- Đợt 1 (13-17/3): tiêu diệt phân khu Bắc (Him Lam, Độc Lập, Bản Kéo).\n"
                    "- Đợt 2 (30/3-26/4): đánh chiếm các cao điểm phía Đông, siết chặt vòng vây.\n"
                    "- Đợt 3 (1-7/5): tổng công kích, 17h30 ngày 7/5/1954 bắt sống tướng De Castries và toàn bộ "
                    "Bộ Chỉ huy địch.\n\n"
                    "Ý nghĩa: đập tan kế hoạch Nava, buộc Pháp kí Hiệp định Genève (21/7/1954), giải phóng miền "
                    "Bắc, cổ vũ phong trào giải phóng dân tộc toàn thế giới."
                ),
            },
            {
                "title": "Đại thắng mùa Xuân 1975",
                "summary": "Ba chiến dịch lớn dẫn đến giải phóng hoàn toàn miền Nam.",
                "duration_minutes": 30,
                "content": (
                    "Đại thắng mùa Xuân 1975 gồm ba chiến dịch lớn:\n\n"
                    "1) Chiến dịch Tây Nguyên (4/3 - 24/3/1975): mở màn bằng trận đánh Buôn Ma Thuột (10/3), "
                    "tạo bước ngoặt chiến lược, giải phóng Tây Nguyên.\n\n"
                    "2) Chiến dịch Huế - Đà Nẵng (21/3 - 29/3/1975): giải phóng Huế (26/3) và Đà Nẵng (29/3).\n\n"
                    "3) Chiến dịch Hồ Chí Minh (26/4 - 30/4/1975): 5 cánh quân tiến vào Sài Gòn, 11h30 ngày "
                    "30/4/1975, xe tăng quân giải phóng tiến vào Dinh Độc Lập, Tổng thống Dương Văn Minh tuyên "
                    "bố đầu hàng vô điều kiện.\n\n"
                    "Ý nghĩa: chấm dứt 21 năm kháng chiến chống Mĩ, thống nhất đất nước, mở ra kỉ nguyên cả "
                    "nước độc lập, thống nhất, đi lên chủ nghĩa xã hội."
                ),
            },
            {
                "title": "Trật tự thế giới sau Chiến tranh lạnh",
                "summary": "Sự sụp đổ Liên Xô và xu thế đa cực sau 1991.",
                "duration_minutes": 20,
                "content": (
                    "Chiến tranh lạnh chấm dứt năm 1989 (cuộc gặp Malta giữa Bush và Gorbachev). Năm 1991, "
                    "Liên Xô tan rã, trật tự hai cực Ianta sụp đổ.\n\n"
                    "Xu thế chính của thế giới sau Chiến tranh lạnh:\n"
                    "- Hình thành trật tự đa cực với nhiều trung tâm: Mĩ, EU, Nhật Bản, Trung Quốc, Nga.\n"
                    "- Hòa bình, hợp tác, phát triển kinh tế trở thành xu thế chủ đạo.\n"
                    "- Cách mạng khoa học - công nghệ và toàn cầu hóa diễn ra mạnh mẽ.\n"
                    "- Tuy nhiên vẫn tồn tại xung đột sắc tộc, tôn giáo và chủ nghĩa khủng bố."
                ),
            },
        ],
    },
    {
        "name": "Địa Lý",
        "slug": "dia-ly",
        "description": "Địa lí tự nhiên, dân cư và các vùng kinh tế Việt Nam.",
        "icon": "public",
        "color": "#1E88E5",
        "grade_level": "Lớp 12",
        "lessons": [
            {
                "title": "Vị trí địa lí và phạm vi lãnh thổ Việt Nam",
                "summary": "Tọa độ, hình dạng lãnh thổ và ý nghĩa vị trí địa lí.",
                "duration_minutes": 22,
                "content": (
                    "Việt Nam nằm ở rìa phía đông bán đảo Đông Dương, gần trung tâm Đông Nam Á.\n\n"
                    "Tọa độ địa lí phần đất liền:\n"
                    "- Điểm cực Bắc: 23°23'B (xã Lũng Cú, Hà Giang).\n"
                    "- Điểm cực Nam: 8°34'B (xã Đất Mũi, Cà Mau).\n"
                    "- Điểm cực Tây: 102°09'Đ (xã Sín Thầu, Điện Biên).\n"
                    "- Điểm cực Đông: 109°24'Đ (xã Vạn Thạnh, Khánh Hòa).\n\n"
                    "Phạm vi lãnh thổ gồm: vùng đất (đất liền + đảo), vùng biển (nội thủy, lãnh hải, vùng tiếp "
                    "giáp, đặc quyền kinh tế và thềm lục địa) và vùng trời.\n\n"
                    "Ý nghĩa vị trí:\n"
                    "- Tự nhiên: thiên nhiên nhiệt đới ẩm gió mùa, đa dạng sinh học cao; nhiều thiên tai.\n"
                    "- Kinh tế - xã hội: thuận lợi giao lưu khu vực, cửa ngõ ra biển; gần các tuyến hàng hải quốc tế.\n"
                    "- Quốc phòng: vị trí chiến lược ở Biển Đông."
                ),
            },
            {
                "title": "Đặc điểm thiên nhiên nhiệt đới ẩm gió mùa",
                "summary": "Khí hậu, sông ngòi, đất và sinh vật mang tính nhiệt đới ẩm gió mùa.",
                "duration_minutes": 25,
                "content": (
                    "Khí hậu: nhiệt độ trung bình năm trên 20°C, lượng mưa lớn (1.500-2.000mm), độ ẩm cao "
                    "(trên 80%). Hai mùa gió chính: gió mùa mùa đông (lạnh khô ở miền Bắc) và gió mùa mùa hạ "
                    "(nóng ẩm, gây mưa lớn).\n\n"
                    "Sông ngòi: dày đặc, nhiều nước, giàu phù sa; chế độ nước theo mùa.\n\n"
                    "Đất: chủ yếu là đất feralit, dễ rửa trôi nếu mất rừng.\n\n"
                    "Sinh vật: hệ sinh thái rừng nhiệt đới ẩm gió mùa với nhiều tầng tán, đa dạng loài.\n\n"
                    "Ảnh hưởng đến sản xuất và đời sống: tạo điều kiện thâm canh, đa dạng cây trồng vật nuôi, "
                    "nhưng cũng gây nhiều thiên tai (bão, lũ, hạn hán) và phải đối mặt với biến đổi khí hậu."
                ),
            },
            {
                "title": "Đặc điểm dân số và phân bố dân cư",
                "summary": "Quy mô, cơ cấu và phân bố dân cư Việt Nam.",
                "duration_minutes": 20,
                "content": (
                    "Việt Nam có quy mô dân số lớn (~100 triệu người), nhiều thành phần dân tộc (54 dân tộc), "
                    "cơ cấu dân số đang chuyển từ trẻ sang già, đang trong thời kì 'cơ cấu dân số vàng'.\n\n"
                    "Phân bố dân cư không đều:\n"
                    "- Tập trung ở đồng bằng, ven biển và đô thị; thưa thớt ở miền núi.\n"
                    "- Dân cư đô thị tăng nhanh do quá trình đô thị hóa.\n\n"
                    "Hệ quả:\n"
                    "- Sức ép lên đất đai, việc làm, môi trường ở vùng đông dân.\n"
                    "- Thiếu lao động ở vùng núi, ảnh hưởng đến khai thác tài nguyên.\n\n"
                    "Giải pháp: phân bố lại dân cư - lao động, đẩy mạnh đô thị hóa hợp lí, phát triển vùng "
                    "kinh tế trọng điểm."
                ),
            },
            {
                "title": "Vùng kinh tế trọng điểm phía Nam",
                "summary": "Vai trò, thế mạnh và hướng phát triển vùng kinh tế trọng điểm phía Nam.",
                "duration_minutes": 25,
                "content": (
                    "Vùng kinh tế trọng điểm phía Nam gồm TP.HCM, Bình Dương, Bà Rịa - Vũng Tàu, Đồng Nai, "
                    "Tây Ninh, Bình Phước, Long An, Tiền Giang. Đây là vùng kinh tế phát triển nhất cả nước.\n\n"
                    "Thế mạnh:\n"
                    "- Vị trí trung tâm Đông Nam Bộ, gần các tuyến hàng hải quốc tế.\n"
                    "- Tài nguyên dầu khí thềm lục địa lớn nhất nước.\n"
                    "- Cơ sở hạ tầng, lao động kĩ thuật cao, thu hút mạnh đầu tư nước ngoài.\n\n"
                    "Vai trò:\n"
                    "- Đóng góp khoảng 40% GDP cả nước.\n"
                    "- Là trung tâm công nghiệp, dịch vụ, xuất khẩu và đầu tàu kinh tế.\n\n"
                    "Hướng phát triển: chuyển dịch sang công nghiệp công nghệ cao, dịch vụ chất lượng cao, "
                    "đồng thời giải quyết ô nhiễm môi trường và giãn dân tại TP.HCM."
                ),
            },
        ],
    },
    {
        "name": "Sinh Học",
        "slug": "sinh-hoc",
        "description": "Sinh học tế bào, di truyền và tiến hóa.",
        "icon": "biotech",
        "color": "#43A047",
        "grade_level": "Lớp 12",
        "lessons": [
            {
                "title": "Cấu trúc và chức năng của ADN",
                "summary": "Cấu tạo hóa học, cấu trúc xoắn kép và chức năng của phân tử ADN.",
                "duration_minutes": 25,
                "content": (
                    "ADN (axit deoxyribonucleic) là vật chất di truyền cấp phân tử.\n\n"
                    "Cấu tạo hóa học: ADN là một polime sinh học, đơn phân là nucleotit. Mỗi nucleotit gồm: "
                    "1 nhóm phosphate, 1 đường deoxyribose, 1 trong 4 loại bazơ nitơ A, T, G, X.\n\n"
                    "Cấu trúc không gian (Watson - Crick, 1953): hai mạch polinucleotit xoắn song song ngược "
                    "chiều quanh một trục. Các bazơ liên kết theo nguyên tắc bổ sung: A=T (2 liên kết hidro), "
                    "G≡X (3 liên kết hidro). Chu kì xoắn ≈ 34Å gồm 10 cặp nucleotit, đường kính 20Å.\n\n"
                    "Chức năng:\n"
                    "- Lưu giữ thông tin di truyền trong trình tự các nucleotit.\n"
                    "- Bảo quản và truyền đạt thông tin di truyền qua các thế hệ tế bào và cơ thể nhờ cơ chế "
                    "nhân đôi.\n"
                    "- Là khuôn để tổng hợp ARN (phiên mã) → protein (dịch mã)."
                ),
            },
            {
                "title": "Quy luật phân li của Mendel",
                "summary": "Thí nghiệm và ý nghĩa quy luật phân li.",
                "duration_minutes": 22,
                "content": (
                    "Mendel lai hai dòng đậu Hà Lan thuần chủng tương phản (hoa đỏ x hoa trắng), thu được:\n"
                    "- F1: 100% hoa đỏ.\n"
                    "- F2: 3 hoa đỏ : 1 hoa trắng.\n\n"
                    "Giải thích: mỗi tính trạng do một cặp nhân tố di truyền (gen) quy định, gồm 2 alen. Khi "
                    "hình thành giao tử, hai alen phân li đồng đều về các giao tử, mỗi giao tử chỉ chứa một alen.\n\n"
                    "Nội dung quy luật phân li (theo cách hiểu hiện đại): trong quá trình hình thành giao tử, "
                    "mỗi cặp alen phân li đồng đều về các giao tử.\n\n"
                    "Cơ sở tế bào học: sự phân li đồng đều của các cặp NST tương đồng trong giảm phân.\n\n"
                    "Ý nghĩa: là cơ sở cho việc dự đoán kết quả lai và giải thích biến dị di truyền."
                ),
            },
            {
                "title": "Đột biến gen",
                "summary": "Khái niệm, các dạng và hậu quả của đột biến gen.",
                "duration_minutes": 20,
                "content": (
                    "Đột biến gen là những biến đổi trong cấu trúc của gen, liên quan đến một hoặc một số "
                    "cặp nucleotit.\n\n"
                    "Các dạng đột biến điểm: mất, thêm hoặc thay thế một cặp nucleotit.\n\n"
                    "Nguyên nhân: bên trong (rối loạn quá trình sinh lí - hóa sinh) và bên ngoài (tia phóng xạ, "
                    "tia tử ngoại, hóa chất, sốc nhiệt, virut).\n\n"
                    "Cơ chế: thường do bắt cặp sai trong quá trình nhân đôi ADN hoặc tác động trực tiếp lên ADN.\n\n"
                    "Hậu quả:\n"
                    "- Đột biến có thể trung tính, có hại hoặc có lợi tùy môi trường.\n"
                    "- Cung cấp nguyên liệu sơ cấp cho tiến hóa và chọn giống.\n\n"
                    "Ý nghĩa: là nguồn biến dị di truyền chủ yếu, cơ sở cho tiến hóa và chọn lọc giống."
                ),
            },
            {
                "title": "Tiến hóa: chọn lọc tự nhiên",
                "summary": "Vai trò của chọn lọc tự nhiên theo quan niệm tiến hóa hiện đại.",
                "duration_minutes": 25,
                "content": (
                    "Theo thuyết tiến hóa tổng hợp hiện đại, chọn lọc tự nhiên là nhân tố tiến hóa có hướng, "
                    "tác động lên quần thể.\n\n"
                    "Đối tượng: là cá thể, nhưng kết quả là sự sống sót và sinh sản khác nhau của các kiểu gen "
                    "trong quần thể.\n\n"
                    "Thực chất: phân hóa khả năng sinh sản (giá trị thích nghi) của các kiểu gen khác nhau "
                    "trong quần thể.\n\n"
                    "Vai trò:\n"
                    "- Là nhân tố quy định chiều hướng và nhịp điệu tiến hóa.\n"
                    "- Làm thay đổi tần số alen và thành phần kiểu gen của quần thể theo hướng thích nghi.\n\n"
                    "Các hình thức chọn lọc: ổn định, vận động và phân hóa - mỗi hình thức tương ứng với một "
                    "kiểu môi trường nhất định."
                ),
            },
        ],
    },
]


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_email = "admin@elearning.app"
        if not db.query(User).filter(User.email == admin_email).first():
            admin = User(
                email=admin_email,
                full_name="Administrator",
                hashed_password=hash_password("Admin@123"),
                is_admin=True,
            )
            db.add(admin)
        demo_email = "student@elearning.app"
        if not db.query(User).filter(User.email == demo_email).first():
            demo = User(
                email=demo_email,
                full_name="Học sinh demo",
                hashed_password=hash_password("Student@123"),
            )
            db.add(demo)
        db.commit()

        for data in SUBJECTS:
            subject = db.query(Subject).filter(Subject.slug == data["slug"]).first()
            if subject:
                continue
            subject = Subject(
                name=data["name"],
                slug=data["slug"],
                description=data["description"],
                icon=data["icon"],
                color=data["color"],
                grade_level=data["grade_level"],
            )
            db.add(subject)
            db.flush()
            for idx, lesson in enumerate(data["lessons"]):
                db.add(
                    Lesson(
                        subject_id=subject.id,
                        title=lesson["title"],
                        summary=lesson["summary"],
                        content=lesson["content"],
                        duration_minutes=lesson["duration_minutes"],
                        order_index=idx,
                    )
                )
        db.commit()
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
