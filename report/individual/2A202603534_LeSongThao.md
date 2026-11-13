# Báo cáo cá nhân — Day 6: Data Ingestion Engineering

**Học viên:** Lê Song Thảo  
**MSSV:** 2A202603534  
**Lớp:** K5-L3A  
**Kho lưu trữ mã nguồn:** [lesongthao/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion](https://github.com/lesongthao/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion)  

---

## Dữ liệu và pipeline

- **Chủ đề, nguồn/quyền, số trang và quy tắc tính trang:**
  - *Chủ đề:* Sổ tay Sinh viên và Quy chế Đào tạo Đại học Chính quy năm học 2024 - 2025.
  - *Nguồn và quyền sử dụng:* Tài liệu do học viên **Lê Song Thảo** tự biên soạn và kết xuất kỹ thuật bằng thư viện `reportlab` (phiên bản 5.1.0). Nội dung văn bản được chuẩn hóa, tổng hợp trung thực từ các văn bản quy phạm pháp luật công khai của Bộ Giáo dục & Đào tạo và Chính phủ Việt Nam:
    1. Thông tư 08/2021/TT-BGDĐT: Quy chế đào tạo trình độ đại học ([Thư viện Pháp luật](https://thuvienphapluat.vn/van-ban/Giao-duc/Thong-tu-08-2021-TT-BGDDT-Quy-che-dao-tao-trinh-do-dai-hoc-468202.aspx)).
    2. Thông tư 10/2016/TT-BGDĐT: Quy chế công tác sinh viên đối với chương trình đào tạo đại học hệ chính quy ([Thư viện Pháp luật](https://thuvienphapluat.vn/van-ban/Giao-duc/Thong-tu-10-2016-TT-BGDDT-Quy-che-cong-tac-sinh-vien-dai-hoc-he-chinh-quy-308316.aspx)).
    3. Nghị định 81/2021/NĐ-CP: Cơ chế thu, quản lý học phí và chính sách miễn, giảm học phí ([Cổng TTĐT Chính phủ](https://chinhphu.vn)).
    4. Quyết định 157/2007/QĐ-TTg: Tín dụng đối với học sinh, sinh viên.
    Tài liệu được phát hành mở cho mục đích nghiên cứu, học tập Data Ingestion theo giấy phép Creative Commons **CC-BY 4.0**; metadata PDF phản ánh trung thực thông tin tác giả và công cụ kết xuất, không sử dụng số quyết định hư cấu.
  - *Tổng số trang vật lý:* 35 trang PDF (tổng số ký tự nội dung: 45.269 ký tự).
  - *Quy tắc tính trang:* Chỉ tính các trang thực sự chứa nội dung điều khoản quy chế, nghĩa vụ, quyền lợi và chính sách đào tạo (từ Trang 3 đến Trang 34, tổng cộng **32 trang nội dung hữu ích**, đạt yêu cầu tối thiểu $\ge 30$ trang của đề bài). Loại trừ đúng 3 trang không phải nội dung quy chuẩn: Trang 1 (bìa tài liệu), Trang 2 (lời nói đầu và mục lục), Trang 35 (phụ lục danh mục văn bản tham chiếu).
  - *Chi tiết lưu trữ:* Toàn bộ danh mục trang, số ký tự từng trang và quy tắc tính được lưu trữ chuẩn hóa tại file [data/manifest.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/data/manifest.json).

- **Chuẩn hóa, lỗi và giới hạn:**
  - *Chuẩn hóa Unicode:* Sử dụng `unicodedata.normalize("NFC", text)` để quy chuẩn toàn bộ bảng mã tiếng Việt dựng sẵn.
  - *Xử lý khoảng trắng và dòng:* Chuẩn hóa dấu xuống dòng (`\r\n` $\rightarrow$ `\n`), gộp khoảng trắng thừa (`[ \t]+` $\rightarrow$ ` `), loại bỏ non-breaking space (`\u00a0`), và thu gọn các khoảng trống ngắt dòng lớn hơn 2 dòng thành phân đoạn chuẩn (`\n\n`).
  - *Ghi nhận lỗi/trang bỏ qua:* Hệ thống nhận diện và ghi log chi tiết 3 trang bị loại trừ (`pypdf` trích xuất được nhưng dung lượng hoặc tính chất là non-content) vào file [results/skipped_pages.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/skipped_pages.json), không xảy ra lỗi mã hóa ký tự hay rỗng trang ngoài ý muốn.
  - *Xử lý tài liệu thay đổi (Obsolete Chunk Cleanup):* Khi cập nhật hoặc tái nạp tài liệu cùng `document_id` nhưng có số lượng chunk giảm đi, `ChromaVectorStore` tự động truy vấn danh sách `chunk_id` hiện hữu trong cơ sở dữ liệu và gọi lệnh `delete(ids=...)` loại bỏ triệt để các chunk mồ côi (obsolete chunks) trước khi upsert các chunk mới, đảm bảo tính toàn vẹn và không để lại chunk rác lỗi thời.

- **Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí:**
  - *Embedding Model:* Google Gemini Embedding API, tên model `models/gemini-embedding-001` (Google GenAI SDK v3.0.0), số chiều vector: **3072 chiều**.
  - *Vector Store:* **ChromaDB v1.5.9** ở chế độ lưu trữ đĩa bền vững (`chromadb.PersistentClient(path="./results/chroma_db")`), metric tính độ tương đồng: **Cosine Similarity** (`{"hnsw:space": "cosine"}`).
  - *Lệnh chạy pipeline:*
    ```bash
    python -m starter.src.run
    # hoặc
    python -m src.run
    ```
  - *Chi phí:* Billed Cost thực tế = **$0.00** (toàn bộ các yêu cầu embedding nằm trong hạn mức Free Tier của Google Gemini API). Ước tính chi phí thương mại theo đơn giá chuẩn $0.00002 / 1.000 tokens: Chiến lược A (~14.113 tokens) $\approx$ \$0.000282; Chiến lược B (~12.913 tokens) $\approx$ \$0.000258; Chiến lược C tái sử dụng vector của B nên chi phí phát sinh là \$0.00.

- **Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn:**
  - *Metadata bắt buộc:* `document_id` ("so-tay-sinh-vien-2024"), `source` ("data/so_tay_sinh_vien_2024.pdf"), `page` (số trang vật lý từ 3 đến 34), `chunk_id` (định danh duy nhất không trùng lặp theo quy tắc `{doc_id}_p{page}_{strategy}_{index}`).
  - *Trường lọc bổ sung (`section`):* Giá trị gồm 4 nhóm phân vùng nghiệp vụ chính: `quy_che_dao_tao` (Trang 3–10), `hoc_bong_hoc_phi` (Trang 11–18), `cong_tac_sinh_vien` (Trang 19–26), `tot_nghiep_khen_thuong` (Trang 27–34).
  - *Lý do chọn:* Trường `section` phản ánh ranh giới ngữ cảnh pháp lý và chuyên môn thực tế của trường đại học. Khi người dùng tra cứu về "học phí", filter `{"section": "hoc_bong_hoc_phi"}` giúp ngăn chặn việc vector store kéo nhầm các chunk ở Chương I (quy định tín chỉ lý thuyết/thực hành) vào Top-3 do trùng lặp từ khóa.

---

## Cấu hình và benchmark

- **A / B / C (tham số cụ thể, khác biệt duy nhất B–C):**
  - **Chiến lược A (Fixed-size Baseline):** Cắt theo cửa sổ cố định `chunk_size = 500` ký tự, bước nhảy dịch chuyển với `overlap = 50` ký tự. Sinh ra **116 chunks**. Metadata: `source`, `page`, `section`, `year`. Truy xuất Top-3 không áp dụng metadata filter.
  - **Chiến lược B (Structure-aware Paragraph):** Cắt theo cấu trúc điều khoản và đoạn văn logic (`\n\n`), có giới hạn kích thước trần `max_size = 800` ký tự. Nếu đoạn văn hoặc câu dài vượt quá giới hạn, hệ thống ngắt phân đoạn theo dấu chấm câu hoặc dấu cách đảm bảo tuyệt đối không có chunk nào vượt quá 800 ký tự. Sinh ra **72 chunks**. Cùng embedding model, cùng vector store, truy xuất Top-3 không áp dụng metadata filter.
  - **Chiến lược C (Paragraph + Metadata Filter):** Sử dụng **chính xác 72 chunks và vector embeddings của Chiến lược B** (không thay đổi bất kỳ yếu tố nào về chunking hay mô hình). Điểm khác biệt duy nhất giữa B và C: Khi thực hiện truy xuất cho các câu hỏi có điều kiện ngữ cảnh/phạm vi, Chiến lược C truyền bộ lọc `where={"section": <target_section>}` vào lệnh truy vấn vector store.

- **$\ge 20$ câu: phân chia $\ge 15$ dev / $\ge 5$ test, câu metadata filter và cách kiểm chứng evidence:**
  - *Quy mô:* Tổng cộng **20 câu hỏi** được lưu trữ tại [benchmark/benchmark_questions.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/benchmark/benchmark_questions.json).
  - *Phân chia split:* **15 câu Dev (q01 đến q15)** và **5 câu Test (q16 đến q20)**. Phân chia độc lập và cố định trước khi chạy pipeline.
  - *Câu hỏi kiểm tra Metadata Filter:* Có **3 câu có filter** (2 câu thuộc Dev: `q08`, `q11`; 1 câu thuộc Test: `q19`).
  - *Cách kiểm chứng Evidence:* 100% các câu hỏi đều có trường `evidence_quote` (hoặc `evidence_quotes` đối với các câu có nhiều điều kiện như `q07` và `q20`) là đoạn trích nguyên văn từ nội dung đã trích xuất của `gold_page`. Script kiểm thử tự động đã xác nhận chuỗi con bằng chứng tồn tại chính xác tại trang nguồn và hàm chấm `is_evidence_hit` xác thực nghiêm ngặt cả `gold_source_id`, `gold_page` và đầy đủ các trích dẫn bằng chứng bắt buộc.

- **Tiêu chí chọn chiến lược đã chốt trước khi xem test:**
  - Tiêu chí ưu tiên số 1: **Retrieval Accuracy (Evidence Hit@3)** trên tập Dev phải đạt tối thiểu $\ge 90\%$.
  - Tiêu chí ưu tiên số 2: **Tính mạch lạc của Chunk (Chunk Coherence)** trung bình phải đạt $\ge 1.5/2.0$ để AI Agent khi đọc context không bị đứt câu hay hiểu sai chủ thể.
  - Tiêu chí ưu tiên số 3: **Tuân thủ bộ lọc Metadata (Filter Compliance)** đạt $100\%$ khi có yêu cầu lọc phạm vi.
  - Tiêu chí ưu tiên số 4: **Hiệu quả tài nguyên (Tối ưu số lượng chunk và thời gian ingest)**.

---

## Kết quả

### Bảng 1: Hiệu năng Truy xuất và Tài nguyên Pipeline

| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian đo đạc | Chi phí thực tế / Ước tính |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **A (Fixed-size 500/50)** | Dev | 10/15 (66.7%) | 12/15 (80.0%) | 116 | Chunk: 0.00s<br>Embed: 63.09s<br>Store: 0.53s<br>**Tổng Ingest: 63.95s** | \$0.00 / \$0.000282 |
| **A (Fixed-size 500/50)** | Test | 3/5 (60.0%) | 3/5 (60.0%) | 116 | (Query time: ~1.2s) | \$0.00 |
| **B (Paragraph max 800)** | Dev | 13/15 (86.7%) | 15/15 (100.0%) | 72 | Chunk: 0.002s<br>Embed: 79.74s<br>Store: 0.26s<br>**Tổng Ingest: 80.34s** | \$0.00 / \$0.000258 |
| **B (Paragraph max 800)** | Test | 5/5 (100.0%) | 5/5 (100.0%) | 72 | (Query time: ~1.2s) | \$0.00 |
| **C (Paragraph + Filter)** | Dev | 13/15 (86.7%) | 15/15 (100.0%) | 72 | Tái sử dụng chunks & embeddings từ B<br>Store: 0.29s<br>**Tổng Ingest: 80.34s** | \$0.00 / \$0.00 |
| **C (Paragraph + Filter)** | Test | 5/5 (100.0%) | 5/5 (100.0%) | 72 | (Query time: ~1.2s) | \$0.00 |

### Bảng 2: Đánh giá Thủ công 5 Khía cạnh Chất lượng

| Strategy | Coherence trung bình /2 (n=10) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 (n=5) |
|---|:---:|:---:|:---:|:---:|
| **A (Fixed-size)** | 0.50 / 2.0 (10) | 15/15 (100.0%) | N/A (Không lọc) | 0 câu mức 0, 2 câu mức 1, 3 câu mức 2 $\rightarrow$ **1.60 / 2.0** |
| **B (Paragraph)** | **1.90 / 2.0** (10) | 15/15 (100.0%) | N/A (Không lọc) | 0 câu mức 0, 0 câu mức 1, 5 câu mức 2 $\rightarrow$ **2.00 / 2.0** |
| **C (Paragraph + Filter)** | **1.90 / 2.0** (10) | 15/15 (100.0%) | **1/1 (100.0%) [Test]**<br>*(2/2 trên Dev)* | 0 câu mức 0, 0 câu mức 1, 5 câu mức 2 $\rightarrow$ **2.00 / 2.0** |

- **Đường dẫn trace, nhãn thủ công và cách chọn mẫu:**
  - *Dữ liệu trace chi tiết:* [results/traces_strategy_a.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/traces_strategy_a.json), [results/traces_strategy_b.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/traces_strategy_b.json), [results/traces_strategy_c.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/traces_strategy_c.json). Mỗi trace xuất toàn bộ văn bản của top-3 chunks cùng đầy đủ metadata truy nguồn (`document_id`, `source`, `page`, `section`, `year`, `chunk_strategy`, `chunk_size`, `score`, `distance`, `is_evidence_hit`).
  - *Nhật ký thí nghiệm tổng hợp:* [artifacts/experiment_log.csv](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/artifacts/experiment_log.csv) và [results/benchmark_summary.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/benchmark_summary.json).
  - *Bảng nhãn audit thủ công:* [results/audit_report.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/audit_report.json).
  - *Người thực hiện audit:* Học viên **Lê Song Thảo** (MSSV: 2A202603534) tự đọc và đối chiếu thủ công 100% từng chunk với tài liệu PDF gốc tại các vị trí nguồn cố định, có sự hỗ trợ của script để chuẩn hóa dữ liệu so khớp.
  - *Cách chọn mẫu Coherence:* Chọn cố định 10 vị trí trang trải dài cả 4 chương (Trang 3, 5, 8, 11, 13, 16, 21, 24, 28, 30) trước khi chạy chấm điểm để đảm bảo tính khách quan không thiên vị.
  - *Cách chọn mẫu Metadata & Grounding:* Đánh giá trên toàn bộ 5 câu hỏi của tập Test độc lập (`q16` $\rightarrow$ `q20`) với $5 \times 3 = 15$ chunks thuộc Top-3 cho từng chiến lược A, B, C.

---

## Phân tích và kết luận

### 1. So sánh Chiến lược A – B và B – C

- **Tác động của Chunking (A vs B):**
  - Chiến lược A (cắt cứng 500 ký tự) tạo ra tới **116 chunks** (nhiều hơn 61.1% so với Chiến lược B chỉ có 72 chunks), dẫn đến thời gian tạo embedding lâu hơn và làm phân mảnh văn bản.
  - Nghiêm trọng hơn, việc cắt cố định theo số ký tự gây ra hiện tượng **"gãy ranh giới ngữ nghĩa" (semantic boundary fragmentation)**: Các câu văn, bảng số liệu hoặc điều kiện bị cắt làm đôi ở ranh giới giữa hai chunk. Kết quả là Hit@3 của Chiến lược A giảm xuống chỉ còn **80% trên Dev** và **60% trên Test** (bỏ lỡ bằng chứng do câu bị cắt mất một nửa). Điểm Coherence trung bình chỉ đạt **0.50/2.0** do 5/10 mẫu bị đứt câu giữa chừng.
  - Ngược lại, Chiến lược B phân chia theo ranh giới đoạn văn/điều khoản logic giúp bảo tồn tính nguyên vẹn ngữ nghĩa của phần lớn các điều khoản quy chế, đạt điểm Coherence cao **1.90/2.0** và đưa Hit@3 lên **100% trên cả tập Dev và tập Test**. Điểm Coherence không đạt tuyệt đối 2.0/2.0 do ở một số vị trí như Trang 30 (`p30_para_000`), dòng tiêu đề tiểu mục ("2. Các trường hợp bị hạ một bậc...") bị dính vào cuối đoạn trước do ranh giới ngắt dòng `\n\n`.

- **Tác động của Metadata Filter (B vs C):**
  - Khác biệt duy nhất giữa B và C là bộ lọc metadata. Ở tập Test nhỏ gồm các câu hỏi rõ nghĩa, cả B và C đều đạt Hit@3 là 100%.
  - Tuy nhiên, sự khác biệt thể hiện rõ rệt ở **tính tinh khiết của không gian tìm kiếm (Search Space Purity)** và khả năng loại bỏ chunk gây nhiễu:
    * Minh chứng điển hình nhất là câu hỏi **`q08`** ("Mức học phí đối với 01 tín chỉ thực hành, thí nghiệm của chương trình đào tạo chuẩn là bao nhiêu?"):
    * **Chiến lược B (không áp dụng filter):** Top-3 trả về gồm Rank 1 (`p11_para_000`, Trang 11, `hoc_bong_hoc_phi`, hit=True), Rank 2 (`p11_para_001`, Trang 11, `hoc_bong_hoc_phi`), nhưng **Rank 3 lại kéo chunk `p4_para_000` (Trang 4, `quy_che_dao_tao`)** vào danh sách. Nguyên nhân là chunk Trang 4 ở Chương I chứa cụm từ quy định "tín chỉ lý thuyết, tín chỉ thực hành" khiến mô hình embedding có độ tương đồng ngữ nghĩa cao, tạo ra kết quả gây nhiễu ngoài phạm vi chuyên môn học phí.
    * **Chiến lược C (áp dụng `where={"section": "hoc_bong_hoc_phi"}`):** Bộ lọc metadata đã **loại bỏ triệt để** chunk gây nhiễu Trang 4. Top-3 của Chiến lược C gồm Rank 1 (`p11_para_000`), Rank 2 (`p11_para_001`) và Rank 3 (`p15_para_000`), **100% chunks trong Top-3 đều thuộc đúng Chương II về học bổng và học phí**.

### 2. Hai ví dụ sai điển hình (Failure Analysis)

- **Ví dụ lỗi 1 — Câu `q01` (Tập Dev, Trang 3):**
  - *Câu hỏi:* "Thời gian đào tạo tiêu chuẩn đối với sinh viên khối ngành Kỹ thuật - Công nghệ là bao nhiêu năm?"
  - *Evidence chuẩn:* `"Đối với khối ngành Kỹ thuật - Công nghệ là 4,0 năm (tương đương 8 học kỳ chính)"`
  - *Chiến lược A thất bại:* Cửa sổ 500 ký tự của chunk `so-tay-sinh-vien-2024_p3_fix_001` kết thúc ngay tại cụm từ "...(bao gồm..." và chunk kế tiếp `so-tay-sinh-vien-2024_p3_fix_002` bắt đầu bằng `"ngành Kỹ thuật - Công nghệ là 4,0 năm..."`. Cụm từ `"Đối với khối"` bị cắt nằm ở chunk trước, còn phần vị ngữ nằm ở chunk sau. Do bằng chứng bị chia cắt ngang xương sống câu văn, không có chunk nào chứa trọn vẹn evidence quote $\rightarrow$ Hit@3 = False.
  - *Chiến lược B thành công:* Chunk `so-tay-sinh-vien-2024_p3_para_001` gom trọn vẹn toàn bộ Điều 2: Kế hoạch và thời gian đào tạo, chứa đầy đủ cả chủ ngữ và vị ngữ $\rightarrow$ Hit@1 = True.

- **Ví dụ lỗi 2 — Câu `q20` (Tập Test, Trang 30):**
  - *Câu hỏi:* "Trường hợp nào sinh viên có kết quả học tập loại Xuất sắc hoặc Giỏi bị hạ một bậc xếp loại tốt nghiệp?"
  - *Evidence chuẩn gồm cả 2 điều kiện:*
    1. `"Có khối lượng tín chỉ của các học phần phải thi lại hoặc học lại vượt quá 5% tổng số tín chỉ quy định cho toàn bộ chương trình đào tạo của ngành học"`
    2. `"Đã bị kỷ luật từ mức cảnh cáo cấp trường trở lên trong thời gian học tập tại trường"`
  - *Chiến lược A thất bại:* Chunk `so-tay-sinh-vien-2024_p30_fix_001` chỉ chứa phần đầu `"2. Các trường hợp bị hạ một bậc xếp loại tốt nghiệp: Hạng tốt nghiệp của n..."` rồi bị đứt. Chunk tiếp theo `fix_002` bắt đầu bằng `"hần phải thi lại hoặc học lại vượt quá 5% tổng số tín chỉ..."` và bị ngắt trước khi diễn giải đầy đủ điều kiện kỷ luật. Cả hai chunk đều không chứa đủ 100% bằng chứng hỗ trợ hai trường hợp hạ bậc $\rightarrow$ Hit@3 = False, Grounding chỉ được chấm 1/2.
  - *Chiến lược B & C thành công:* Toàn bộ Khoản 2 Điều 31 về 2 trường hợp hạ bậc nằm trọn vẹn trong chunk `so-tay-sinh-vien-2024_p30_para_001` $\rightarrow$ Hit@1 = True, Grounding đạt điểm tối đa 2/2.

### 3. Chiến lược được chọn, đánh đổi và điều kiện áp dụng

- **Chiến lược được lựa chọn:** **Chiến lược C (Paragraph-based Chunking kết hợp Metadata Filter)**.
- **Lý do lựa chọn:**
  1. Đáp ứng toàn diện mọi tiêu chí đã chốt trước thử nghiệm: Hit@3 đạt $100\%$ trên cả Dev và Test, Coherence đạt $1.90/2.0$, Grounding đạt $2.0/2.0$, tuân thủ filter $100\%$.
  2. Tiết kiệm tài nguyên: Giảm số lượng chunk từ 116 xuống 72 chunks (giảm $37.9\%$ dung lượng index vector và chi phí embedding).
  3. Loại bỏ triệt để nhiễu xuyên phân vùng chuyên môn nhờ bộ lọc `section`.
- **Đánh đổi (Trade-offs):**
  - Cần chi phí công sức tiền xử lý cao hơn: Cần viết parser phân tích cấu trúc tài liệu (`by_paragraph`) kèm bộ kiểm soát kích thước trần (`_split_oversized_unit`) thay vì chỉ dùng phép trượt chuỗi đơn giản (`fixed_size`).
  - Phụ thuộc vào chất lượng metadata: Nếu metadata gán nhãn sai hoặc query của người dùng không trích xuất được filter đúng, việc lọc cứng có thể gây loại bỏ nhầm tài liệu liên quan (False Negative). Do đó, chỉ áp dụng filter khi giá trị metadata được xác định rõ ràng từ ngữ cảnh truy vấn.

### 4. Hạn chế của nghiên cứu

- *Quy mô tập Test:* Tập Test gồm 5 câu là đại diện tiêu biểu để kiểm thử tại chỗ trong phạm vi lab 4 giờ; chưa đủ lớn để đưa ra kết luận thống kê suy rộng cho mọi thể loại văn bản khác ngoài thể loại văn bản quy chế.
- *Đo lường thời gian và chi phí:* Tốc độ gọi API phụ thuộc vào độ trễ mạng Internet và cơ chế điều tiết băng thông (rate limit) của provider bên ngoài; chi phí ghi nhận $0.00$ là do dữ liệu nằm trọn trong hạn mức miễn phí hàng tháng của Gemini.
- *Hiện tượng tiêu đề dính đoạn:* Thuật toán ngắt đoạn theo `\n\n` đôi khi để lại tiêu đề của mục tiếp theo ở cuối chunk trước (như trường hợp `p30_para_000`), cần bổ sung regex nhận diện dòng tiêu đề để ngắt trang tách biệt hơn.

### 5. Đề xuất cải tiến và mở rộng

Nếu tiếp tục mở rộng dự án trong tương lai, các hướng nâng cấp ưu tiên bao gồm:
1. **Hybrid Retrieval (Dense + BM25):** Kết hợp vector embedding của Gemini với bộ lọc từ khóa BM25 để xử lý hoàn hảo các câu hỏi chứa mã học phần hoặc từ viết tắt chuyên biệt (ví dụ: "IC3", "MOS", "TOEIC", "GPA", "VSTEP").
2. **Contextual Retrieval / Title Prepending:** Tự động gắn tên Chương và số hiệu Điều khoản vào đầu mỗi chunk trước khi embed (ví dụ: `[Chương IV - Điều 31: Xếp loại tốt nghiệp] ...`) để chunk vừa giữ được tính cục bộ vừa mang đầy đủ bối cảnh toàn cục của tài liệu.
3. **Bộ phân loại Query Filter tự động (Query Router):** Sử dụng một LLM nhỏ gọn để tự động phân loại ý định người dùng và trích xuất trường `section` tương ứng trước khi gọi vector search, tránh việc phải chỉ định filter thủ công.
