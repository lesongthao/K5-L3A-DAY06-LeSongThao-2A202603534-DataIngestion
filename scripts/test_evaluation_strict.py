"""Strict evaluation verification script.
Tests that 100% of the 20 benchmark questions have their evidence_quote
verified character-by-character on the PDF physical page, and checks is_evidence_hit.
"""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import json
import pypdf
from starter.src.evaluation import is_evidence_hit, normalize_whitespace, check_filter_compliance

PDF_PATH = BASE_DIR / "data" / "so_tay_sinh_vien_2024.pdf"
BENCHMARK_PATH = BASE_DIR / "benchmark" / "benchmark_questions.json"


def test_strict_evidence():
    reader = pypdf.PdfReader(str(PDF_PATH))
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} queries from {BENCHMARK_PATH.name}")
    all_passed = True

    for q in questions:
        page_idx = q["gold_page"] - 1
        page_text = reader.pages[page_idx].extract_text()
        norm_page_text = normalize_whitespace(page_text)

        # Check evidence quotes
        quotes = q.get("evidence_quotes") or [q.get("evidence_quote")]
        for quote in quotes:
            norm_q = normalize_whitespace(quote)
            if norm_q not in norm_page_text:
                print(f"FAIL: Query {q['id']} quote not found on page {q['gold_page']}")
                print(f"  Missing: {quote[:80]}...")
                all_passed = False

        # Test is_evidence_hit matching
        mock_hit = {
            "id": f"test_p{q['gold_page']}_001",
            "text": page_text,
            "metadata": {
                "document_id": q["gold_source_id"],
                "page": q["gold_page"]
            }
        }
        if not is_evidence_hit(mock_hit, q):
            print(f"FAIL: is_evidence_hit returned False for valid gold hit in {q['id']}")
            all_passed = False

        # Test is_evidence_hit rejection of wrong document
        mock_wrong_doc = {
            "id": f"test_p{q['gold_page']}_001",
            "text": page_text,
            "metadata": {
                "document_id": "wrong-doc-id",
                "page": q["gold_page"]
            }
        }
        if is_evidence_hit(mock_wrong_doc, q):
            print(f"FAIL: is_evidence_hit accepted wrong document_id for {q['id']}")
            all_passed = False

        missing_doc = {"text": page_text, "metadata": {"page": q["gold_page"]}}
        if is_evidence_hit(missing_doc, q):
            raise AssertionError(f"Missing document_id accepted for {q['id']}")

        no_evidence = {**q, "evidence_quote": "", "evidence_quotes": []}
        if is_evidence_hit(mock_hit, no_evidence):
            raise AssertionError(f"Missing evidence accepted for {q['id']}")

        if len(quotes) > 1:
            partial_hit = {**mock_hit, "text": quotes[0]}
            if is_evidence_hit(partial_hit, q):
                raise AssertionError(f"Partial evidence accepted for {q['id']}")

    if check_filter_compliance([], {"section": "quy_che_dao_tao"}):
        raise AssertionError("Empty filtered results must not count as compliance")

    if all_passed:
        print("ALL 20 BENCHMARK EVIDENCE STRINGS VERIFIED 100% MATCH ON PDF!")
        print("is_evidence_hit strict verification passed successfully!")
    else:
        raise AssertionError("Strict evidence verification failed.")


if __name__ == "__main__":
    test_strict_evidence()
