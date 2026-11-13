# Phạm vi bảo mật của demo

Demo phục vụ kiểm tra bài lab trên máy local. Máy chủ chỉ bind `127.0.0.1`, không có chức năng đăng nhập, upload, chạy shell hoặc chỉnh file qua HTTP.

Các biện pháp đã triển khai:

- Danh sách route tĩnh cố định, không dùng directory listing hoặc chuyển đường dẫn người dùng thành đường dẫn file. `.env`, `.git`, source và database không được phục vụ qua HTTP.
- Kiểm tra Host và Origin để hạn chế DNS rebinding và yêu cầu từ trang khác. POST cần JSON và cùng origin; không bật CORS.
- Giới hạn body 4 KB, câu hỏi 500 ký tự, allowlist section, một truy vấn live tại một thời điểm và tối thiểu 5 giây giữa hai truy vấn. Kết nối và provider có timeout/retry hữu hạn.
- API key chỉ được đọc từ môi trường hoặc hai file `.env` trong project. Trình duyệt không nhận key. Lỗi provider không trả raw exception, URL hoặc nội dung query vào log/response.
- Text của tài liệu được render bằng DOM/textContent, không chèn HTML từ corpus. CSP, nosniff, frame-ancestors và no-store được đặt ở response.
- Input chunk/vector được kiểm tra trước khi ghi; chỉ dọn chunk cũ sau khi upsert mới thành công. Vector NaN/Infinity, kích thước chia chunk không hợp lệ và ID trùng bị từ chối.
- Gói nộp dùng allowlist file, chặn symlink trỏ ngoài repo và quét mẫu token phổ biến trước khi tạo ZIP. Kết quả quét không thay thế việc tự kiểm tra dữ liệu nhạy cảm.

Kiểm thử tự động nằm trong `scripts/test_demo.py` và `scripts/test_pipeline_safety.py`; kiểm tra browser nằm trong `scripts/test_demo_ui.py`. Những kiểm tra này bao phủ các trường hợp đã nêu, không chứng minh mọi dependency hoặc mọi hình thức tấn công đều an toàn.

Chưa thực hiện quét CVE toàn bộ cây dependency hoặc kiểm thử hạ tầng public. Nếu triển khai qua mạng cần bổ sung kiểm soát truy cập, TLS và chính sách vận hành phù hợp; cấu hình hiện tại cố ý không cho bind public.
