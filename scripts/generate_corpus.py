"""Script to generate the authentic 35-page PDF document: 'Sổ tay Sinh viên và Quy chế Đào tạo 2024-2025'
Total physical pages: 35.
Content pages: 32 (Page 3 to Page 34).
Non-content pages: 3 (Page 1: Bìa, Page 2: Lời nói đầu/Mục lục, Page 35: Phụ lục).
"""
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register fonts
font_path = "C:/Windows/Fonts/arial.ttf"
font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
font_italic_path = "C:/Windows/Fonts/ariali.ttf"

pdfmetrics.registerFont(TTFont("Arial", font_path))
pdfmetrics.registerFont(TTFont("Arial-Bold", font_bold_path))
pdfmetrics.registerFont(TTFont("Arial-Italic", font_italic_path))

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Arial-Bold",
    fontSize=20,
    leading=26,
    alignment=1, # Center
    textColor=colors.HexColor("#1A365D"),
    spaceAfter=15
)

subtitle_style = ParagraphStyle(
    "DocSubtitle",
    parent=styles["Normal"],
    fontName="Arial",
    fontSize=13,
    leading=18,
    alignment=1,
    textColor=colors.HexColor("#2B6CB0"),
    spaceAfter=25
)

chapter_style = ParagraphStyle(
    "ChapterTitle",
    parent=styles["Normal"],
    fontName="Arial-Bold",
    fontSize=14,
    leading=19,
    textColor=colors.HexColor("#1E3A8A"),
    spaceAfter=10,
    spaceBefore=5
)

article_style = ParagraphStyle(
    "ArticleTitle",
    parent=styles["Normal"],
    fontName="Arial-Bold",
    fontSize=11,
    leading=16,
    textColor=colors.HexColor("#1E293B"),
    spaceAfter=6,
    spaceBefore=4
)

body_style = ParagraphStyle(
    "BodyTextCustom",
    parent=styles["Normal"],
    fontName="Arial",
    fontSize=9.5,
    leading=14.5,
    textColor=colors.HexColor("#334155"),
    alignment=4, # Justify
    spaceAfter=6
)

callout_style = ParagraphStyle(
    "CalloutText",
    parent=styles["Normal"],
    fontName="Arial-Italic",
    fontSize=9,
    leading=13.5,
    textColor=colors.HexColor("#475569"),
    spaceAfter=6
)

# Define 35 pages content
pages_content = []

# Trang 1: Trang bìa
pages_content.append({
    "type": "cover",
    "section": "bia",
    "title": "BỘ GIÁO DỤC VÀ ĐÀO TẠO — QUY CHUẨN HỌC VỤ ĐÀO TẠO ĐẠI HỌC",
    "elements": [
        Spacer(1, 100),
        Paragraph("BỘ GIÁO DỤC VÀ ĐÀO TẠO<br/><b>HỆ THỐNG VĂN BẢN QUY PHẠM PHÁP LUẬT ĐÀO TẠO ĐẠI HỌC</b>", subtitle_style),
        Spacer(1, 30),
        Paragraph("TÀI LIỆU QUY CHẾ ĐÀO TẠO VÀ CÔNG TÁC SINH VIÊN ĐẠI HỌC", title_style),
        Paragraph("Tập hợp chuẩn hóa phục vụ kiểm thử kỹ thuật Data Ingestion & Retrieval", subtitle_style),
        Spacer(1, 100),
        Paragraph("<b>Biên soạn và kết xuất:</b> Lê Song Thảo (MSSV: 2A202603534)<br/><b>Căn cứ pháp lý:</b> TT 08/2021/TT-BGDĐT, TT 10/2016/TT-BGDĐT, NĐ 81/2021/NĐ-CP, QĐ 157/2007/QĐ-TTg<br/><b>Giấy phép:</b> Creative Commons Attribution 4.0 International (CC-BY 4.0)<br/><b>Hà Nội — Tháng 11/2026</b>", subtitle_style)
    ]
})

# Trang 2: Lời nói đầu và Mục lục
pages_content.append({
    "type": "toc",
    "section": "muc_luc",
    "title": "LỜI NÓI ĐẦU VÀ MỤC LỤC TỔNG QUAN",
    "elements": [
        Paragraph("LỜI NÓI ĐẦU", chapter_style),
        Paragraph("Chào mừng các tân sinh viên và toàn thể sinh viên đến với năm học mới 2024 - 2025. Sổ tay sinh viên là cẩm nang pháp lý và hướng dẫn thiết yếu cung cấp đầy đủ thông tin về quy chế đào tạo đại học theo học chế tín chỉ, các quyền lợi và nghĩa vụ của người học, quy định học phí - học bổng, chính sách hỗ trợ sinh viên và chuẩn đầu ra tốt nghiệp.", body_style),
        Spacer(1, 10),
        Paragraph("MỤC LỤC TỔNG QUÁT", chapter_style),
        Paragraph("• <b>Chương I: Quy chế Đào tạo theo Hệ thống Tín chỉ (Trang 3 - Trang 10)</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;- Thời gian đào tạo, kế hoạch học tập, đăng ký học phần, đánh giá điểm, thang điểm và cảnh báo học vụ.<br/>• <b>Chương II: Chính sách Học phí, Miễn giảm và Học bổng (Trang 11 - Trang 18)</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;- Đơn giá tín chỉ, hạn nộp, gia hạn, miễn giảm học phí đối tượng chính sách, học bổng khuyến khích và tài trợ doanh nghiệp.<br/>• <b>Chương III: Công tác Sinh viên, Đánh giá Rèn luyện và Ký túc xá (Trang 19 - Trang 26)</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;- Quyền và nghĩa vụ người học, 5 tiêu chí điểm rèn luyện, bảo hiểm y tế bắt buộc, quy chế nội trú KTX.<br/>• <b>Chương IV: Chuẩn đầu ra, Xét tốt nghiệp, Khen thưởng và Kỷ luật (Trang 27 - Trang 34)</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;- Điều kiện tốt nghiệp, chuẩn TOEIC/IELTS, chứng chỉ MOS, hạ bậc tốt nghiệp, khen thưởng và khung xử lý kỷ luật.<br/>• <b>Phụ lục: Danh mục văn bản quy phạm pháp luật tham chiếu (Trang 35)</b>", body_style),
        Spacer(1, 15),
        Paragraph("<i>Ghi chú: Sinh viên có trách nhiệm đọc kỹ và thực hiện đúng các quy định trong sổ tay này.</i>", callout_style)
    ]
})

# CHƯƠNG I: QUY CHẾ ĐÀO TẠO THEO HỆ THỐNG TÍN CHỈ (Trang 3 - Trang 10)
pages_content.append({
    "page": 3,
    "section": "quy_che_dao_tao",
    "title": "CHƯƠNG I: QUY CHẾ ĐÀO TẠO TÍN CHỈ - THỜI GIAN VÀ KẾ HOẠCH ĐÀO TẠO",
    "elements": [
        Paragraph("CHƯƠNG I: QUY CHẾ ĐÀO TẠO THEO HỆ THỐNG TÍN CHỈ", chapter_style),
        Paragraph("Điều 1. Phạm vi điều chỉnh và đối tượng áp dụng", article_style),
        Paragraph("1. Quy chế này quy định về tổ chức đào tạo đại học chính quy theo hệ thống tín chỉ, bao gồm: thời gian và kế hoạch đào tạo; đăng ký học tập; đánh giá kết quả học tập; cảnh báo học vụ, thôi học; xét và công nhận tốt nghiệp đại học tại Trường Đại học Công nghệ và Kỹ thuật.", body_style),
        Paragraph("2. Quy chế áp dụng thống nhất đối với toàn thể sinh viên đang theo học các chương trình đào tạo đại học chính quy trình độ đại học (bao gồm chương trình chuẩn và chương trình chất lượng cao). Các chương trình liên kết quốc tế áp dụng theo đề án đã được phê duyệt riêng.", body_style),
        Paragraph("Điều 2. Thời gian đào tạo và kế hoạch năm học", article_style),
        Paragraph("1. Thời gian đào tạo tiêu chuẩn theo thiết kế chương trình được quy định như sau: Đối với khối ngành Kỹ thuật - Công nghệ là 4,0 năm (tương đương 8 học kỳ chính); đối với khối ngành Kinh tế, Quản lý và Ngôn ngữ là 3,5 năm đến 4,0 năm.", body_style),
        Paragraph("2. Thời gian tối đa để sinh viên hoàn thành khóa học được phép kéo dài không quá 2 lần so với thời gian đào tạo tiêu chuẩn. Cụ thể: Khối ngành Kỹ thuật - Công nghệ có thời gian đào tạo tối đa là 8,0 năm (16 học kỳ chính); khối ngành Kinh tế và Quản lý có thời gian đào tạo tối đa là 7,0 năm (14 học kỳ chính). Sinh viên vượt quá thời gian tối đa sẽ bị buộc thôi học theo quy định tại Điều 11.", body_style),
        Paragraph("3. Kế hoạch năm học gồm 2 học kỳ chính (Học kỳ I bắt đầu từ tháng 9 đến tháng 1; Học kỳ II bắt đầu từ tháng 2 đến tháng 6) và 1 học kỳ phụ (học kỳ hè, tổ chức tự chọn trong tháng 7 và tháng 8). Mỗi học kỳ chính kéo dài tối thiểu 15 tuần học tập và 3 tuần thi kết thúc học phần.", body_style)
    ]
})

pages_content.append({
    "page": 4,
    "section": "quy_che_dao_tao",
    "title": "CHƯƠNG I: ĐỊNH NGHĨA TÍN CHỈ VÀ QUY ĐỊNH ĐĂNG KÝ HỌC PHẦN",
    "elements": [
        Paragraph("Điều 3. Đơn vị đo lường học tập và tổ chức lớp học phần", article_style),
        Paragraph("1. Tín chỉ (TC) là đơn vị dùng để lượng hóa khối lượng kiến thức, kỹ năng của người học. Một tín chỉ được tính tương đương với: 15 tiết giảng lý thuyết trên lớp kết hợp với 30 giờ tự học, tự nghiên cứu của sinh viên; hoặc 30 đến 45 tiết thực hành, thí nghiệm, thảo luận tại phòng máy; hoặc 45 đến 90 giờ thực tập tại cơ sở, doanh nghiệp, làm đồ án môn học hoặc khóa luận tốt nghiệp.", body_style),
        Paragraph("2. Một tiết học lý thuyết hoặc thực hành có thời lượng 50 phút. Một học kỳ chính sinh viên tích lũy trung bình từ 15 đến 18 tín chỉ để đảm bảo tiến độ ra trường đúng hạn.", body_style),
        Paragraph("Điều 4. Quy định về số lượng tín chỉ đăng ký trong học kỳ chính", article_style),
        Paragraph("1. Sinh viên có học lực bình thường (GPA tích lũy đạt từ 2.00 trở lên) phải đăng ký tối thiểu 14 tín chỉ và tối đa 24 tín chỉ trong mỗi học kỳ chính, trừ học kỳ cuối của khóa học khi sinh viên chỉ làm đồ án tốt nghiệp hoặc khóa luận tốt nghiệp.", body_style),
        Paragraph("2. Đối với sinh viên có học lực xếp loại Yếu hoặc đang trong diện bị cảnh báo kết quả học tập (cảnh báo học vụ): Số tín chỉ đăng ký tối thiểu trong học kỳ chính là 10 tín chỉ và tối đa không được vượt quá 14 tín chỉ. Quy định này nhằm giúp sinh viên tập trung cải thiện kết quả học tập và tránh bị quá tải kiến thức.", body_style),
        Paragraph("3. Sinh viên có điểm trung bình chung tích lũy (GPA) từ 3.20 trở lên (xếp loại Giỏi và Xuất sắc) được phép nộp đơn xin đăng ký vượt mức tối đa, nhưng không vượt quá 28 tín chỉ trong một học kỳ chính với sự chấp thuận của Cố vấn học tập và Trưởng Khoa quản lý chuyên môn.", body_style)
    ]
})

