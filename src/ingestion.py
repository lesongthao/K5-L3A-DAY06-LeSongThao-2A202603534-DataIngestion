"""Read and normalize source data.
Extract each physical page; keep its page number, source, and metadata.
Detect and record pages with no text or non-content pages.
"""
from pathlib import Path
import unicodedata
import re
from typing import Any
import pypdf
from .models import DocumentPage


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFC) and whitespace without discarding useful structure."""
    if not text:
        return ""
    # 1. Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)
    # 2. Normalize Windows newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # 3. Replace non-breaking spaces
    text = text.replace("\u00a0", " ")
    # 4. Remove multiple spaces on the same line
    text = re.sub(r"[ \t]+", " ", text)
    # 5. Collapse excessive line breaks (more than 2 consecutive newlines to 2)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_section_for_page(page_num: int) -> str:
    """Classify section based on page ranges defined in manifest."""
    if 3 <= page_num <= 10:
        return "quy_che_dao_tao"
    elif 11 <= page_num <= 18:
        return "hoc_bong_hoc_phi"
    elif 19 <= page_num <= 26:
        return "cong_tac_sinh_vien"
    elif 27 <= page_num <= 34:
        return "tot_nghiep_khen_thuong"
    elif page_num == 35:
        return "phu_luc"
    else:
        return "tong_quan"


def load_pdf(path: Path, document_id: str, source: str) -> tuple[list[DocumentPage], list[dict[str, Any]]]:
    """Extract each physical page; keep its page number, source, and section metadata.

    Filters out non-content pages (Page 1: Bìa, Page 2: Mục lục, Page 35: Phụ lục).
    Returns (content_pages, skipped_pages_log).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {path}")

    reader = pypdf.PdfReader(str(path))
    content_pages: list[DocumentPage] = []
    skipped_log: list[dict[str, Any]] = []

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        raw_text = page.extract_text() or ""
        norm_text = normalize_text(raw_text)

        # Check for non-content or empty pages
        if page_num in [1, 2, 35] or len(norm_text) < 300:
            reason = "Trang bìa" if page_num == 1 else (
                "Lời nói đầu và Mục lục" if page_num == 2 else (
                    "Phụ lục tham chiếu" if page_num == 35 else "Văn bản rỗng / không đủ dung lượng"
                )
            )
            skipped_log.append({
                "page": page_num,
                "character_count": len(norm_text),
                "reason": reason
            })
            continue

        section = get_section_for_page(page_num)
        page_obj = DocumentPage(
            document_id=document_id,
            source=source,
            page=page_num,
            text=norm_text,
            metadata={
                "section": section,
                "year": 2024,
                "document_type": "handbook",
                "character_count": len(norm_text)
            }
        )
        content_pages.append(page_obj)

    print(f"Loaded {len(content_pages)} valid content pages (skipped {len(skipped_log)} non-content pages).")
    return content_pages, skipped_log
