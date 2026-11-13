# Báo cáo Day 06 — Data Ingestion Engineering

**Học viên:** Lê Sông Thao · **MSSV:** 2A202603534 · **Lớp:** K5-L3A

[Repo bài nộp](https://github.com/lesongthao/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion)

## 1. Dữ liệu và cách xử lý

Corpus của bài là tài liệu về đào tạo và công tác sinh viên do học viên tự biên soạn, kết xuất bằng ReportLab. Đây là dữ liệu thực hành, không phải sổ tay do một trường đại học ban hành. Các số liệu học phí, học bổng và chuẩn đầu ra trong corpus chưa được đối chiếu từng điều với văn bản chính thức; không dùng chúng làm hướng dẫn học vụ thực tế.

Tài liệu tham khảo gồm [Thông tư 08/2021/TT-BGDĐT](https://congbao.chinhphu.vn/van-ban/thong-tu-so-08-2021-tt-bgddt-33673.htm), [Thông tư 10/2016/TT-BGDĐT](https://congbao.chinhphu.vn/van-ban/thong-tu-so-10-2016-tt-bgddt-19434/13882.htm) và các văn bản được liệt kê trong [manifest](../../data/manifest.json). Học viên khai báo giấy phép CC BY 4.0 cho phần tài liệu tự biên soạn.

PDF có 35 trang vật lý. Bài tính 32 trang nội dung, từ trang 3 đến 34; bỏ trang bìa, lời mở đầu/mục lục và phụ lục tham khảo. Sau chuẩn hóa, phần nội dung có **45.237 ký tự**. Manifest ghi danh sách trang, số ký tự, section và SHA-256 của PDF để kiểm tra đúng phiên bản dữ liệu.

Pipeline đọc PDF bằng `pypdf`, chuẩn hóa Unicode NFC, khoảng trắng và ngắt dòng rồi chia chunk theo từng trang. Mỗi chunk giữ `document_id`, `source`, `page`, `chunk_id`, `section` và `year`. Danh sách trang bỏ qua được lưu trong [skipped_pages.json](../../results/skipped_pages.json). Corpus này trích xuất được text, không dùng OCR.

Embedding dùng `models/gemini-embedding-001`, 3072 chiều, cùng cách xử lý văn bản/query giữa các cấu hình. Vector được lưu bằng ChromaDB 1.5.9 tại `results/chroma_db`, tìm kiếm cosine bằng index HNSW. Phiên bản thư viện trực tiếp được ghim trong [requirements](../../starter/requirements.txt).

Khi nạp lại một phiên bản tài liệu, ID ổn định giúp ghi đè chunk cũ. Chunk không còn xuất hiện chỉ được xóa sau khi toàn bộ dữ liệu mới được kiểm tra và ghi thành công. Backend báo lỗi khi embedding/vector không hợp lệ; không dùng vector ngẫu nhiên thay kết quả provider.

## 2. Ba cấu hình và benchmark

| Cấu hình | Chunking | Retrieval | Số chunk |
|---|---|---|---:|
| A | Cửa sổ 500 ký tự, overlap 50 | Top-3, không filter | 116 |
| B | Theo đoạn/câu, tối đa 800 ký tự; chia theo từ khi đơn vị quá dài | Top-3, không filter | 72 |
| C | Dùng đúng chunk và vector của B | Chỉ thêm filter `section` khi câu hỏi có phạm vi | 72 |

A–B thay phương pháp chunking; B–C chỉ thay bước lọc. Các giá trị section đến từ bốn chương của corpus: đào tạo (trang 3–10), học phí/học bổng (11–18), công tác sinh viên (19–26), tốt nghiệp/khen thưởng (27–34).

[Benchmark](../../benchmark/benchmark_questions.json) có 20 câu: 15 dev (`q01`–`q15`) và 5 test (`q16`–`q20`). Ba câu có filter là `q08`, `q11`, `q19`; giá trị filter được coi là phạm vi do người dùng cung cấp trước khi tìm kiếm. Query chỉ chứa câu hỏi, không chứa gold answer hay gold source.

Mỗi câu có đáp án, nguồn, trang và evidence. Với câu nhiều điều kiện như `q07`, `q20`, hàm chấm yêu cầu đủ các đoạn trong `evidence_quotes` nằm trong cùng một chunk, đồng thời khớp document và trang. Evidence được kiểm chứng trên text trích xuất sau chuẩn hóa; đây không phải phép so khớp byte của file PDF.

Split được giữ từ bản đầu. Sau khi xem kết quả, bài đã sửa chunking và gold rồi dùng lại cùng tập test. Vì vậy, **test hiện tại là kiểm tra hồi quy, không còn là holdout độc lập**. Tiêu chí lựa chọn được ghi trong bài là ưu tiên Hit@3 trên dev, sau đó coherence, tuân thủ phạm vi và tài nguyên; chưa có log riêng chứng minh thời điểm chốt tiêu chí trước lần chạy đầu.

## 3. Kết quả truy xuất và tài nguyên

| Cấu hình | Split | Hit@1 | Evidence Hit@3 | Filter tuân thủ |
|---|---|---:|---:|---:|
| A | Dev | 10/15 | 12/15 | 2/2 |
| A | Test | 3/5 | 3/5 | 1/1 |
| B | Dev | 13/15 | 15/15 | 1/2 |
| B | Test | 5/5 | 5/5 | 1/1 |
| C | Dev | 13/15 | 15/15 | 2/2 |
| C | Test | 5/5 | 5/5 | 1/1 |

Ở A/B, filter compliance chỉ đo kết quả có nằm trong phạm vi được hỏi hay không; hai cấu hình này không thực thi filter. Mọi trace lưu đủ ba chunk, text, score và metadata để đối chiếu: [A](../../results/traces_strategy_a.json), [B](../../results/traces_strategy_b.json), [C](../../results/traces_strategy_c.json).

| Cấu hình | Thời gian embedding | Thời gian ghi store | Tổng ingest theo log | Chi phí document embedding ước tính |
|---|---:|---:|---:|---:|
| A | 63.09s | 0.526s | 63.95s | 0.002117 USD |
| B | 79.74s | 0.259s | 80.34s | 0.001937 USD |
| C | Dùng lại B | 0.294s | 0.63s, khi đã có vector B | 0 USD phát sinh |

Thời gian trên thuộc lần chạy được lưu trong [summary](../../results/benchmark_summary.json), không phải số đo mới khi mở giao diện. Chưa lưu thời gian query riêng. Tổng thời gian C không đại diện cho một lần dựng C từ đầu; nếu chưa có vector B vẫn phải trả chi phí chuẩn bị tương ứng.

Token ước tính bằng số ký tự/3.5: A khoảng 14.113, B khoảng 12.913. Chi phí tham khảo tính theo Standard API **0.15 USD/1 triệu token**, kiểm tra ngày 13/11/2026 tại [bảng giá Google](https://aistudio.google.com/docs/pricing#gemini-embedding). Ước tính chưa gồm query, probe và retry. Bài từng khai báo chi phí 0 USD theo Free Tier, nhưng chưa có hóa đơn để đối chiếu; không coi ước tính thương mại là billed cost.

## 4. Coherence, metadata và grounding

| Cấu hình | Coherence /2, 10 mẫu | Metadata đúng và đủ | Grounding mức 0/1/2 | Grounding trung bình /2 |
|---|---:|---:|---|---:|
| A | 0.50 | 15/15 | 0 / 2 / 3 câu | 1.60 |
| B | 1.90 | 15/15 | 0 / 0 / 5 câu | 2.00 |
| C | Dùng cùng chunk B: 1.90 | 15/15 | 0 / 0 / 5 câu | 2.00 |

Coherence lấy mẫu tại trang 3, 5, 8, 11, 13, 16, 21, 24, 28, 30. Mỗi vị trí có đoạn neo nguồn (`source_anchor`, bắt đầu tại ký tự 450) được kiểm tra nằm trong cả chunk A và B; C dùng chung chunk B. Đoạn neo được bổ sung trong lần hoàn thiện để làm rõ vị trí so sánh, không phải bằng chứng rằng mẫu đã được chọn trước lần chạy đầu.

Metadata được kiểm tra trên 5 câu test × top-3 cho từng cấu hình: đúng document, đường dẫn nguồn, số trang, section, year và text thực sự thuộc trang đó. `page` giúp mở lại đúng PDF; `section` giúp giới hạn phạm vi. Nhược điểm là section đang gán theo khoảng trang cố định, nên phải cập nhật khi cấu trúc PDF thay đổi.

Grounding đánh giá khả năng trả lời từ **toàn bộ top-3**, không đo câu trả lời do LLM sinh. Các nhãn và lý do nằm trong [audit_report.json](../../results/audit_report.json). Học viên **Lê Sông Thao** xác nhận kết quả/bảng chấm ngày 14/11/2026. [Bản xác nhận](../../artifacts/audit_confirmation.json) ghi rõ đây là xác nhận của tác giả và được gắn với hash corpus, bảng nhãn; script không tự xác nhận cho một phiên bản dữ liệu khác.

## 5. Phân tích và lựa chọn

**A so với B.** A tạo nhiều hơn 44 chunk và làm một số evidence bị cắt qua ranh giới cửa sổ. B giảm số chunk 37.9% và đạt Hit@3 cao hơn trên bộ câu hỏi này. Tuy nhiên, B có thời gian embedding dài hơn trong lần chạy đã lưu (79.74s so với 63.09s), nên chưa thể kết luận ít chunk sẽ chạy nhanh hơn. Chưa đo dung lượng index trên đĩa.

**B so với C.** Hit@3 bằng nhau, nhưng C kiểm soát phạm vi tốt hơn. Với `q08`, B trả về trang 11, 11, 4; chunk trang 4 nói về tín chỉ, nằm ngoài chương học phí. C thay kết quả thứ ba bằng trang 15. Filter compliance trên dev tăng từ 1/2 lên 2/2, còn test vẫn là 1/1 ở cả B/C. Mức tăng này chỉ được quan sát trên ba câu có filter.

Hai trường hợp lỗi đáng chú ý:

- **`q01`, trang 3:** `p3_fix_001` kết thúc tại phần “4,0 năm (tương đươn”, còn `p3_fix_002` bắt đầu từ “ngành Kỹ thuật…”. Không chunk nào trong top-3 của A chứa trọn evidence đã định nghĩa. B trả `p3_para_001`, chứa đủ evidence về thời gian tiêu chuẩn. Chunk này không bao phủ toàn bộ Điều 2.
- **`q20`, trang 30:** A trả các cửa sổ chứa những phần khác nhau của điều kiện hạ bậc. `p30_fix_001` kết thúc tại “5% tổng số”, `p30_fix_002` bắt đầu giữa cụm “hần phải thi lại…”, nên không có một chunk chứa đủ hai evidence bắt buộc. B/C trả `p30_para_001`, chứa cả điều kiện học lại và kỷ luật. Nhãn grounding A là 1/2 theo bảng chấm đã xác nhận; đây là đánh giá thủ công có tính chủ quan.

Bài chọn **C** khi phạm vi section được cung cấp rõ ràng, vì giữ được kết quả của B và loại các kết quả ngoài phạm vi. Nếu không biết section, C chạy như B. Lọc sai section có thể loại mất evidence đúng; không nên suy ra filter từ gold answer hoặc gán phạm vi khi chưa có căn cứ.

Hạn chế chính là corpus tự biên soạn, test chỉ có 5 câu và đã được dùng lại, cùng một tác giả chuẩn bị câu hỏi và chấm mẫu. Các điểm trung bình audit có thể chịu thiên lệch. Parser chưa giữ hoàn toàn ranh giới điều khoản; các tiêu đề như “Điều 2.” đôi khi dính vào chunk trước. Nếu làm tiếp, nên bổ sung test mới, người chấm thứ hai và thử giữ heading hoặc kết hợp BM25 trên cùng thiết lập so sánh.

## 6. Demo và cách kiểm tra

Chạy từ thư mục root:

```bash
python -m pip install -r starter/requirements.txt
python -m demo
```

Mở **http://127.0.0.1:8765**. Demo mặc định đọc trace đã lưu, không cần API key. Có thể lọc dev/test, so sánh A/B/C, xem evidence được đánh dấu, mở PDF đúng trang và xuất bảng nhãn. [Ảnh desktop](../../assets/demo-desktop.png) · [Ảnh mobile](../../assets/demo-mobile.png).

Tra cứu câu hỏi mới dùng `python -m demo --live`, cần `.env` ở máy chủ và Chroma đã được dựng bởi pipeline. Query mới không có gold nên không tự tính Hit@1/Hit@3. Hai cách chạy pipeline tương đương là `python -m src.run` và `python -m starter.src.run`.

Kiểm tra bài và các nhánh lỗi:

```bash
python scripts/verify_submission.py
python scripts/test_evaluation_strict.py
python scripts/test_obsolete_chunks.py
python scripts/test_pipeline_safety.py
python scripts/test_demo.py
```

Demo chỉ bind loopback, dùng danh sách route cố định, kiểm tra Host/Origin, giới hạn body/query và không đưa key xuống trình duyệt. Lỗi provider được rút gọn để tránh lộ URL hoặc nội dung nhạy cảm. Những biện pháp này được kiểm thử cho phạm vi demo local, không phải chứng nhận bảo mật tổng thể.

**Công cụ hỗ trợ:** Codex/ChatGPT hỗ trợ lập trình, rà soát và biên tập. Học viên xác nhận bảng chấm và chịu trách nhiệm giải thích bài làm. Lần hoàn thiện demo không chạy lại Gemini để tạo số liệu retrieval mới.
