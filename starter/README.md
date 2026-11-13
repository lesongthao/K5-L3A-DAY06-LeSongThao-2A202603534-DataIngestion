# Starter trong bài nộp Day 06

Bản hiện tại đã được triển khai bằng Gemini Embedding và ChromaDB. `starter/src/` là bản sao tương thích của `src/` ở root; hai cách chạy xuất chung vào `results/` và `artifacts/` ở root.

Chạy các lệnh sau từ thư mục root của repo:

```bash
python -m pip install -r starter/requirements.txt
python scripts/verify_submission.py
python scripts/test_evaluation_strict.py
python scripts/test_obsolete_chunks.py
```

Kiểm tra offline không cần API key. Để chạy lại embedding và retrieval, tạo `.env` hoặc `starter/.env` chứa `GEMINI_API_KEY`, rồi dùng một trong hai lệnh:

```bash
python -m src.run
python -m starter.src.run
```

Hai lệnh trên là lựa chọn tương đương; chạy cả hai sẽ thực hiện pipeline hai lần. Xem [README của bài nộp](../README.md) để biết corpus, benchmark, outputs và các giới hạn.

`docker-compose.yml`, `init.sql`, `scripts/check_setup.py` và `.env.example` được giữ từ starter PostgreSQL + pgvector ban đầu. Pipeline ChromaDB hiện tại không sử dụng PostgreSQL. Nếu dùng công cụ kiểm tra PostgreSQL cũ, cần cài thêm `psycopg[binary]` và làm theo [starter gốc](https://github.com/VinUni-AI20k/K5-L3-Day06-DataIngestionEngineering/blob/main/starter/README.md).