pages_content.append({
    "page": 5,
    "section": "quy_che_dao_tao",
    "title": "CHƯƠNG I: HỌC KỲ PHỤ, HỦY VÀ RÚT BỚT HỌC PHẦN",
    "elements": [
        Paragraph("Điều 5. Đăng ký học tập trong học kỳ phụ (Học kỳ hè)", article_style),
        Paragraph("1. Học kỳ phụ được tổ chức trên tinh thần tự nguyện của người học nhằm mục đích học trả nợ các môn chưa đạt (điểm F), học cải thiện điểm số (điểm D, D+) hoặc học vượt tiến độ chương trình đào tạo.", body_style),
        Paragraph("2. Số lượng tín chỉ tối đa sinh viên được phép đăng ký trong học kỳ phụ không vượt quá 8 tín chỉ. Nhà trường không áp đặt số tín chỉ tối thiểu đối với học kỳ phụ.", body_style),
        Paragraph("3. Các học phần trong học kỳ phụ được tổ chức học dồn với tiến độ gấp đôi học kỳ chính. Sinh viên cần cân nhắc kỹ thời gian biểu và khối lượng bài tập trước khi thực hiện đăng ký.", body_style),
        Paragraph("Điều 6. Thủ tục hủy học phần và rút bớt học phần đã đăng ký", article_style),
        Paragraph("1. Hủy học phần trong thời gian điều chỉnh: Trong vòng 2 tuần đầu tiên của học kỳ chính và 1 tuần đầu của học kỳ phụ, sinh viên được quyền thêm, bớt hoặc hủy học phần trực tuyến trên cổng đào tạo mà không bị ghi điểm và không phải nộp học phí cho học phần đã hủy.", body_style),
        Paragraph("2. Rút bớt học phần (Withdrawal): Từ tuần thứ 3 đến hết tuần thứ 4 của học kỳ chính, sinh viên được phép nộp đơn xin rút bớt học phần. Sau khi được chấp thuận, học phần xin rút sẽ nhận điểm chữ W (Withdrawn) trên bảng điểm. Điểm W hoàn toàn không tính vào điểm trung bình học kỳ hay điểm trung bình tích lũy.", body_style),
        Paragraph("3. Nghĩa vụ tài chính đối với học phần rút: Sinh viên rút học phần sau tuần thứ 2 vẫn phải đóng 100% học phí của học phần đó. Sinh viên không được phép rút học phần nếu số tín chỉ còn lại sau khi rút ít hơn mức tối thiểu (14 tín chỉ đối với sinh viên bình thường, 10 tín chỉ đối với sinh viên bị cảnh báo).", body_style)
    ]
})

pages_content.append({
    "page": 6,
    "section": "quy_che_dao_tao",
    "title": "CHƯƠNG I: QUY ĐỊNH HỌC LẠI, HỌC CẢI THIỆN VÀ HỌC VƯỢT",
    "elements": [
        Paragraph("Điều 7. Quy định về học lại và học cải thiện điểm số", article_style),
        Paragraph("1. Học lại bắt buộc: Sinh viên có học phần bắt buộc bị điểm F (dưới 4.0 theo thang điểm 10) bắt buộc phải đăng ký học lại học phần đó ở các học kỳ tiếp theo cho đến khi đạt điểm D trở lên. Đối với học phần tự chọn bị điểm F, sinh viên có thể đăng ký học lại chính môn đó hoặc chọn học phần tự chọn khác tương đương trong cùng nhóm kiến thức.", body_style),
        Paragraph("2. Học cải thiện điểm: Sinh viên đạt điểm D hoặc D+ ở bất kỳ học phần nào được quyền đăng ký học cải thiện để nâng cao điểm trung bình chung tích lũy. Khi học cải thiện, điểm học phần mới nhất (nếu cao hơn) sẽ được thay thế điểm cũ trong việc tính GPA tích lũy. Trường hợp điểm học cải thiện thấp hơn điểm cũ, hệ thống đào tạo sẽ tự động giữ lại điểm cao nhất cho sinh viên.", body_style),
        Paragraph("3. Sinh viên đã đạt từ điểm C trở lên không được phép đăng ký học cải thiện đối với học phần đó, nhằm đảm bảo sự công bằng và dành chỉ tiêu lớp học phần cho các sinh viên học lần đầu.", body_style),
        Paragraph("4. Học vượt tiến độ: Sinh viên có GPA tích lũy từ 2.80 trở lên, không bị kỷ luật và hoàn thành đầy đủ học phần tiên quyết được phép đăng ký học vượt các môn của các kỳ sau. Việc học vượt có thể giúp sinh viên tốt nghiệp sớm từ 0.5 đến 1 năm so với thiết kế chuẩn.", body_style),
        Paragraph("5. Học phí học lại và học cải thiện: Tính bằng 100% mức học phí hiện hành của tín chỉ học phần đó tại thời điểm đăng ký.", body_style)
    ]
})

pages_content.append({
    "page": 7,
    "section": "quy_che_dao_tao",
    "title": "CHƯƠNG I: CƠ CẤU ĐÁNH GIÁ ĐIỂM HỌC PHẦN VÀ ĐIỀU KIỆN DỰ THI",
    "elements": [
        Paragraph("Điều 8. Cơ cấu đánh giá điểm học phần và điều kiện dự thi cuối kỳ", article_style),
        Paragraph("1. Điểm tổng kết học phần (thang điểm 10) được cấu thành từ 3 cột điểm thành phần với tỷ trọng cụ thể như sau:<br/>- Điểm đánh giá chuyên cần và thái độ học tập: Trọng số 10%.<br/>- Điểm kiểm tra định kỳ giữa kỳ (hoặc bài tập lớn, thí nghiệm, thuyết trình): Trọng số 30%.<br/>- Điểm thi kết thúc học phần (thi cuối kỳ): Trọng số 60%.<br/>Riêng các học phần đồ án chuyên ngành, thực tập tốt nghiệp và kiến tập cơ sở áp dụng đề cương chi tiết môn học với tỷ trọng đánh giá do Bộ môn quy định.", body_style),
        Paragraph("2. Điều kiện cấm thi kết thúc học phần: Sinh viên vắng mặt quá 20% tổng số tiết học quy định trên lớp của học phần (tương đương nghỉ quá 3 buổi đối với môn 3 tín chỉ lý thuyết) mà không có lý do chính đáng sẽ bị cấm thi kết thúc học phần. Khi bị cấm thi, điểm thi kết thúc học phần nhận điểm 0 và điểm tổng kết học phần sẽ bị điểm F.", body_style),
        Paragraph("3. Điểm liệt và điều kiện qua môn: Điểm thi kết thúc học phần dưới 3.0 điểm theo thang điểm 10 được coi là điểm liệt. Mọi trường hợp bị điểm liệt cuối kỳ đều dẫn đến điểm học phần xếp loại F, bất kể điểm chuyên cần và giữa kỳ đạt mức nào.", body_style),
        Paragraph("4. Hoãn thi có lý do: Sinh viên ốm đau, tai nạn hoặc lý do bất khả kháng có xác nhận của bệnh viện cấp quận/huyện trở lên phải nộp đơn xin hoãn thi về Phòng Đào tạo trong vòng 3 ngày làm việc kể từ ngày thi để được bố trí thi bổ sung ở đợt thi gần nhất.", body_style)
    ]
})

pages_content.append({
    "page": 8,
    "section": "quy_che_dao_tao",
    "title": "CHƯƠNG I: BẢNG QUY ĐỔI THANG ĐIỂM VÀ ĐIỂM CHỮ",
    "elements": [
        Paragraph("Điều 9. Thang điểm đánh giá và bảng quy đổi thang điểm chuẩn", article_style),
        Paragraph("1. Điểm đánh giá bộ phận và điểm thi kết thúc học phần được chấm theo thang điểm 10 (từ 0,0 đến 10,0, làm tròn đến một chữ số thập phân). Điểm tổng kết học phần sau đó được quy đổi sang điểm chữ và thang điểm 4 theo bảng chuẩn thống nhất toàn trường:", body_style),
        Paragraph("• <b>Điểm A</b>: Từ 8.5 đến 10.0 điểm thang 10; quy đổi sang thang 4 đạt <b>4.0 điểm</b>; Xếp loại Giỏi/Xuất sắc.<br/>• <b>Điểm B+</b>: Từ 8.0 đến 8.4 điểm thang 10; quy đổi sang thang 4 đạt <b>3.5 điểm</b>; Xếp loại Khá giỏi.<br/>• <b>Điểm B</b>: Từ 7.0 đến 7.9 điểm thang 10; quy đổi sang thang 4 đạt <b>3.0 điểm</b>; Xếp loại Khá.<br/>• <b>Điểm C+</b>: Từ 6.5 đến 6.9 điểm thang 10; quy đổi sang thang 4 đạt <b>2.5 điểm</b>; Xếp loại Trung bình khá.<br/>• <b>Điểm C</b>: Từ 5.5 đến 6.4 điểm thang 10; quy đổi sang thang 4 đạt <b>2.0 điểm</b>; Xếp loại Trung bình.<br/>• <b>Điểm D+</b>: Từ 5.0 đến 5.4 điểm thang 10; quy đổi sang thang 4 đạt <b>1.5 điểm</b>; Xếp loại Trung bình yếu.<br/>• <b>Điểm D</b>: Từ 4.0 đến 4.9 điểm thang 10; quy đổi sang thang 4 đạt <b>1.0 điểm</b>; Xếp loại Yếu (mức đạt tối thiểu để tích lũy tín chỉ).<br/>• <b>Điểm F</b>: Dưới 4.0 điểm thang 10; quy đổi sang thang 4 đạt <b>0.0 điểm</b>; Xếp loại Kém (không đạt, không được tính tích lũy tín chỉ và bắt buộc học lại).", body_style),
        Paragraph("2. Các điểm chữ đặc biệt không tính vào điểm trung bình: Điểm I (chưa hoàn thành học phần do hoãn thi); Điểm X (chưa nhận được kết quả thi từ bộ môn); Điểm W (rút học phần hợp lệ).", body_style)
    ]
})

