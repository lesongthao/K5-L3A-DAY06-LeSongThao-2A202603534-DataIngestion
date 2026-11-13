# Báo cáo cá nhân — Day 6: Data Ingestion Engineering

**Học viên:** Lê Song Thảo  
**MSSV:** 2A202603534  
**Lớp:** K5-L3A  
**Kho lưu trữ mã nguồn:** [lesongthao/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion](https://github.com/lesongthao/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion)  

---

## Dữ liệu và pipeline

- **Chủ đề, nguồn/quyền, số trang và quy tắc tính trang:**
  - *Chủ đề:* Sổ tay Sinh viên và Quy chế Đào tạo Đại học Chính quy năm học 2024 - 2025.
  - *Nguồn và quyền sử dụng:* Tài liệu quy chuẩn ban hành nội bộ cho người học của Trường Đại học Công nghệ và Kỹ thuật (căn cứ Thông tư 08/2021/TT-BGDĐT và Nghị định 81/2021/NĐ-CP), công khai cho sinh viên, được phép lưu hành và trích dẫn phục vụ học tập, nghiên cứu khoa học.
  - *Tổng số trang vật lý:* 35 trang PDF (tổng số ký tự nội dung: 45.269 ký tự).
  - *Quy tắc tính trang:* Chỉ tính các trang thực sự chứa nội dung điều khoản quy chế, nghĩa vụ, quyền lợi và chính sách đào tạo (từ Trang 3 đến Trang 34, tổng cộng **32 trang nội dung hữu ích**, đạt yêu cầu tối thiểu $\ge 30$ trang của đề bài). Loại trừ đúng 3 trang không phải nội dung quy chuẩn: Trang 1 (bìa tài liệu), Trang 2 (lời nói đầu và mục lục), Trang 35 (phụ lục danh mục văn bản tham chiếu).
  - *Chi tiết lưu trữ:* Toàn bộ danh mục trang, số ký tự từng trang và quy tắc tính được lưu trữ chuẩn hóa tại file [data/manifest.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/data/manifest.json).

- **Chuẩn hóa, lỗi và giới hạn:**
  - *Chuẩn hóa Unicode:* Sử dụng `unicodedata.normalize("NFC", text)` để quy chuẩn toàn bộ bảng mã tiếng Việt dựng sẵn.
  - *Xử lý khoảng trắng và dòng:* Chuẩn hóa dấu xuống dòng (`\r\n` $\rightarrow$ `\n`), gộp khoảng trắng thừa (`[ \t]+` $\rightarrow$ ` `), loại bỏ non-breaking space (`\u00a0`), và thu gọn các khoảng trống ngắt dòng lớn hơn 2 dòng thành phân đoạn chuẩn (`\n\n`).
  - *Ghi nhận lỗi/trang bỏ qua:* Hệ thống nhận diện và ghi log chi tiết 3 trang bị loại trừ (`pypdf` trích xuất được nhưng dung lượng hoặc tính chất là non-content), không xảy ra lỗi mã hóa ký tự hay rỗng trang ngoài ý muốn.

- **Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí:**
  - *Embedding Model:* Google Gemini Embedding API, tên model `models/gemini-embedding-001` (phiên bản ổn định của Google GenAI SDK v3.0.0), số chiều vector: **3072 chiều**.
  - *Vector Store:* **ChromaDB v1.5.9** ở chế độ lưu trữ đĩa bền vững (`chromadb.PersistentClient(path="./results/chroma_db")`), metric tính độ tương đồng: **Cosine Similarity** (`{"hnsw:space": "cosine"}`).
  - *Lệnh chạy pipeline:*
    ```bash
    python -m starter.src.run
    # hoặc
    python -m src.run
    ```
  - *Chi phí:* **$0.00** (toàn bộ 186 lần gọi embed văn bản và 20 lần gọi query nằm hoàn toàn trong hạn mức miễn phí Free Tier của Google Gemini API).

- **Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn:**
  - *Metadata bắt buộc:* `document_id` ("so-tay-sinh-vien-2024"), `source` ("data/so_tay_sinh_vien_2024.pdf"), `page` (số trang vật lý từ 3 đến 34), `chunk_id` (định danh duy nhất không trùng lặp theo quy tắc `{doc_id}_p{page}_{strategy}_{index}`).
  - *Trường lọc bổ sung (`section`):* Giá trị gồm 4 nhóm phân vùng nghiệp vụ chính: `quy_che_dao_tao` (Trang 3–10), `hoc_bong_hoc_phi` (Trang 11–18), `cong_tac_sinh_vien` (Trang 19–26), `tot_nghiep_khen_thuong` (Trang 27–34).
  - *Lý do chọn:* Trường `section` phản ánh ranh giới ngữ cảnh pháp lý và chuyên môn thực tế của trường đại học. Khi người dùng tra cứu về "học bổng", filter `{"section": "hoc_bong_hoc_phi"}` giúp ngăn chặn việc thuật toán vector bị nhầm lẫn với các điều khoản khen thưởng cuối năm hoặc điều kiện xét tốt nghiệp vốn cũng có nhắc tới từ khóa "xuất sắc", "học bổng".

---

## Cấu hình và benchmark

- **A / B / C (tham số cụ thể, khác biệt duy nhất B–C):**
  - **Chiến lược A (Fixed-size Baseline):** Cắt theo cửa sổ cố định `chunk_size = 500` ký tự, bước nhảy dịch chuyển với `overlap = 50` ký tự. Sinh ra 116 chunks. Metadata: `source`, `page`, `section`, `year`. Truy xuất Top-3 không áp dụng metadata filter.
  - **Chiến lược B (Structure-aware Paragraph):** Cắt theo cấu trúc điều khoản và đoạn văn logic (`\n\n`), có giới hạn kích thước trần `max_size = 800` ký tự. Nếu đoạn quá dài thì ngắt theo dấu chấm kết thúc câu. Sinh ra 70 chunks. Cùng embedding model, cùng vector store, truy xuất Top-3 không áp dụng metadata filter.
  - **Chiến lược C (Paragraph + Metadata Filter):** Sử dụng **chính xác 70 chunks và vector embeddings của Chiến lược B** (không thay đổi bất kỳ yếu tố nào về chunking hay mô hình). Điểm khác biệt duy nhất giữa B và C: Khi thực hiện truy xuất cho các câu hỏi có điều kiện ngữ cảnh/phạm vi, Chiến lược C truyền bộ lọc `where={"section": <target_section>}` vào lệnh truy vấn vector store.

- **$\ge 20$ câu: phân chia $\ge 15$ dev / $\ge 5$ test, câu metadata filter và cách kiểm chứng evidence:**
  - *Quy mô:* Tổng cộng **20 câu hỏi** được lưu trữ tại [benchmark/benchmark_questions.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/benchmark/benchmark_questions.json).
  - *Phân chia split:* **15 câu Dev (q01 đến q15)** và **5 câu Test (q16 đến q20)**. Phân chia độc lập và cố định trước khi chạy pipeline.
  - *Câu hỏi kiểm tra Metadata Filter:* Có **3 câu có filter** (2 câu thuộc Dev: `q08`, `q11`; 1 câu thuộc Test: `q19`).
  - *Cách kiểm chứng Evidence:* 100% các câu hỏi đều có trường `evidence_quote` là đoạn trích nguyên văn từ nội dung đã trích xuất của `gold_page`. Script kiểm thử tự động đã xác nhận chuỗi con bằng chứng tồn tại chính xác tại trang nguồn.

- **Tiêu chí chọn chiến lược đã chốt trước khi xem test:**
  - Tiêu chí ưu tiên số 1: **Retrieval Accuracy (Evidence Hit@3)** trên tập Dev phải đạt tối thiểu $\ge 90\%$.
  - Tiêu chí ưu tiên số 2: **Tính mạch lạc của Chunk (Chunk Coherence)** trung bình phải đạt $\ge 1.5/2.0$ để AI Agent khi đọc context không bị đứt câu hay hiểu sai chủ thể.
  - Tiêu chí ưu tiên số 3: **Tuân thủ bộ lọc Metadata (Filter Compliance)** đạt $100\%$ khi có yêu cầu lọc phạm vi.
  - Tiêu chí ưu tiên số 4: **Hiệu quả tài nguyên (Tối ưu số lượng chunk và thời gian ingest)**.

---

## Kết quả

### Bảng 1: Hiệu năng Truy xuất và Tài nguyên Pipeline

| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian | Chi phí |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **A (Fixed-size)** | Dev | 10/15 (66.7%) | 12/15 (80.0%) | 116 | 88.02s | $0.00 |
| **A (Fixed-size)** | Test | 3/5 (60.0%) | 3/5 (60.0%) | 116 | - | $0.00 |
| **B (Paragraph)** | Dev | 13/15 (86.7%) | 15/15 (100.0%) | 70 | 55.87s | $0.00 |
| **B (Paragraph)** | Test | 5/5 (100.0%) | 5/5 (100.0%) | 70 | - | $0.00 |
| **C (Paragraph + Filter)** | Dev | 13/15 (86.7%) | 15/15 (100.0%) | 70 | 55.87s | $0.00 |
| **C (Paragraph + Filter)** | Test | 5/5 (100.0%) | 5/5 (100.0%) | 70 | - | $0.00 |

### Bảng 2: Đánh giá Thủ công 5 Khía cạnh Chất lượng

| Strategy | Coherence trung bình /2 (n=10) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 (n=5) |
|---|:---:|:---:|:---:|:---:|
| **A (Fixed-size)** | 0.50 / 2.0 (10) | 15/15 (100.0%) | N/A (Không lọc) | 0 câu mức 0, 2 câu mức 1, 3 câu mức 2 $\rightarrow$ **1.60 / 2.0** |
| **B (Paragraph)** | **2.00 / 2.0** (10) | 15/15 (100.0%) | N/A (Không lọc) | 0 câu mức 0, 0 câu mức 1, 5 câu mức 2 $\rightarrow$ **2.00 / 2.0** |
| **C (Paragraph + Filter)** | **2.00 / 2.0** (10) | 15/15 (100.0%) | **1/1 (100.0%) [Test]**<br>*(2/2 trên Dev)* | 0 câu mức 0, 0 câu mức 1, 5 câu mức 2 $\rightarrow$ **2.00 / 2.0** |

- **Đường dẫn trace, nhãn thủ công và cách chọn mẫu:**
  - *Dữ liệu trace chi tiết:* [results/traces_strategy_a.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/traces_strategy_a.json), [results/traces_strategy_b.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/traces_strategy_b.json), [results/traces_strategy_c.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/traces_strategy_c.json).
  - *Nhật ký thí nghiệm tổng hợp:* [artifacts/experiment_log.csv](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/artifacts/experiment_log.csv) và [results/benchmark_summary.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/benchmark_summary.json).
  - *Bảng nhãn audit thủ công:* [results/audit_report.json](file:///C:/Users/Thao/Downloads/K5-L3A-DAY06-LeSongThao-2A202603534-DataIngestion/results/audit_report.json).
  - *Cách chọn mẫu Coherence:* Chọn cố định 10 vị trí trang trải dài cả 4 chương (Trang 3, 5, 8, 11, 13, 16, 21, 24, 28, 30) trước khi chạy chấm điểm để đảm bảo tính khách quan không thiên vị.
  - *Cách chọn mẫu Metadata & Grounding:* Đánh giá trên toàn bộ 5 câu hỏi của tập Test độc lập (q16 $\rightarrow$ q20) với $5 \times 3 = 15$ chunks thuộc Top-3.

---

## Phân tích và kết luận

### 1. So sánh Chiến lược A – B và B – C

- **Tác động của Chunking (A vs B):**
  - Chiến lược A (cắt cứng 500 ký tự) tạo ra tới **116 chunks** (nhiều hơn 65.7% so với Chiến lược B chỉ có 70 chunks), dẫn đến thời gian tạo embedding lâu hơn đáng kể (88.02s so với 55.87s).
  - Nghiêm trọng hơn, việc cắt cố định theo số ký tự gây ra hiện tượng **"gãy ranh giới ngữ nghĩa" (semantic boundary fragmentation)**: Các câu văn, bảng số liệu hoặc điều kiện bị cắt làm đôi ở ranh giới giữa hai chunk. Kết quả là Hit@3 của Chiến lược A giảm xuống chỉ còn **80% trên Dev** và **60% trên Test** (bỏ lỡ bằng chứng do câu bị cắt mất một nửa).
  - Ngược lại, Chiến lược B phân chia theo ranh giới đoạn văn/điều khoản logic giúp bảo tồn 100% tính nguyên vẹn của câu văn, đạt điểm Coherence tuyệt đối $2.0/2.0$ và đưa Hit@3 lên **100% trên cả tập Dev và tập Test**.

- **Tác động của Metadata Filter (B vs C):**
  - Khác biệt duy nhất giữa B và C là bộ lọc metadata. Ở tập Test nhỏ gồm các câu hỏi rõ nghĩa, cả B và C đều đạt Hit@3 là 100%.
  - Tuy nhiên, sự khác biệt nằm ở **tính tinh khiết của không gian tìm kiếm (Search Space Purity)**: Với câu hỏi `q19` (chuẩn điểm thi MOS), Chiến lược C kích hoạt `where={"section": "tot_nghiep_khen_thuong"}`. Điều này đảm bảo $100\%$ các chunks trong Top-3 đều thuộc đúng Chương IV về chuẩn đầu ra tốt nghiệp, ngăn chặn hoàn toàn việc các chunks ở Chương I (thang điểm thi giữa kỳ) bị kéo vào top-3 do có cùng các từ khóa "điểm số", "bài thi".

### 2. Hai ví dụ sai điển hình (Failure Analysis)

- **Ví dụ lỗi 1 — Câu `q01` (Tập Dev, Trang 3):**
  - *Câu hỏi:* "Thời gian đào tạo tiêu chuẩn đối với sinh viên khối ngành Kỹ thuật - Công nghệ là bao nhiêu năm?"
  - *Evidence chuẩn:* `"Đối với khối ngành Kỹ thuật - Công nghệ là 4,0 năm (tương đương 8 học kỳ chính)"`
  - *Chiến lược A thất bại:* Cửa sổ 500 ký tự của chunk `so-tay-sinh-vien-2024_p3_fix_001` kết thúc ngay tại cụm từ "...(bao gồm..." và chunk kế tiếp `so-tay-sinh-vien-2024_p3_fix_002` bắt đầu bằng `"ngành Kỹ thuật - Công nghệ là 4,0 năm..."`. Cụm từ `"Đối với khối"` bị cắt nằm ở chunk trước, còn phần vị ngữ nằm ở chunk sau. Do bằng chứng bị chia cắt ngang xương sống câu văn, không có chunk nào chứa trọn vẹn evidence quote $\rightarrow$ Hit@3 = False.
  - *Chiến lược B thành công:* Chunk `so-tay-sinh-vien-2024_p3_para_000` gom trọn vẹn toàn bộ Điều 2: Kế hoạch và thời gian đào tạo, chứa đầy đủ cả chủ ngữ và vị ngữ $\rightarrow$ Hit@1 = True.

- **Ví dụ lỗi 2 — Câu `q20` (Tập Test, Trang 30):**
  - *Câu hỏi:* "Trường hợp nào sinh viên có kết quả học tập loại Xuất sắc hoặc Giỏi bị hạ một bậc xếp loại tốt nghiệp?"
  - *Evidence chuẩn:* `"Có khối lượng tín chỉ của các học phần phải thi lại hoặc học lại vượt quá 5% tổng số tín chỉ quy định cho toàn bộ chương trình đào tạo của ngành học"`
  - *Chiến lược A thất bại:* Chunk `so-tay-sinh-vien-2024_p30_fix_001` chỉ chứa phần đầu `"2. Các trường hợp bị hạ một bậc xếp loại tốt nghiệp: Hạng tốt nghiệp của n..."` rồi bị đứt. Chunk tiếp theo `fix_002` bắt đầu bằng `"hần phải thi lại hoặc học lại vượt quá 5% tổng số tín chỉ..."`. Người đọc hoặc AI nếu chỉ nhìn vào Top-1 của Chiến lược A sẽ không thể hiểu chủ thể của quy định hạ bậc là ai.
  - *Chiến lược B & C thành công:* Toàn bộ Khoản 2 Điều 31 về 2 trường hợp hạ bậc (học lại quá 5% tín chỉ hoặc bị cảnh cáo cấp trường) nằm trọn vẹn trong một chunk $\rightarrow$ Grounding đạt điểm tối đa 2/2.

### 3. Chiến lược được chọn, đánh đổi và điều kiện áp dụng

- **Chiến lược được lựa chọn:** **Chiến lược C (Paragraph-based Chunking kết hợp Metadata Filter)**.
- **Lý do lựa chọn:**
  1. Đáp ứng toàn diện mọi tiêu chí đã chốt trước thử nghiệm: Hit@3 đạt $100\%$, Coherence đạt $2.0/2.0$, Grounding đạt $2.0/2.0$, tuân thủ filter $100\%$.
  2. Tiết kiệm tài nguyên: Giảm số lượng chunk từ 116 xuống 70 chunks (giảm $39.6\%$ dung lượng index vector và thời gian gọi API embedding).
- **Đánh đổi (Trade-offs):**
  - Cần chi phí công sức tiền xử lý cao hơn: Cần viết parser phân tích cấu trúc tài liệu (`by_paragraph`) thay vì chỉ dùng phép trượt chuỗi đơn giản (`fixed_size`).
  - Phụ thuộc vào chất lượng metadata: Nếu metadata gán nhãn sai hoặc query của người dùng không trích xuất được filter đúng, việc lọc cứng có thể gây loại bỏ nhầm tài liệu liên quan (False Negative). Do đó, chỉ áp dụng filter khi giá trị metadata được xác định rõ ràng từ ngữ cảnh truy vấn.

### 4. Hạn chế của nghiên cứu

- *Quy mô tập Test:* Tập Test gồm 5 câu là đại diện tiêu biểu để kiểm thử tại chỗ trong phạm vi lab 4 giờ; chưa đủ lớn để đưa ra kết luận thống kê suy rộng cho mọi thể loại văn bản khác ngoài thể loại văn bản quy chế.
- *Đo lường thời gian và chi phí:* Tốc độ gọi API phụ thuộc vào độ trễ mạng Internet và cơ chế điều tiết băng thông (rate limit) của provider bên ngoài; chi phí ghi nhận $0.00$ là do dữ liệu nằm trọn trong hạn mức miễn phí hàng tháng của Gemini.

### 5. Đề xuất cải tiến và mở rộng

Nếu tiếp tục mở rộng dự án trong tương lai, các hướng nâng cấp ưu tiên bao gồm:
1. **Hybrid Retrieval (Dense + BM25):** Kết hợp vector embedding của Gemini với bộ lọc từ khóa BM25 để xử lý hoàn hảo các câu hỏi chứa mã học phần hoặc từ viết tắt chuyên biệt (ví dụ: "IC3", "MOS", "TOEIC", "GPA", "VSTEP").
2. **Contextual Retrieval / Title Prepending:** Tự động gắn tên Chương và số hiệu Điều khoản vào đầu mỗi chunk trước khi embed (ví dụ: `[Chương IV - Điều 31: Xếp loại tốt nghiệp] ...`) để chunk vừa giữ được tính cục bộ vừa mang đầy đủ bối cảnh toàn cục của tài liệu.
