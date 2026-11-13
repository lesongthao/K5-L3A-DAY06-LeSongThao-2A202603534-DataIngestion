"""Evaluate retrieved evidence and preserve complete per-query traces.
Calculates Hit@1, Evidence Hit@3, and filter compliance.
Preserves FULL chunk text and source metadata for 100% auditability.
"""
from typing import Any
import unicodedata


def normalize_whitespace(text: str) -> str:
    """Normalize Unicode (NFC) and whitespace for robust evidence matching."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", text)
    return " ".join(norm.split()).lower()


def is_evidence_hit(hit: dict[str, Any], question: dict[str, Any]) -> bool:
    """Check if the hit matches gold document_id, gold page and contains sufficient evidence.
    
    Verifies that all required evidence quotes supporting the answer exist in the chunk.
    """
    gold_source_id = question.get("gold_source_id")
    gold_page = question.get("gold_page")
    
    hit_metadata = hit.get("metadata", {})
    hit_source_id = hit_metadata.get("document_id")
    hit_page = hit_metadata.get("page")
    
    # 1. Check gold document_id match
    if not gold_source_id or str(hit_source_id) != str(gold_source_id):
        return False

    # 2. Check gold page match
    if hit_page != gold_page:
        return False
        
    # 3. Check evidence quotes
    evidence_quote = question.get("evidence_quote", "")
    evidence_quotes = question.get("evidence_quotes", [])
    if not evidence_quotes and evidence_quote:
        evidence_quotes = [evidence_quote]
        
    if not evidence_quotes or any(not normalize_whitespace(eq) for eq in evidence_quotes):
        return False
        
    norm_doc = normalize_whitespace(hit.get("text", ""))
    
    # Check that ALL required evidence quotes are present in the chunk text
    for eq in evidence_quotes:
        norm_eq = normalize_whitespace(eq)
        if norm_eq not in norm_doc:
            return False
            
    return True


def check_filter_compliance(hits: list[dict[str, Any]], expected_filter: dict[str, Any] | None) -> bool:
    """Check if all returned top-k hits comply with the query filter."""
    if not expected_filter:
        return True
    if not hits:
        return False
        
    for hit in hits:
        metadata = hit.get("metadata", {})
        for k, v in expected_filter.items():
            if str(metadata.get(k)) != str(v):
                return False
    return True


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate a single question against its retrieved top-k hits and build full trace."""
    hits_detail: list[dict[str, Any]] = []
    has_hit_at_1 = False
    has_hit_at_3 = False
    
    for rank, hit in enumerate(hits):
        hit_is_valid = is_evidence_hit(hit, question)
        if rank == 0 and hit_is_valid:
            has_hit_at_1 = True
        if hit_is_valid:
            has_hit_at_3 = True

        hit_meta = hit.get("metadata", {})
        hits_detail.append({
            "rank": rank + 1,
            "chunk_id": hit.get("chunk_id"),
            "score": hit.get("score"),
            "distance": hit.get("distance"),
            "document_id": hit_meta.get("document_id"),
            "source": hit_meta.get("source"),
            "page": hit_meta.get("page"),
            "section": hit_meta.get("section"),
            "year": hit_meta.get("year"),
            "chunk_strategy": hit_meta.get("chunk_strategy"),
            "chunk_size": len(hit.get("text", "")),
            "is_evidence_hit": hit_is_valid,
            # Preserving FULL text as required by GUIDE
            "text": hit.get("text", "")
        })

    filter_req = question.get("filter")
    is_filter_compliant = check_filter_compliance(hits, filter_req) if filter_req else None

    trace = {
        "id": question.get("id"),
        "split": question.get("split"),
        "type": question.get("type"),
        "question": question.get("question"),
        "gold_source_id": question.get("gold_source_id"),
        "gold_page": question.get("gold_page"),
        "evidence_quote": question.get("evidence_quote"),
        "evidence_quotes": question.get("evidence_quotes", [question.get("evidence_quote")] if question.get("evidence_quote") else []),
        "expected_answer": question.get("expected_answer"),
        "filter": filter_req,
        "hit_at_1": has_hit_at_1,
        "hit_at_3": has_hit_at_3,
        "filter_compliant": is_filter_compliant,
        "hits": hits_detail
    }
    return trace


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate Hit@1, Evidence Hit@3, and filter compliance by split and overall."""
    splits = ["dev", "test", "overall"]
    summary: dict[str, Any] = {}

    for s in splits:
        if s == "overall":
            subset = traces
        else:
            subset = [t for t in traces if t.get("split") == s]

        total = len(subset)
        if total == 0:
            continue

        hit1_count = sum(1 for t in subset if t.get("hit_at_1"))
        hit3_count = sum(1 for t in subset if t.get("hit_at_3"))

        filter_subset = [t for t in subset if t.get("filter") is not None]
        filter_total = len(filter_subset)
        filter_compliant_count = sum(1 for t in filter_subset if t.get("filter_compliant"))

        summary[s] = {
            "total_queries": total,
            "hit_at_1": f"{hit1_count}/{total}",
            "hit_at_1_rate": round(hit1_count / total, 4),
            "hit_at_3": f"{hit3_count}/{total}",
            "hit_at_3_rate": round(hit3_count / total, 4),
            "filter_compliance": f"{filter_compliant_count}/{filter_total}" if filter_total > 0 else "N/A",
            "filter_compliance_rate": round(filter_compliant_count / filter_total, 4) if filter_total > 0 else None
        }

    return summary