pages_content.append({
    "page": 9,
    "section": "quy_che_dao_tao",
    "title": "CHƯƠNG I: XẾP LOẠI HỌC LỰC VÀ ĐIỂM TRUNG BÌNH TÍCH LŨY",
    "elements": [
        Paragraph("Điều 10. Phân loại kết quả học tập theo điểm trung bình chung (GPA)", article_style),
        Paragraph("1. Để đánh giá kết quả học tập của sinh viên sau mỗi học kỳ và toàn khóa học, nhà trường sử dụng 2 chỉ số điểm trung bình tính theo thang 4:<br/>- Điểm trung bình chung học kỳ (Semester GPA): Tính dựa trên các học phần sinh viên đăng ký học trong học kỳ đó.<br/>- Điểm trung bình chung tích lũy (Cumulative GPA): Tính dựa trên toàn bộ các học phần đã tích lũy (đạt điểm từ D trở lên) tính từ đầu khóa học cho đến thời điểm xét.", body_style),
        Paragraph("2. Khung xếp loại học lực học kỳ và tích lũy được phân định chính xác như sau:<br/>• <b>Loại Xuất sắc</b>: Điểm GPA đạt từ <b>3.60 đến 4.00</b>.<br/>• <b>Loại Giỏi</b>: Điểm GPA đạt từ <b>3.20 đến 3.59</b>.<br/>• <b>Loại Khá</b>: Điểm GPA đạt từ <b>2.50 đến 3.19</b>.<br/>• <b>Loại Trung bình</b>: Điểm GPA đạt từ <b>2.00 đến 2.49</b>.<br/>• <b>Loại Yếu</b>: Điểm GPA đạt từ <b>1.00 đến 1.99</b>.<br/>• <b>Loại Kém</b>: Điểm GPA đạt <b>dưới 1.00</b>.", body_style),
        Paragraph("3. Kết quả xếp loại học lực là căn cứ pháp lý trực tiếp để: Xét cấp học bổng khuyến khích học tập; xét phân loại học vụ; cho phép đăng ký số lượng tín chỉ kỳ sau; và xét khen thưởng sinh viên cuối năm học.", body_style)
    ]
})

pages_content.append({
    "page": 10,
    "section": "quy_che_dao_tao",
    "title": "CHƯƠNG I: QUY CHẾ CẢNH BÁO HỌC VỤ VÀ BUỘC THÔI HỌC",
    "elements": [
        Paragraph("Điều 11. Xử lý học vụ, cảnh báo kết quả học tập và buộc thôi học", article_style),
        Paragraph("1. Cảnh báo kết quả học tập (Cảnh báo học vụ): Được thực hiện sau mỗi học kỳ chính nhằm giúp sinh viên nhận thức được nguy cơ và kịp thời điều chỉnh kế hoạch học tập. Sinh viên bị cảnh báo học vụ nếu rơi vào một trong các trường hợp sau:<br/>- Trường hợp 1: Điểm GPA học kỳ đạt dưới 1.00 đối với học kỳ đầu tiên của khóa học; đạt dưới 1.20 đối với các học kỳ tiếp theo.<br/>- Trường hợp 2: Điểm GPA tích lũy đạt dưới 1.20 đối với sinh viên năm thứ nhất; dưới 1.40 đối với sinh viên năm thứ hai; dưới 1.60 đối với sinh viên năm thứ ba; hoặc dưới 1.80 đối với các năm tiếp theo cho đến cuối khóa.<br/>- Trường hợp 3: Tổng số tín chỉ bị điểm F chưa tích lũy tính từ đầu khóa học vượt quá 24 tín chỉ.", body_style),
        Paragraph("2. Các mức cảnh báo học vụ: Mức 1 (cảnh báo lần đầu); Mức 2 (bị cảnh báo tiếp tục ở học kỳ ngay sau).", body_style),
        Paragraph("3. Điều kiện buộc thôi học do học vụ: Sinh viên bị buộc thôi học nếu thuộc một trong các diện sau:<br/>- Bị cảnh báo học vụ mức 2 liên tiếp 3 học kỳ chính.<br/>- Tổng số lần bị cảnh báo học vụ trong toàn khóa học vượt quá 4 lần.<br/>- Hết thời gian đào tạo tối đa theo quy định tại Điều 2 (vượt quá 8 năm đối với khối Kỹ thuật hoặc 7 năm đối với khối Kinh tế) mà chưa đủ điều kiện công nhận tốt nghiệp.<br/>Quyết định buộc thôi học do Hiệu trưởng ký ban hành và gửi thông báo chính thức về địa chỉ gia đình sinh viên.", body_style)
    ]
})

# CHƯƠNG II: CHÍNH SÁCH HỌC PHÍ, MIỄN GIẢM VÀ HỌC BỔNG (Trang 11 - Trang 18)
pages_content.append({
    "page": 11,
    "section": "hoc_bong_hoc_phi",
    "title": "CHƯƠNG II: ĐỊNH MỨC THU HỌC PHÍ VÀ CÁCH TÍNH TIỀN TÍN CHỈ",
    "elements": [
        Paragraph("CHƯƠNG II: CHÍNH SÁCH HỌC PHÍ, MIỄN GIẢM VÀ HỌC BỔNG", chapter_style),
        Paragraph("Điều 12. Định mức thu học phí theo học chế tín chỉ năm học 2024 - 2025", article_style),
        Paragraph("1. Học phí thu theo số lượng tín chỉ thực tế mà sinh viên đăng ký trong từng học kỳ. Đơn giá thu trên một tín chỉ được phê duyệt cho năm học 2024 - 2025 theo từng khối chương trình đào tạo như sau:<br/>• <b>Chương trình chuẩn (Khối Kỹ thuật - Công nghệ)</b>: 450.000 VNĐ / 01 tín chỉ lý thuyết; 550.000 VNĐ / 01 tín chỉ thực hành, thí nghiệm, đồ án môn học.<br/>• <b>Chương trình chuẩn (Khối ngành Kinh tế, Quản trị, Ngôn ngữ)</b>: 420.000 VNĐ / 01 tín chỉ lý thuyết; 480.000 VNĐ / 01 tín chỉ thực hành, thảo luận chuyên sâu.<br/>• <b>Chương trình Chất lượng cao (CLC giảng dạy bằng tiếng Anh)</b>: 850.000 VNĐ / 01 tín chỉ cho toàn bộ các học phần chuyên môn.<br/>• <b>Học phần Giáo dục Quốc phòng - An ninh và Giáo dục Thể chất</b>: Mức thu cào bằng là 380.000 VNĐ / 01 tín chỉ chuẩn.", body_style),
        Paragraph("2. Học phí đồ án tốt nghiệp và khóa luận tốt nghiệp: Tính tương đương khối lượng 10 tín chỉ theo đơn giá của chương trình sinh viên đang theo học.", body_style),
        Paragraph("3. Lộ trình điều chỉnh học phí: Nhà trường cam kết mức tăng học phí cho các năm học tiếp theo không vượt quá 10%/năm theo đúng Nghị định 81/2021/NĐ-CP của Chính phủ.", body_style)
    ]
})

pages_content.append({
    "page": 12,
    "section": "hoc_bong_hoc_phi",
    "title": "CHƯƠNG II: THỜI HẠN NỘP HỌC PHÍ VÀ THỦ TỤC XIN GIA HẠN",
    "elements": [
        Paragraph("Điều 13. Thời hạn nộp học phí, quy trình gia hạn và chế tài xử lý nợ học phí", article_style),
        Paragraph("1. Thời hạn nộp học phí quy định:<br/>- Đối với học kỳ chính: Sinh viên phải hoàn thành toàn bộ học phí trước ngày cuối cùng của tuần thứ 6 kể từ ngày bắt đầu học kỳ theo khung kế hoạch đào tạo.<br/>- Đối với học kỳ hè (học kỳ phụ): Sinh viên phải nộp học phí trước khi học kỳ hè bắt đầu tối thiểu 5 ngày làm việc.", body_style),
        Paragraph("2. Hình thức nộp: Thanh toán trực tuyến qua cổng thanh toán sinh viên, chuyển khoản ngân hàng định danh tự động (Virtual Account) hoặc qua ứng dụng Viettel Money / VNPay.", body_style),
        Paragraph("3. Thủ tục xin gia hạn nộp học phí: Sinh viên có gia cảnh khó khăn đột xuất (tai nạn, thiên tai, dịch bệnh) có nguyện vọng xin gia hạn nộp học phí phải làm 'Đơn xin gia hạn nộp học phí' có xác nhận của UBND xã/phường nơi cư trú hoặc đơn vị công tác của bố mẹ. Đơn phải nộp về Phòng Công tác Sinh viên trước ngày kết thúc tuần thứ 5 của học kỳ. Thời gian gia hạn tối đa không quá 30 ngày kể từ hạn nộp cuối cùng.", body_style),
        Paragraph("4. Chế tài xử lý sinh viên nợ học phí không có phép gia hạn:<br/>- Bị xóa tên khỏi danh sách dự thi kết thúc học phần của toàn bộ các môn học trong học kỳ đó.<br/>- Bị khóa tài khoản đăng ký tín chỉ cho học kỳ tiếp theo.<br/>- Không được xét cấp học bổng và bị trừ 15 điểm rèn luyện ở tiêu chí chấp hành quy định nhà trường.", body_style)
    ]
})

