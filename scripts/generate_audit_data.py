"""Replay stored audit labels and verify metadata; never invent human labels."""
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.ingestion import load_pdf
from src.run import build_audit_report


def main():
    pdf_path = BASE_DIR / "data" / "so_tay_sinh_vien_2024.pdf"
    pages, _ = load_pdf(pdf_path, "so-tay-sinh-vien-2024", "data/so_tay_sinh_vien_2024.pdf")
    traces = [json.loads((BASE_DIR / "results" / f"traces_strategy_{s}.json").read_text(encoding="utf-8"))
              for s in "abc"]
    report = build_audit_report(pages, *traces, pdf_path)
    output = BASE_DIR / "results" / "audit_report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Audit regenerated from shared pipeline functions. Review status:", report["human_review_status"])


if __name__ == "__main__":
    main()
