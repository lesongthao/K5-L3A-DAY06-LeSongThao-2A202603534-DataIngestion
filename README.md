# Day 06 · Data Ingestion Engineering

**Lab cá nhân** · **4 giờ** · **Dữ liệu tự chọn**

Biến tài liệu thành kho tri thức có thể truy xuất cho AI agent, rồi đo xem cách chuẩn bị dữ liệu nào hiệu quả nhất.

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark |
|---|---|---|
| Tối thiểu **30 trang nội dung** | Tối thiểu **3 cấu hình** | Tối thiểu **20 câu hỏi** |

## Hướng dẫn cài đặt và Chạy thực nghiệm (Học viên: Lê Song Thảo - MSSV: 2A202603534)

### 1. Cài đặt môi trường
Yêu cầu Python 3.11+. Cài đặt các thư viện cần thiết:
```bash
pip install -r starter/requirements.txt
```
*(Bao gồm: `pypdf>=5.0.0`, `chromadb>=1.5.0`, `reportlab>=5.0.0`, `google-genai>=3.0.0`, `python-dotenv>=1.0.0`)*

### 2. Cấu hình API Key
Tạo file `.env` (hoặc `starter/.env`) chứa `GEMINI_API_KEY`:
```text
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Dữ liệu và Benchmark
- **Corpus**: `data/so_tay_sinh_vien_2024.pdf` (32 trang nội dung hữu ích / 35 trang vật lý, manifest trung thực tại `data/manifest.json`).
- **Benchmark**: `benchmark/benchmark_questions.json` (20 câu hỏi: 15 dev / 5 test, 3 câu có metadata filter). 100% câu hỏi có evidence kiểm chứng nguyên văn từ trang nguồn.

### 4. Lệnh chạy Pipeline hoàn chỉnh
```bash
# Chạy pipeline Day 06 trọn vẹn: nạp corpus, sinh 3 chiến lược A/B/C, embed bằng gemini-embedding-001 (3072d), lưu ChromaDB persistent, chạy benchmark 20 câu, audit 5 khía cạnh và tự động xuất tất cả artifacts
python -m starter.src.run
# hoặc
python -m src.run
```

**Các tệp đầu ra được tự động tạo và cập nhật:**
- `results/traces_strategy_a.json`: Traces top-3 với toàn bộ văn bản và metadata cho Chiến lược A.
- `results/traces_strategy_b.json`: Traces top-3 với toàn bộ văn bản và metadata cho Chiến lược B.
- `results/traces_strategy_c.json`: Traces top-3 với toàn bộ văn bản và metadata cho Chiến lược C.
- `results/benchmark_summary.json`: Tóm tắt đo đạc Hit@1, Hit@3, filter compliance, thời gian đo đạc và chi phí.
- `results/audit_report.json`: Kết quả audit thủ công 5 khía cạnh chất lượng (Coherence 10 mẫu, Metadata 15 mẫu x 3 chiến lược, Grounding 5 câu test x 3 chiến lược).
- `results/skipped_pages.json`: Nhật ký ghi nhận các trang non-content bị loại trừ.
- `artifacts/experiment_log.csv`: Nhật ký thí nghiệm chuẩn hóa.
- `results/chroma_db/`: Vector database bền vững (ChromaDB PersistentClient).

### 5. Kiểm thử độc lập
```bash
# Kiểm tra đối chiếu evidence khớp 100% ký tự trên trang PDF
python scripts/test_evaluation_strict.py

# Kiểm tra cơ chế dọn dẹp obsolete chunks khi tài liệu cập nhật giảm số chunk
python scripts/test_obsolete_chunks.py
```

Báo cáo cá nhân chi tiết: [report/individual/2A202603534_LeSongThao.md](report/individual/2A202603534_LeSongThao.md).

---

## Bắt đầu nhanh (Đề bài gốc)

Dùng [starter PostgreSQL + pgvector](starter/README.md) để dựng database và hoàn thiện các hàm TODO, hoặc tự chọn vector store tương đương. Starter chỉ là khung: **bạn tự hiện thực pipeline và benchmark**.

## 1. Xây pipeline

![Đọc tài liệu, chuẩn hóa, chia chunk, tạo vector, lưu và kiểm tra](assets/ingestion-pipeline.svg)

Chọn tài liệu được phép sử dụng; giữ **ID tài liệu, nguồn, trang/vị trí** và metadata phù hợp. Dùng embedding model thật qua API hoặc chạy local; lưu và truy xuất bằng pgvector, Qdrant, Chroma hoặc một store tương đương.

## 2. So sánh và đánh giá

![Ba chiến lược được đánh giá trên cùng corpus và benchmark dev/test](assets/benchmark-workflow.svg)

Dùng cùng dữ liệu, model và câu hỏi cho cả ba cấu hình. Tách **15 câu dev / 5 câu test** trước khi chạy; chọn cấu hình trên dev, rồi đánh giá test sau khi cố định. Mỗi câu hỏi cần có đoạn bằng chứng và trang nguồn; thiết kế bộ câu hỏi và đánh giá theo [BENCHMARK.md](BENCHMARK.md).

Đánh giá theo năm khía cạnh: **độ chính xác truy xuất**, **tính mạch lạc của chunk**, **tính hữu dụng của metadata**, **chất lượng grounding** và **tác động của chiến lược dữ liệu**. Giải thích lựa chọn bằng kết quả, ví dụ lỗi và các đánh đổi.

## 3. Chuẩn bị bài nộp

1. Chạy pipeline và lưu cấu hình, kết quả top-3, trace cùng nhãn đánh giá thủ công.
2. Điền [thông tin học viên](STUDENT.md), [nhật ký thí nghiệm](artifacts/experiment_log.csv) và bản sao [mẫu báo cáo cá nhân](report/individual/MSSV_HoTen.md).
3. Kiểm tra mã nguồn, cách chạy, manifest dữ liệu và checklist trong [SUBMISSION.md](SUBMISSION.md).

## Tài liệu hướng dẫn

| Bạn cần tìm | Tài liệu |
|---|---|
| Setup baseline PostgreSQL + pgvector | [starter/README.md](starter/README.md) |
| Các bước làm và cách tính chỉ số | [GUIDE.md](GUIDE.md) |
| Tiến độ trong 4 giờ | [CHECKPOINTS.md](CHECKPOINTS.md) |
| Năm tiêu chí benchmark và bộ câu hỏi | [BENCHMARK.md](BENCHMARK.md) |
| Tiêu chí chấm điểm | [RUBRIC.md](RUBRIC.md) |
| Quy tắc sử dụng dữ liệu, AI và API | [RULES.md](RULES.md) |
| Cách nộp bài | [SUBMISSION.md](SUBMISSION.md) |

[data/format-example.json](data/format-example.json) chỉ minh họa định dạng, không phải corpus đủ điều kiện. Phần xử lý và benchmark do bạn tự hiện thực; không bắt buộc xây chatbot.