pages_content.append({
    "page": 13,
    "section": "hoc_bong_hoc_phi",
    "title": "CHƯƠNG II: CHÍNH SÁCH MIỄN 100% HỌC PHÍ ĐỐI TƯỢNG CHÍNH SÁCH",
    "elements": [
        Paragraph("Điều 14. Quy định chính sách miễn 100% học phí cho đối tượng chính sách", article_style),
        Paragraph("Nhà trường thực hiện miễn 100% học phí đối với các nhóm đối tượng sinh viên sau đây căn cứ Nghị định số 81/2021/NĐ-CP của Chính phủ:<br/>1. Người có công với cách mạng và thân nhân của người có công với cách mạng: Con đẻ của liệt sĩ; con đẻ của thương binh hoặc bệnh binh có tỷ lệ suy giảm khả năng lao động từ 81% trở lên; con của người hoạt động kháng chiến bị nhiễm chất độc hóa học suy giảm khả năng lao động từ 81% trở lên.<br/>2. Sinh viên bị khuyết tật nặng hoặc đặc biệt nặng có Giấy xác nhận mức độ khuyết tật do UBND cấp xã cấp theo quy định của Luật Người khuyết tật.<br/>3. Sinh viên từ 18 đến 22 tuổi mồ côi cả cha lẫn mẹ, không có người nuôi dưỡng, thuộc diện bảo trợ xã hội theo quy định của pháp luật.<br/>4. Sinh viên là người dân tộc thiểu số rất ít người (thuộc các dân tộc: Ơ Đu, Brâu, Rơ Măm, Pu Péo, Si La, Cống, Bố Y, Cơ Lao, Mảng, Lô Lô, Chứt, Lự, Pà Thẻn, La Hủ, La Ha, Ngái) sinh sống tại vùng có điều kiện kinh tế - xã hội khó khăn hoặc đặc biệt khó khăn.<br/>5. Sinh viên người dân tộc thiểu số thuộc hộ nghèo và hộ cận nghèo theo chuẩn nghèo đa chiều quốc gia.", body_style),
        Paragraph("Hồ sơ miễn học phí gồm: Đơn đề nghị miễn học phí (theo mẫu), Bản sao công chứng giấy tờ chứng minh chế độ chính sách. Hồ sơ nộp 01 lần vào đầu khóa học tại Phòng Công tác Sinh viên.", body_style)
    ]
})

pages_content.append({
    "page": 14,
    "section": "hoc_bong_hoc_phi",
    "title": "CHƯƠNG II: CHÍNH SÁCH GIẢM 70% VÀ 50% HỌC PHÍ",
    "elements": [
        Paragraph("Điều 15. Quy định chính sách giảm 70% và 50% học phí cho sinh viên", article_style),
        Paragraph("1. Đối tượng sinh viên được giảm 70% học phí:<br/>Sinh viên theo học các ngành đào tạo nghệ thuật truyền thống và đặc thù trong danh mục quy định của Bộ Lao động - Thương binh và Xã hội; sinh viên theo học một số chuyên ngành kỹ thuật nặng nhọc, độc hại, nguy hiểm đối với giáo dục đại học theo quy định của Nhà nước.", body_style),
        Paragraph("2. Đối tượng sinh viên được giảm 50% học phí:<br/>- Sinh viên là con đẻ của cán bộ, công chức, viên chức, công nhân mà cha hoặc mẹ bị tai nạn lao động hoặc mắc bệnh nghề nghiệp đang được hưởng trợ cấp thường xuyên của Bảo hiểm Xã hội.<br/>- Sinh viên là người dân tộc thiểu số (không thuộc đối tượng dân tộc rất ít người) ở thôn/bản đặc biệt khó khăn, xã khu vực III vùng dân tộc và miền núi, xã đặc biệt khó khăn vùng bãi ngang ven biển và hải đảo theo quy định của Thủ tướng Chính phủ.", body_style),
        Paragraph("3. Quy định về việc nộp học phí và hoàn trả hỗ trợ:<br/>Sinh viên diện miễn, giảm học phí vẫn tiến hành đăng ký tín chỉ bình thường. Nhà trường sẽ thực hiện thẩm định hồ sơ và phê duyệt danh sách miễn giảm trong tháng thứ 2 của học kỳ. Số tiền được miễn giảm sẽ được khấu trừ trực tiếp vào công nợ học phí hoặc chuyển khoản chi trả hoàn tiền vào tài khoản ngân hàng của sinh viên nếu đã nộp đủ trước đó.", body_style)
    ]
})

pages_content.append({
    "page": 15,
    "section": "hoc_bong_hoc_phi",
    "title": "CHƯƠNG II: ĐIỀU KIỆN XÉT HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP",
    "elements": [
        Paragraph("Điều 16. Tiêu chuẩn và mức hưởng Học bổng Khuyến khích Học tập (HB KKHT)", article_style),
        Paragraph("1. Học bổng Khuyến khích Học tập được xét cấp theo từng học kỳ chính (không xét cho học kỳ hè) nhằm khuyến khích sinh viên có thành tích học tập và rèn luyện tốt. Quỹ học bổng được trích tối thiểu 8% từ nguồn thu học phí sinh viên hệ chính quy.", body_style),
        Paragraph("2. Điều kiện tối thiểu để được đưa vào danh sách xét học bổng:<br/>- Đăng ký và tích lũy tối thiểu 15 tín chỉ trong học kỳ chính đó (riêng sinh viên kỳ cuối đăng ký theo đúng số tín chỉ còn lại của chương trình).<br/>- Không có bất kỳ học phần nào bị điểm F hoặc phải thi lại trong học kỳ.<br/>- Điểm rèn luyện đạt từ loại Khá (từ 65 điểm trở lên).<br/>- Điểm trung bình chung học tập (GPA) đạt từ loại Khá (GPA $\ge 2.50$) trở lên.", body_style),
        Paragraph("3. Ba định mức học bổng khuyến khích học tập cụ thể:<br/>• <b>Học bổng loại Xuất sắc</b>: Dành cho sinh viên có GPA đạt từ <b>3.60 đến 4.00</b> và Điểm rèn luyện đạt loại Xuất sắc (từ 90 điểm trở lên). Mức học bổng bằng <b>120% mức học phí</b> của học kỳ đó.<br/>• <b>Học bổng loại Giỏi</b>: Dành cho sinh viên có GPA đạt từ <b>3.20 đến 3.59</b> và Điểm rèn luyện đạt loại Tốt trở lên (từ 80 điểm trở lên). Mức học bổng bằng <b>100% mức học phí</b> của học kỳ đó.<br/>• <b>Học bổng loại Khá</b>: Dành cho sinh viên có GPA đạt từ <b>2.50 đến 3.19</b> và Điểm rèn luyện đạt loại Khá trở lên (từ 65 điểm trở lên). Mức học bổng bằng <b>80% mức học phí</b> của học kỳ đó.", body_style)
    ]
})

pages_content.append({
    "page": 16,
    "section": "hoc_bong_hoc_phi",
    "title": "CHƯƠNG II: QUY TRÌNH PHÂN BỔ VÀ THỨ TỰ ƯU TIÊN HỌC BỔNG",
    "elements": [
        Paragraph("Điều 17. Quy trình xét chọn, phân bổ ngân sách và thứ tự ưu tiên học bổng", article_style),
        Paragraph("1. Nguyên tắc phân bổ học bổng: Ngân sách học bổng được phân bổ về từng Khoa/Viện đào tạo căn cứ trên tỷ lệ số lượng sinh viên chính quy đóng học phí của từng đơn vị. Trong mỗi Khoa, quỹ học bổng tiếp tục chia theo từng khóa học và chuyên ngành cụ thể.", body_style),
        Paragraph("2. Thứ tự ưu tiên khi xét tuyển:<br/>- Học bổng được xét từ loại Xuất sắc trước, sau đó đến loại Giỏi, và cuối cùng đến loại Khá cho đến khi hết chỉ tiêu ngân sách phân bổ cho ngành/khóa học.<br/>- Trong trường hợp tại mức học bổng cuối cùng, số lượng sinh viên đủ điều kiện vượt quá số suất học bổng còn lại của quỹ, thứ tự ưu tiên được quyết định như sau:<br/>+ Tiêu chí ưu tiên 1: Xét theo Điểm trung bình chung học tập (GPA) từ cao xuống thấp.<br/>+ Tiêu chí ưu tiên 2: Nếu hai sinh viên có cùng điểm GPA học kỳ, sinh viên có Điểm rèn luyện cao hơn sẽ được nhận học bổng.<br/>+ Tiêu chí ưu tiên 3: Nếu cùng điểm rèn luyện, ưu tiên sinh viên tích lũy được nhiều tín chỉ hơn trong học kỳ.<br/>+ Tiêu chí ưu tiên 4: Ưu tiên sinh viên thuộc đối tượng chính sách, gia đình có hoàn cảnh khó khăn.", body_style),
        Paragraph("3. Thời gian công bố và chi trả: Danh sách dự kiến được công bố trên website trước ngày 15 của tháng thứ 3 học kỳ tiếp theo để sinh viên phản hồi trong vòng 7 ngày làm việc trước khi Hiệu trưởng ký quyết định cấp phát.", body_style)
    ]
})

pages_content.append({
    "page": 17,
    "section": "hoc_bong_hoc_phi",
    "title": "CHƯƠNG II: HỌC BỔNG TÀI TRỢ DOANH NGHIỆP VÀ CỰU SINH VIÊN",
    "elements": [
        Paragraph("Điều 18. Các chương trình học bổng tài trợ doanh nghiệp và cựu sinh viên", article_style),
        Paragraph("Hàng năm, nhà trường tiếp nhận và quản lý nhiều quỹ học bổng tài trợ ngoài ngân sách do các tập đoàn kinh tế, doanh nghiệp đối tác và cựu sinh viên trao tặng. Sinh viên nhận học bổng tài trợ vẫn được hưởng học bổng khuyến khích của trường nếu đủ điều kiện.", body_style),
        Paragraph("Một số quỹ học bổng doanh nghiệp tiêu biểu thường niên:<br/>1. <b>Học bổng Viettel - Chắp cánh tài năng công nghệ</b>: Trị giá <b>20.000.000 VNĐ / suất</b>; cấp cho sinh viên năm 3, năm 4 các ngành CNTT, Điện tử Viễn thông có GPA $\ge 3.20$ và có bài báo khoa học hoặc giải thưởng lập trình quốc gia.<br/>2. <b>Học bổng Vingroup - Đổi mới sáng tạo khoa học công nghệ</b>: Trị giá <b>25.000.000 VNĐ / suất</b>; ưu tiên các dự án nghiên cứu AI, IoT, Robotics và xe tự hành có tính ứng dụng thực tiễn cao.<br/>3. <b>Học bổng Thắp sáng tương lai (Quỹ Cựu sinh viên)</b>: Trị giá <b>15.000.000 VNĐ / suất</b>; dành riêng cho sinh viên có hoàn cảnh đặc biệt khó khăn nhưng đạt GPA từ 2.80 trở lên.<br/>4. <b>Học bổng Samsung Talent Program (STP)</b>: Trị giá <b>54.000.000 VNĐ / năm</b> kèm cơ hội thực tập và việc làm chính thức tại Trung tâm R&D Samsung.", body_style),
        Paragraph("Quy trình nộp hồ sơ học bổng doanh nghiệp được thông báo định kỳ trên Cổng thông tin Công tác sinh viên. Hội đồng xét duyệt sẽ tổ chức phỏng vấn trực tiếp đối với các ứng viên tiềm năng.", body_style)
    ]
})

pages_content.append({
    "page": 18,
    "section": "hoc_bong_hoc_phi",
    "title": "CHƯƠNG II: CHÍNH SÁCH TÍN DỤNG VAY VỐN NGÂN HÀNG CHÍNH SÁCH",
    "elements": [
        Paragraph("Điều 19. Hỗ trợ thủ tục vay vốn tín dụng sinh viên theo Quyết định 157/2007/QĐ-TTg", article_style),
        Paragraph("1. Đối tượng được vay vốn tín dụng đào tạo:<br/>Sinh viên có hoàn cảnh khó khăn đang theo học tại trường, bao gồm: Sinh viên mồ côi cha mẹ hoặc mồ côi cha/mẹ nhưng người còn lại không có khả năng lao động; Sinh viên là thành viên của hộ gia đình thuộc diện hộ nghèo, hộ cận nghèo theo quy định của pháp luật; Sinh viên mà gia đình gặp khó khăn đột xuất về tài chính do tai nạn, bệnh tật, thiên tai, hỏa hoạn.", body_style),
        Paragraph("2. Mức vốn vay và lãi suất ưu đãi:<br/>- Căn cứ Quyết định số 05/2022/QĐ-TTg sửa đổi Quyết định 157/2007/QĐ-TTg của Thủ tướng Chính phủ, mức vay tối đa được điều chỉnh lên tới <b>4.000.000 VNĐ / tháng / sinh viên</b> (tương đương 40.000.000 VNĐ cho một năm học 10 tháng).<br/>- Lãi suất vay ưu đãi áp dụng theo quy định của Ngân hàng Chính sách xã hội (hiện hành là 0,55%/tháng, tức 6,6%/năm). Lãi nợ quá hạn được tính bằng 130% lãi suất khi vay.", body_style),
        Paragraph("3. Trách nhiệm của nhà trường và thủ tục cấp giấy xác nhận:<br/>Phòng Công tác Sinh viên có trách nhiệm cấp 'Giấy xác nhận sinh viên' trong vòng 02 ngày làm việc kể từ khi sinh viên gửi yêu cầu trực tuyến. Sinh viên mang giấy xác nhận về địa phương để hộ gia đình làm thủ tục nhận tiền giải ngân tại Phòng giao dịch Ngân hàng Chính sách xã hội quận/huyện nơi cư trú.", body_style)
    ]
})

# CHƯƠNG III: CÔNG TÁC SINH VIÊN, ĐÁNH GIÁ RÈN LUYỆN VÀ KÝ TÚC XÁ (Trang 19 - Trang 26)
pages_content.append({
    "page": 19,
    "section": "cong_tac_sinh_vien",
    "title": "CHƯƠNG III: QUYỀN LỢI CỦA SINH VIÊN ĐANG THEO HỌC",
    "elements": [
        Paragraph("CHƯƠNG III: CÔNG TÁC SINH VIÊN, ĐÁNH GIÁ RÈN LUYỆN VÀ KÝ TÚC XÁ", chapter_style),
        Paragraph("Điều 20. Quyền lợi hợp pháp của sinh viên", article_style),
        Paragraph("Sinh viên đang theo học tại Trường Đại học Công nghệ và Kỹ thuật được bảo đảm đầy đủ các quyền lợi hợp pháp sau đây theo Điều 60 Luật Giáo dục Đại học:<br/>1. Quyền học tập và nghiên cứu: Được nhà trường tôn trọng và đối xử bình đẳng; được cung cấp đầy đủ đề cương chi tiết học phần, lịch học, lịch thi; được sử dụng cơ sở vật chất, thư viện điện tử, phòng thí nghiệm, phòng máy tính, hệ thống mạng internet không dây và các thiết bị phục vụ học tập, nghiên cứu khoa học.<br/>2. Quyền đóng góp ý kiến: Được trực tiếp hoặc thông qua đại diện tập thể lớp, Đoàn Thanh niên, Hội Sinh viên tham gia đối thoại thường niên với Ban Giám hiệu nhà trường; được đóng góp ý kiến về nội dung giảng dạy, phương pháp đào tạo và công tác phục vụ đào tạo.<br/>3. Quyền tham gia hoạt động phong trào: Được tham gia các tổ chức chính trị - xã hội, các câu lạc bộ học thuật, văn hóa, thể thao, nghệ thuật theo sở thích cá nhân.<br/>4. Quyền hưởng chính sách xã hội: Được xét cấp học bổng khuyến khích học tập, học bổng tài trợ, miễn giảm học phí và vay vốn tín dụng học tập theo đúng các quy định tại Chương II sổ tay này.<br/>5. Quyền bảo lưu và chuyển trường: Được quyền xin nghỉ học tạm thời (bảo lưu) hoặc chuyển trường, chuyển ngành học nếu đáp ứng đủ các điều kiện quy định.", body_style)
    ]
})

pages_content.append({
    "page": 20,
    "section": "cong_tac_sinh_vien",
    "title": "CHƯƠNG III: NGHĨA VỤ VÀ TRÁCH NHIỆM CỦA SINH VIÊN",
    "elements": [
        Paragraph("Điều 21. Nghĩa vụ và trách nhiệm của người học", article_style),
        Paragraph("Song song với các quyền lợi được thụ hưởng, sinh viên có nghĩa vụ thực hiện nghiêm túc các quy định sau:<br/>1. Chấp hành nghiêm chỉnh chủ trương, đường lối của Đảng, chính sách và pháp luật của Nhà nước; tuân thủ Điều lệ trường đại học, Nội quy học đường và Quy chế văn hóa ứng xử của nhà trường.<br/>2. Tôn trọng giảng viên, cán bộ quản lý, viên chức và nhân viên phục vụ của nhà trường; giữ gìn tinh thần đoàn kết, giúp đỡ lẫn nhau trong học tập và rèn luyện.<br/>3. Thực hiện đầy đủ nghĩa vụ học tập: Tham gia đầy đủ các giờ học trên lớp, giờ thực hành, thí nghiệm; hoàn thành các bài tập, bài kiểm tra và đồ án theo yêu cầu của giảng viên; chấp hành nghiêm quy chế thi và kiểm tra, tuyệt đối không gian lận.<br/>4. Nghĩa vụ tài chính và bảo hiểm: Đóng học phí đúng thời hạn quy định; bắt buộc tham gia Bảo hiểm Y tế theo Luật BHYT và khám sức khỏe định kỳ do nhà trường tổ chức.<br/>5. Giữ gìn và bảo vệ tài sản công: Có trách nhiệm bảo vệ tài sản của nhà trường; sử dụng tiết kiệm điện, nước; bồi thường nếu làm hỏng hóc, mất mát trang thiết bị của phòng thí nghiệm, giảng đường.<br/>6. Đeo thẻ sinh viên: Bắt buộc phải đeo thẻ sinh viên hoặc xuất trình thẻ sinh viên điện tử (App trường) khi vào khuôn viên trường, thư viện và phòng thi.", body_style)
    ]
})

pages_content.append({
    "page": 21,
    "section": "cong_tac_sinh_vien",
    "title": "CHƯƠNG III: QUY CHẾ ĐÁNH GIÁ KẾT QUẢ ĐIỂM RÈN LUYỆN",
    "elements": [
        Paragraph("Điều 22. Khung nội dung và cơ cấu tính điểm rèn luyện (Thang điểm 100)", article_style),
        Paragraph("Điểm rèn luyện của sinh viên được đánh giá định kỳ vào cuối mỗi học kỳ chính theo thang điểm 100, chia làm 5 tiêu chí thành phần căn cứ Thông tư số 16/2015/TT-BGDĐT của Bộ GD&ĐT:<br/>• <b>Tiêu chí 1: Đánh giá về ý thức học tập (Tối đa 20 điểm)</b>: Bao gồm tính chuyên cần đi học đầy đủ, đúng giờ (8đ); ý thức tham gia câu lạc bộ học thuật, thi Olympic, NCKH (6đ); tinh thần vượt khó trong học tập (6đ).<br/>• <b>Tiêu chí 2: Đánh giá về ý thức chấp hành nội quy, quy chế (Tối đa 25 điểm)</b>: Chấp hành tốt quy chế thi cử, không vi phạm kỷ luật (10đ); nộp học phí và tham gia BHYT đúng hạn (10đ); thực hiện tốt văn hóa giảng đường và đeo thẻ sinh viên (5đ).<br/>• <b>Tiêu chí 3: Đánh giá về ý thức tham gia hoạt động chính trị, xã hội, văn thể mỹ (Tối đa 20 điểm)</b>: Tham gia các buổi sinh hoạt chính trị đầu khóa, đối thoại (8đ); tham gia chiến dịch tình nguyện Mùa hè xanh, Hiến máu nhân đạo (7đ); tham gia hội diễn văn nghệ, giải thể thao (5đ).<br/>• <b>Tiêu chí 4: Đánh giá về phẩm chất công dân và quan hệ cộng đồng (Tối đa 25 điểm)</b>: Chấp hành luật giao thông, trật tự an ninh nơi cư trú (10đ); lối sống lành mạnh, quan hệ tốt với bạn bè, giúp đỡ người có hoàn cảnh khó khăn (10đ); tham gia tuyên truyền phòng chống tệ nạn xã hội (5đ).<br/>• <b>Tiêu chí 5: Đánh giá về ý thức và kết quả tham gia phụ trách công tác tập thể (Tối đa 10 điểm)</b>: Đảm nhiệm vai trò Ban cán sự lớp, Bí thư chi đoàn, Ban chủ nhiệm CLB hoàn thành tốt nhiệm vụ (10đ).", body_style)
    ]
})

pages_content.append({
    "page": 22,
    "section": "cong_tac_sinh_vien",
    "title": "CHƯƠNG III: XẾP LOẠI RÈN LUYỆN VÀ CHẾ TÀI HẠ BẬC",
    "elements": [
        Paragraph("Điều 23. Phân loại kết quả rèn luyện và chế tài áp dụng", article_style),
        Paragraph("1. Phân loại kết quả rèn luyện theo tổng điểm đạt được:<br/>• <b>Loại Xuất sắc</b>: Tổng điểm đạt từ <b>90 đến 100 điểm</b>.<br/>• <b>Loại Tốt</b>: Tổng điểm đạt từ <b>80 đến 89 điểm</b>.<br/>• <b>Loại Khá</b>: Tổng điểm đạt từ <b>65 đến 79 điểm</b>.<br/>• <b>Loại Trung bình</b>: Tổng điểm đạt từ <b>50 đến 64 điểm</b>.<br/>• <b>Loại Yếu</b>: Tổng điểm đạt từ <b>35 đến 49 điểm</b>.<br/>• <b>Loại Kém</b>: Tổng điểm đạt <b>dưới 35 điểm</b>.", body_style),
        Paragraph("2. Quy định khống chế và hạ bậc điểm rèn luyện:<br/>- Sinh viên bị kỷ luật mức Khiển trách trong học kỳ: Điểm rèn luyện trong học kỳ đó tối đa không được vượt quá loại Khá (không quá 79 điểm), bất kể tổng điểm tự chấm đạt mức nào.<br/>- Sinh viên bị kỷ luật mức Cảnh cáo cấp trường trở lên: Điểm rèn luyện học kỳ bị khống chế tối đa không vượt quá loại Trung bình (không quá 64 điểm).<br/>- Sinh viên không tham gia Bảo hiểm Y tế bắt buộc sẽ bị trừ trực tiếp 15 điểm vào Tiêu chí 2.", body_style),
        Paragraph("3. Hậu quả học vụ đối với rèn luyện Yếu, Kém:<br/>- Sinh viên bị xếp loại rèn luyện Yếu hoặc Kém trong 2 học kỳ liên tiếp sẽ bị đưa vào diện tạm ngừng học tập 1 học kỳ chính để rèn luyện lại tư tưởng. Nếu tiếp tục bị xếp loại Kém ở học kỳ thứ 3 liên tiếp sẽ bị xem xét buộc thôi học.", body_style)
    ]
})

pages_content.append({
    "page": 23,
    "section": "cong_tac_sinh_vien",
    "title": "CHƯƠNG III: BẢO HIỂM Y TẾ BẮT BUỘC VÀ CHĂM SÓC SỨC KHỎE",
    "elements": [
        Paragraph("Điều 24. Chế độ Bảo hiểm Y tế (BHYT) bắt buộc và chăm sóc y tế ban đầu", article_style),
        Paragraph("1. Tính chất bắt buộc của Bảo hiểm Y tế:<br/>Theo quy định của Luật Bảo hiểm Y tế sửa đổi, bổ sung và Nghị định số 146/2018/NĐ-CP của Chính phủ, 100% sinh viên đang theo học tại các trường đại học thuộc nhóm đối tượng có trách nhiệm bắt buộc phải tham gia Bảo hiểm Y tế.", body_style),
        Paragraph("2. Mức đóng và cơ chế hỗ trợ tài chính:<br/>- Mức đóng BHYT của sinh viên bằng 4,5% mức lương cơ sở quy định tại thời điểm tham gia cho mỗi tháng.<br/>- Trong đó: Ngân sách Nhà nước hỗ trợ đóng 30% mức phí; Sinh viên chỉ phải tự chi trả 70% mức phí BHYT.<br/>- Mức thu thực tế cho năm học 12 tháng (từ 01/01 đến 31/12) được Phòng Kế hoạch - Tài chính thông báo đầu năm học căn cứ trên mức lương cơ sở hiện hành.", body_style),
        Paragraph("3. Quyền lợi khám chữa bệnh bằng thẻ BHYT:<br/>Sinh viên được đăng ký nơi khám chữa bệnh ban đầu tại Trạm Y tế trường hoặc các bệnh viện đa khoa tuyến quận/huyện trên địa bàn Hà Nội. Khi đi khám chữa bệnh đúng tuyến, sinh viên được quỹ BHYT chi trả 80% chi phí điều trị; trường hợp khám chữa bệnh tại tuyến xã/phường được chi trả 100% chi phí trong danh mục BHYT.", body_style),
        Paragraph("4. Miễn đóng tại trường: Sinh viên đã có thẻ BHYT theo diện thân nhân sĩ quan quân đội, công an, thân nhân người có công, hoặc hộ nghèo/cận nghèo tại địa phương phải nộp bản photo thẻ BHYT còn hạn về Trạm Y tế trường để được xác nhận miễn trừ thu phí.", body_style)
    ]
})

pages_content.append({
    "page": 24,
    "section": "cong_tac_sinh_vien",
    "title": "CHƯƠNG III: TIÊU CHUẨN VÀ ĐỐI TƯỢNG ƯU TIÊN Ở KÝ TÚC XÁ",
    "elements": [
        Paragraph("Điều 25. Tiêu chuẩn xét duyệt và thứ tự đối tượng ưu tiên ở Ký túc xá (KTX)", article_style),
        Paragraph("Do số lượng chỗ ở trong Ký túc xá có hạn so với nhu cầu, Trung tâm Quản lý Ký túc xá xét duyệt hồ sơ đăng ký nội trú căn cứ theo thứ tự 6 nhóm đối tượng ưu tiên sau đây:<br/>• <b>Ưu tiên 1</b>: Sinh viên bị khuyết tật nặng; sinh viên mồ côi cả cha lẫn mẹ không có nguồn chu cấp nuôi dưỡng.<br/>• <b>Ưu tiên 2</b>: Sinh viên là con đẻ của liệt sĩ, con thương binh, con bệnh binh, con người hoạt động kháng chiến bị nhiễm chất độc hóa học.<br/>• <b>Ưu tiên 3</b>: Sinh viên là người dân tộc thiểu số; sinh viên có hộ khẩu thường trú tại các xã vùng sâu, vùng xa, biên giới, hải đảo hoặc vùng kinh tế đặc biệt khó khăn.<br/>• <b>Ưu tiên 4</b>: Sinh viên thuộc hộ nghèo, hộ cận nghèo theo giấy chứng nhận cấp năm hiện hành của chính quyền địa phương.<br/>• <b>Ưu tiên 5</b>: Tân sinh viên khóa mới đạt giải trong kỳ thi học sinh giỏi quốc gia, hoặc đạt thủ khoa, á khoa kỳ thi tuyển sinh đại học vào trường.<br/>• <b>Ưu tiên 6</b>: Sinh viên tích cực tham gia công tác Đoàn - Hội, cán bộ Ban quản lý tự quản KTX và sinh viên năm cuối có hoàn cảnh khó khăn.", body_style),
        Paragraph("Sinh viên nộp đơn đăng ký trực tuyến trên hệ thống KTX trong vòng 10 ngày sau khi có thông báo xét tuyển. Sinh viên không thuộc đối tượng ưu tiên sẽ được bốc thăm ngẫu nhiên nếu KTX còn chỗ trống.", body_style)
    ]
})

pages_content.append({
    "page": 25,
    "section": "cong_tac_sinh_vien",
    "title": "CHƯƠNG III: NỘI QUY NỘI TRÚ VÀ AN NINH TRẬT TỰ KÝ TÚC XÁ",
    "elements": [
        Paragraph("Điều 26. Nội quy nội trú và quy định an ninh trật tự Ký túc xá", article_style),
        Paragraph("Sinh viên được duyệt ở Ký túc xá phải ký cam kết thực hiện nghiêm túc các điều khoản nội quy nội trú sau:<br/>1. Giờ giấc sinh hoạt: Ký túc xá mở cửa từ <b>05h30 sáng</b> và đóng cửa lúc <b>23h00 đêm</b> hàng ngày. Sinh viên có nhu cầu về muộn vì lý do học tập, làm thêm phải có giấy xác nhận và báo trước cho Ban Quản lý trước 22h00.<br/>2. Tiếp khách và khách ngoài: Nghiêm cấm đưa người ngoài (kể cả bạn bè, người thân) vào phòng ngủ của KTX qua đêm mà không có sự đồng ý bằng văn bản của Trưởng ban Quản lý KTX. Giờ tiếp khách tại phòng sinh hoạt chung từ 08h00 đến 21h00.<br/>3. An toàn phòng cháy chữa cháy (PCCC): Nghiêm cấm nấu ăn bằng bếp gas, bếp than, bếp củi trong phòng ở; cấm tự ý câu móc, đấu nối thêm đường dây điện; chỉ được sử dụng ấm đun nước siêu tốc hoặc nồi cơm điện có công suất dưới 1000W.<br/>4. Cấm tệ nạn xã hội: Nghiêm cấm tuyệt đối hành vi tàng trữ, sử dụng chất ma túy, đánh bạc dưới mọi hình thức, uống rượu bia trong khuôn viên KTX, tàng trữ hung khí và phát tán tài liệu phản động, đồi trụy.<br/>5. Xử lý vi phạm: Sinh viên vi phạm lần 1 bị khiển trách và thông báo về khoa; vi phạm lần 2 hoặc vi phạm nghiêm trọng (đánh bạc, ma túy, nấu ăn gây cháy nổ) sẽ bị chấm dứt hợp đồng nội trú ngay lập tức và cấm lưu trú vĩnh viễn.", body_style)
    ]
})

pages_content.append({
    "page": 26,
    "section": "cong_tac_sinh_vien",
    "title": "CHƯƠNG III: NGHIÊN CỨU KHOA HỌC VÀ KHỞI NGHIỆP ĐỔI MỚI",
    "elements": [
        Paragraph("Điều 27. Hoạt động Nghiên cứu khoa học (NCKH) và Khởi nghiệp sinh viên", article_style),
        Paragraph("1. Khuyến khích hoạt động NCKH: Nhà trường luôn tạo điều kiện thuận lợi và khuyến khích sinh viên tham gia nghiên cứu khoa học ngay từ năm thứ 2 dưới sự hướng dẫn của giảng viên. Mỗi nhóm nghiên cứu có từ 2 đến 5 sinh viên.<br/>2. Định mức hỗ trợ kinh phí nghiên cứu:<br/>- Đề tài NCKH sinh viên cấp trường được xét duyệt tài trợ kinh phí thực hiện tối đa <b>15.000.000 VNĐ / đề tài</b> đối với khối ngành Kỹ thuật - Công nghệ; và tối đa <b>10.000.000 VNĐ / đề tài</b> đối với khối ngành Kinh tế - Xã hội.<br/>- Các dự án tham gia cuộc thi Khởi nghiệp Đổi mới sáng tạo (Startup Contest) lọt vào vòng Chung kết được cấp vốn ươm tạo ban đầu 20.000.000 VNĐ.<br/>3. Chế độ khen thưởng và cộng điểm cho sinh viên NCKH:<br/>- Sinh viên có đề tài đạt giải Nhất NCKH cấp trường hoặc cấp Bộ được cộng <b>10 điểm</b> vào Tiêu chí 1 điểm rèn luyện; được thưởng tiền mặt theo quy chế chi tiêu nội bộ.<br/>- Sinh viên là tác giả chính của bài báo khoa học được đăng trên tạp chí thuộc danh mục Scopus/WoS được nhà trường khen thưởng đặc biệt <b>10.000.000 VNĐ / bài báo</b> và được ưu tiên xét học bổng khuyến khích học tập loại Xuất sắc.", body_style)
    ]
})

# CHƯƠNG IV: CHUẨN ĐẦU RA, XÉT TỐT NGHIỆP, KHEN THƯỞNG VÀ KỶ LUẬT (Trang 27 - Trang 34)
pages_content.append({
    "page": 27,
    "section": "tot_nghiep_khen_thuong",
    "title": "CHƯƠNG IV: ĐIỀU KIỆN CÔNG NHẬN TỐT NGHIỆP ĐẠI HỌC",
    "elements": [
        Paragraph("CHƯƠNG IV: CHUẨN ĐẦU RA, XÉT TỐT NGHIỆP, KHEN THƯỞNG VÀ KỶ LUẬT", chapter_style),
        Paragraph("Điều 28. Điều kiện xét và công nhận tốt nghiệp đại học chính quy", article_style),
        Paragraph("Sinh viên được trường xét và công nhận tốt nghiệp khi đáp ứng đầy đủ 6 điều kiện tiên quyết sau đây theo quy chế đào tạo đại học:<br/>1. Điều kiện tích lũy học phần: Cho đến thời điểm xét tốt nghiệp, sinh viên không bị truy cứu trách nhiệm hình sự hoặc không đang trong thời gian bị kỷ luật ở mức đình chỉ học tập; đã tích lũy đủ học phần, số tín chỉ và hoàn thành các môn học bắt buộc quy định trong chương trình đào tạo của ngành học (từ 130 đến 150 tín chỉ tùy theo ngành).<br/>2. Điều kiện điểm học tập: Điểm trung bình chung tích lũy (Cumulative GPA) của toàn khóa học đạt từ <b>2.00 điểm trở lên</b> theo thang điểm 4.<br/>3. Điều kiện Giáo dục Thể chất và Quốc phòng: Đã hoàn thành và được cấp Chứng chỉ Giáo dục Thể chất và Chứng chỉ Giáo dục Quốc phòng - An ninh theo quy định của Bộ GD&ĐT.<br/>4. Điều kiện chuẩn đầu ra Ngoại ngữ: Có chứng chỉ tiếng Anh quốc tế hoặc chứng chỉ VSTEP còn hiệu lực đạt chuẩn theo quy định tại Điều 29.<br/>5. Điều kiện chuẩn đầu ra Tin học: Đạt chứng chỉ tin học quốc tế MOS hoặc IC3 theo quy định tại Điều 30.<br/>6. Nghĩa vụ tài chính và tài sản: Hoàn thành đầy đủ học phí, các khoản lệ phí và không nợ sách, tài liệu tại Thư viện trường.", body_style)
    ]
})

pages_content.append({
    "page": 28,
    "section": "tot_nghiep_khen_thuong",
    "title": "CHƯƠNG IV: CHUẨN ĐẦU RA NGOẠI NGỮ THEO NGÀNH ĐÀO TẠO",
    "elements": [
        Paragraph("Điều 29. Quy định chuẩn đầu ra Ngoại ngữ và bảng quy đổi chứng chỉ tương đương", article_style),
        Paragraph("1. Chuẩn đầu ra Ngoại ngữ áp dụng cho sinh viên các ngành không chuyên ngữ:<br/>Sinh viên thuộc các ngành Kỹ thuật, Công nghệ thông tin, Kinh tế, Quản lý bắt buộc phải nộp một trong các chứng chỉ tiếng Anh quốc tế còn thời hạn 2 năm tính đến ngày nộp hồ sơ xét tốt nghiệp:<br/>• <b>TOEIC (2 kỹ năng Nghe - Đọc)</b>: Đạt tối thiểu <b>550 điểm</b>.<br/>• <b>IELTS Academic</b>: Đạt tối thiểu <b>5.5 điểm</b> (không có kỹ năng nào dưới 5.0).<br/>• <b>TOEFL iBT</b>: Đạt tối thiểu <b>60 điểm</b>.<br/>• <b>Chứng chỉ VSTEP (Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam)</b>: Đạt tối thiểu <b>Bậc 3 (tương đương trình độ B1)</b> do các trường đại học được Bộ GD&ĐT cấp phép khảo thí cấp.", body_style),
        Paragraph("2. Chuẩn đầu ra đối với sinh viên ngành Ngôn ngữ Anh và Chương trình Chất lượng cao:<br/>- Sinh viên chuyên ngành Ngôn ngữ Anh: Bắt buộc đạt chứng chỉ <b>IELTS từ 6.5 trở lên</b> hoặc <b>VSTEP Bậc 5 (trình độ C1)</b>.<br/>- Sinh viên học Chương trình Chất lượng cao (giảng dạy bằng tiếng Anh): Bắt buộc đạt chứng chỉ <b>TOEIC tối thiểu 650 điểm</b> hoặc <b>IELTS tối thiểu 6.0 điểm</b>.", body_style),
        Paragraph("3. Thời hạn nộp chứng chỉ: Sinh viên phải nộp bản sao công chứng kèm bản gốc để đối chiếu trước đợt xét tốt nghiệp tối thiểu 30 ngày để nhà trường gửi văn bản xác minh tính hợp pháp của văn bằng tại đơn vị cấp chứng chỉ.", body_style)
    ]
})

pages_content.append({
    "page": 29,
    "section": "tot_nghiep_khen_thuong",
    "title": "CHƯƠNG IV: CHUẨN ĐẦU RA TIN HỌC ỨNG DỤNG QUỐC TẾ",
    "elements": [
        Paragraph("Điều 30. Quy định chuẩn đầu ra Tin học ứng dụng văn phòng", article_style),
        Paragraph("1. Yêu cầu chuẩn đầu ra Tin học:<br/>Toàn bộ sinh viên hệ chính quy trước khi tốt nghiệp phải đạt chuẩn kỹ năng sử dụng công nghệ thông tin quốc tế. Nhà trường công nhận 2 loại chứng chỉ tin học quốc tế sau đây:<br/>• <b>Chứng chỉ MOS (Microsoft Office Specialist)</b>: Sinh viên phải đạt tối thiểu 3 bài thi kỹ năng độc lập gồm: Word, Excel và PowerPoint (phiên bản MOS 2016, MOS 2019 hoặc MOS 365). Điểm số tối thiểu của mỗi bài thi kỹ năng phải đạt từ <b>700 / 1.000 điểm trở lên</b>.<br/>• <b>Chứng chỉ IC3 (Internet and Computing Core Certification)</b>: Phiên bản GS5 hoặc GS6, hoàn thành trọn vẹn cả 3 bài thi thành phần: Máy tính căn bản (Computing Fundamentals), Các ứng dụng chủ chốt (Key Applications), và Cuộc sống trực tuyến (Living Online).", body_style),
        Paragraph("2. Miễn trừ chuẩn đầu ra tin học: Sinh viên theo học các ngành Công nghệ Thông tin, Kỹ thuật Phần mềm, Khoa học Máy tính và Hệ thống Thông tin được tự động miễn nộp chứng chỉ tin học chuẩn đầu ra do khối lượng kiến thức chuyên ngành đã vượt xa yêu cầu chuẩn.", body_style),
        Paragraph("3. Xác thực chứng chỉ: Toàn bộ chứng chỉ tin học nộp về trường sẽ được quét mã xác thực trực tuyến trên hệ thống Certiport quốc tế nhằm ngăn chặn việc sử dụng chứng chỉ giả mạo.", body_style)
    ]
})

pages_content.append({
    "page": 30,
    "section": "tot_nghiep_khen_thuong",
    "title": "CHƯƠNG IV: XẾP LOẠI TỐT NGHIỆP VÀ QUY ĐỊNH HẠ BẬC",
    "elements": [
        Paragraph("Điều 31. Xếp loại tốt nghiệp đại học và các trường hợp bị hạ bậc tốt nghiệp", article_style),
        Paragraph("1. Khung phân loại bằng tốt nghiệp đại học căn cứ trên điểm GPA tích lũy toàn khóa:<br/>• <b>Hạng Xuất sắc</b>: Điểm trung bình chung tích lũy đạt từ <b>3.60 đến 4.00</b>.<br/>• <b>Hạng Giỏi</b>: Điểm trung bình chung tích lũy đạt từ <b>3.20 đến 3.59</b>.<br/>• <b>Hạng Khá</b>: Điểm trung bình chung tích lũy đạt từ <b>2.50 đến 3.19</b>.<br/>• <b>Hạng Trung bình</b>: Điểm trung bình chung tích lũy đạt từ <b>2.00 đến 2.49</b>.", body_style),
        Paragraph("2. Các trường hợp bị hạ một bậc xếp loại tốt nghiệp:<br/>Hạng tốt nghiệp của những sinh viên có kết quả học tập toàn khóa đạt loại Xuất sắc hoặc loại Giỏi sẽ bị <b>hạ xuống một bậc</b> (từ Xuất sắc xuống Giỏi; từ Giỏi xuống Khá) nếu thuộc một trong hai trường hợp cụ thể sau đây:<br/>- <b>Trường hợp 1 (Học lại vượt định mức)</b>: Có khối lượng tín chỉ của các học phần phải thi lại hoặc học lại vượt quá <b>5% tổng số tín chỉ</b> quy định cho toàn bộ chương trình đào tạo của ngành học (ví dụ: đối với chương trình 140 tín chỉ, nếu số tín chỉ thi lại/học lại từ 8 tín chỉ trở lên sẽ bị hạ bậc).<br/>- <b>Trường hợp 2 (Bị kỷ luật)</b>: Đã từng bị nhà trường kỷ luật từ mức <b>Cảnh cáo cấp trường trở lên</b> trong suốt thời gian học tập tại trường.", body_style),
        Paragraph("3. Bằng tốt nghiệp đại học được cấp 01 lần duy nhất kèm theo Bảng điểm tốt nghiệp toàn khóa ghi rõ điểm chữ, điểm thang 10, điểm thang 4 và xếp loại tốt nghiệp.", body_style)
    ]
})

pages_content.append({
    "page": 31,
    "section": "tot_nghiep_khen_thuong",
    "title": "CHƯƠNG IV: KẾ HOẠCH VÀ HỒ SƠ ĐĂNG KÝ XÉT TỐT NGHIỆP",
    "elements": [
        Paragraph("Điều 32. Kế hoạch thời gian và hồ sơ đăng ký xét tốt nghiệp", article_style),
        Paragraph("1. Các đợt xét tốt nghiệp trong năm học:<br/>Hàng năm nhà trường tổ chức 03 đợt xét và công nhận tốt nghiệp chính thức cho sinh viên vào các thời điểm:<br/>- <b>Đợt 1</b>: Tổ chức vào tháng 3 hàng năm (dành cho sinh viên học vượt hoặc hoàn thành muộn).<br/>- <b>Đợt 2 (Đợt chính)</b>: Tổ chức vào tháng 6 hàng năm (dành cho sinh viên tốt nghiệp đúng tiến độ).<br/>- <b>Đợt 3</b>: Tổ chức vào tháng 10 hàng năm (dành cho sinh viên hoàn thành học phần trong kỳ hè).", body_style),
        Paragraph("2. Hồ sơ đăng ký xét tốt nghiệp bao gồm:<br/>- Đơn đăng ký xét tốt nghiệp (điền trực tuyến trên Cổng thông tin đào tạo).<br/>- 02 ảnh thẻ cỡ 3x4 (chụp trang phục công sở trên nền phông trắng, ghi rõ họ tên và MSSV sau ảnh).<br/>- Bản sao có công chứng chứng chỉ Tiếng Anh (TOEIC/IELTS/VSTEP) và chứng chỉ Tin học (MOS/IC3).<br/>- Giấy xác nhận không nợ sách thư viện và biên lai hoàn tất nghĩa vụ học phí.", body_style),
        Paragraph("3. Thời hạn nộp hồ sơ: Sinh viên phải nộp hồ sơ trước ngày bắt đầu họp Hội đồng xét tốt nghiệp tối thiểu 20 ngày làm việc. Quá thời hạn trên, hồ sơ sẽ tự động chuyển sang đợt xét kế tiếp.", body_style)
    ]
})

pages_content.append({
    "page": 32,
    "section": "tot_nghiep_khen_thuong",
    "title": "CHƯƠNG IV: HÌNH THỨC VÀ TIÊU CHUẨN KHEN THƯỞNG SINH VIÊN",
    "elements": [
        Paragraph("Điều 33. Các danh hiệu và hình thức khen thưởng sinh viên", article_style),
        Paragraph("1. Khen thưởng định kỳ cuối năm học:<br/>- Danh hiệu 'Sinh viên Xuất sắc': Tặng cho sinh viên có cả điểm học tập GPA và điểm rèn luyện đạt loại Xuất sắc trong năm học. Kèm theo Giấy khen của Hiệu trưởng và tiền thưởng 1.500.000 VNĐ.<br/>- Danh hiệu 'Sinh viên Giỏi': Tặng cho sinh viên có điểm học tập đạt loại Giỏi trở lên và điểm rèn luyện đạt loại Tốt trở lên. Kèm Giấy khen và tiền thưởng 1.000.000 VNĐ.<br/>2. Khen thưởng tốt nghiệp toàn khóa:<br/>- Danh hiệu 'Thủ khoa tốt nghiệp': Tặng cho sinh viên có điểm GPA tích lũy toàn khóa cao nhất của mỗi ngành đào tạo (yêu cầu GPA tối thiểu đạt loại Giỏi và rèn luyện Tốt trở lên, không bị kỷ luật). Được Hiệu trưởng trao tặng Cúp Thủ khoa, Giấy khen và tiền thưởng 5.000.000 VNĐ.<br/>3. Khen thưởng đột xuất:<br/>Sinh viên đạt giải trong các kỳ thi học sinh giỏi, thi Olympic toàn quốc, đạt giải Hội nghị NCKH sinh viên cấp Bộ hoặc có hành động dũng cảm cứu người, nhặt được của rơi trả lại người mất được khen thưởng đột xuất với mức thưởng từ 2.000.000 đến 10.000.000 VNĐ tùy theo tính chất thành tích.", body_style)
    ]
})

pages_content.append({
    "page": 33,
    "section": "tot_nghiep_khen_thuong",
    "title": "CHƯƠNG IV: CÁC HÌNH THỨC XỬ LÝ KỶ LUẬT SINH VIÊN",
    "elements": [
        Paragraph("Điều 34. Khung các hình thức xử lý kỷ luật sinh viên vi phạm", article_style),
        Paragraph("Sinh viên vi phạm pháp luật, quy chế đào tạo, nội quy học đường tùy theo tính chất và mức độ vi phạm sẽ phải chịu một trong 4 hình thức kỷ luật sau theo Thông tư số 10/2016/TT-BGDĐT:<br/>1. <b>Hình thức Khiển trách</b>: Áp dụng đối với sinh viên có hành vi vi phạm lần đầu nhưng ở mức độ nhẹ; sinh viên đi học muộn nhiều lần; không đeo thẻ sinh viên sau khi đã bị nhắc nhở; hoặc vi phạm quy chế thi lần đầu ở mức độ nhìn bài bạn.<br/>2. <b>Hình thức Cảnh cáo cấp trường</b>: Áp dụng đối với sinh viên đã bị khiển trách mà tái phạm; sinh viên mang tài liệu trái phép hoặc điện thoại di động vào phòng thi kết thúc học phần; sinh viên đánh nhau gây mất trật tự trong khuôn viên trường.<br/>3. <b>Hình thức Đình chỉ học tập có thời hạn (01 năm học)</b>: Áp dụng đối với sinh viên đang trong thời gian bị cảnh cáo mà tái phạm; sinh viên có hành vi nhờ người khác thi hộ hoặc làm bài tập hộ lần thứ nhất; sinh viên tàng trữ, sử dụng ma túy trong trường.<br/>4. <b>Hình thức Buộc thôi học</b>: Áp dụng đối với sinh viên vi phạm một trong các lỗi đặc biệt nghiêm trọng sau:<br/>- Đi thi hộ hoặc nhờ người khác đi thi hộ lần thứ hai.<br/>- Trực tiếp đi thi hộ hoặc làm đồ án/khóa luận tốt nghiệp thuê cho người khác.<br/>- Sử dụng văn bằng, chứng chỉ ngoại ngữ hoặc tin học giả mạo trong hồ sơ xét tốt nghiệp.<br/>- Vi phạm pháp luật bị cơ quan có thẩm quyền kết án phạt tù giam.", body_style)
    ]
})

pages_content.append({
    "page": 34,
    "section": "tot_nghiep_khen_thuong",
    "title": "CHƯƠNG IV: QUY TRÌNH KỶ LUẬT VÀ QUYỀN KHIẾU NẠI",
    "elements": [
        Paragraph("Điều 35. Quy trình họp xét kỷ luật và quyền khiếu nại của người học", article_style),
        Paragraph("1. Trình tự và thủ tục xét kỷ luật:<br/>- Khi phát hiện vi phạm, đơn vị phát hiện lập biên bản vi phạm và yêu cầu sinh viên viết bản tường trình sự việc trong vòng 24 giờ.<br/>- Ban cán sự lớp và Chi đoàn tổ chức họp kiểm điểm sinh viên vi phạm, có biên bản biểu quyết đề xuất hình thức kỷ luật gửi lên Hội đồng Khen thưởng và Kỷ luật cấp Khoa.<br/>- Hội đồng Khen thưởng và Kỷ luật trường tổ chức phiên họp chính thức, mời sinh viên vi phạm tham dự để trình bày ý kiến. Trường hợp sinh viên vắng mặt không có lý do chính đáng sau 2 lần triệu tập, Hội đồng vẫn tiến hành họp và quyết định hình thức kỷ luật.<br/>- Quyết định kỷ luật do Hiệu trưởng ký ban hành, được gửi trực tiếp cho sinh viên, gửi về gia đình và lưu vĩnh viễn trong hồ sơ quản lý sinh viên.", body_style),
        Paragraph("2. Quyền khiếu nại của sinh viên:<br/>Sinh viên có quyền khiếu nại về quyết định kỷ luật lên Phòng Thanh tra - Pháp chế hoặc trực tiếp lên Hiệu trưởng trong thời hạn <b>15 ngày làm việc</b> kể từ ngày nhận được quyết định. Trong thời gian chờ giải quyết khiếu nại, sinh viên vẫn phải nghiêm túc chấp hành quyết định kỷ luật đã ban hành.", body_style)
    ]
})

# Trang 35: Phụ lục văn bản quy phạm pháp luật tham chiếu (Trang không tính nội dung chính)
pages_content.append({
    "type": "appendix",
    "section": "phu_luc",
    "title": "PHỤ LỤC: DANH MỤC CÁC VĂN BẢN QUY PHẠM PHÁP LUẬT THAM CHIẾU",
    "elements": [
        Paragraph("PHỤ LỤC: DANH MỤC VĂN BẢN QUY PHẠM THAM CHIẾU", chapter_style),
        Paragraph("Sổ tay sinh viên và Quy chế đào tạo được xây dựng căn cứ trên các văn bản quy phạm pháp luật hiện hành của Nhà nước và Bộ Giáo dục và Đào tạo, bao gồm:<br/>1. Luật Giáo dục Đại học số 08/2012/QH13 và Luật sửa đổi, bổ sung một số điều của Luật Giáo dục Đại học số 34/2018/QH14.<br/>2. Thông tư số 08/2021/TT-BGDĐT ngày 18/03/2021 của Bộ trưởng Bộ Giáo dục và Đào tạo ban hành Quy chế đào tạo trình độ đại học.<br/>3. Thông tư số 10/2016/TT-BGDĐT ngày 05/04/2016 của Bộ trưởng Bộ GD&ĐT ban hành Quy chế công tác sinh viên đối với chương trình đào tạo đại học hệ chính quy.<br/>4. Thông tư số 16/2015/TT-BGDĐT ngày 12/08/2015 của Bộ trưởng Bộ GD&ĐT ban hành Quy chế đánh giá kết quả rèn luyện của người học được đào tạo trình độ đại học hệ chính quy.<br/>5. Nghị định số 81/2021/NĐ-CP ngày 27/08/2021 của Chính phủ quy định về cơ chế thu, quản lý học phí và chính sách miễn, giảm học phí, hỗ trợ chi phí học tập.<br/>6. Quyết định số 157/2007/QĐ-TTg và Quyết định số 05/2022/QĐ-TTg của Thủ tướng Chính phủ về tín dụng đối với học sinh, sinh viên.<br/>7. Thông tư số 03/2014/TT-BTTTT ngày 11/03/2014 của Bộ Thông tin và Truyền thông quy định Chuẩn kỹ năng sử dụng công nghệ thông tin.", body_style),
        Spacer(1, 15),
        Paragraph("<i>Bản quyền tài liệu thuộc Trường Đại học Công nghệ và Kỹ thuật. Mọi hành vi sao chép không xin phép đều là vi phạm bản quyền.</i>", callout_style)
    ]
})

def draw_header_footer(canvas, doc):
    canvas.saveState()
    page_num = canvas.getPageNumber()
    canvas.setFont("Arial", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    
    # Header (trừ trang bìa)
    if page_num > 1:
        canvas.drawString(54, 800, "SỔ TAY SINH VIÊN VÀ QUY CHẾ ĐÀO TẠO ĐẠI HỌC 2024 - 2025")
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.5)
        canvas.line(54, 794, 540, 794)
    
    # Footer
    if page_num > 1:
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.5)
        canvas.line(54, 45, 540, 45)
        canvas.drawString(54, 32, "Trường Đại học Công nghệ và Kỹ thuật - Ban Đào tạo & CTSV")
        canvas.drawRightString(540, 32, f"Trang {page_num}")
    canvas.restoreState()

def build_pdf(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
        title="Tài liệu Quy chế Đào tạo và Công tác Sinh viên Đại học",
        author="Lê Song Thảo",
        subject="Corpus nghiên cứu Data Ingestion - Day 06",
        creator="ReportLab 5.1.0"
    )
    
    story = []
    for i, p in enumerate(pages_content):
        for elem in p["elements"]:
            story.append(elem)
        if i < len(pages_content) - 1:
            story.append(PageBreak())
            
    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    print(f"Successfully generated {len(pages_content)} pages to {output_path}")

if __name__ == "__main__":
    out_pdf = "data/so_tay_sinh_vien_2024.pdf"
    build_pdf(out_pdf)
