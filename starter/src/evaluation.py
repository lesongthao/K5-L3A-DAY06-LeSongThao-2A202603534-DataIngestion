"""Evaluate retrieved evidence and preserve per-query traces.
Calculates Hit@1, Evidence Hit@3, and filter compliance.
"""
from typing import Any
import re


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for fuzzy substring matching."""
    return " ".join(text.split()).lower()


def is_evidence_hit(hit: dict[str, Any], question: dict[str, Any]) -> bool:
    """Check if the hit matches gold source/page and contains sufficient evidence quote."""
    gold_page = question.get("gold_page")
    hit_page = hit.get("metadata", {}).get("page")
    
    # Must match gold page
    if hit_page != gold_page:
        return False
        
    evidence_quote = question.get("evidence_quote", "")
    if not evidence_quote:
        return True
        
    norm_doc = normalize_whitespace(hit.get("text", ""))
    norm_evidence = normalize_whitespace(evidence_quote)
    
    # Check if evidence quote (or significant portion) is in chunk text
    return norm_evidence in norm_doc


def check_filter_compliance(hits: list[dict[str, Any]], expected_filter: dict[str, Any] | None) -> bool:
    """Check if all returned top-k hits comply with the query filter."""
    if not expected_filter or not hits:
        return True
        
    for hit in hits:
        metadata = hit.get("metadata", {})
        for k, v in expected_filter.items():
            if str(metadata.get(k)) != str(v):
                return False
    return True


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate a single question against its retrieved top-k hits and build trace."""
    hits_detail: list[dict[str, Any]] = []
    has_hit_at_1 = False
    has_hit_at_3 = False
    
    for rank, hit in enumerate(hits):
        hit_is_valid = is_evidence_hit(hit, question)
        if rank == 0 and hit_is_valid:
            has_hit_at_1 = True
        if hit_is_valid:
            has_hit_at_3 = True

        hits_detail.append({
            "rank": rank + 1,
            "chunk_id": hit.get("chunk_id"),
            "score": hit.get("score"),
            "page": hit.get("metadata", {}).get("page"),
            "section": hit.get("metadata", {}).get("section"),
            "is_evidence_hit": hit_is_valid,
            "text_snippet": hit.get("text", "")[:180] + ("..." if len(hit.get("text", "")) > 180 else "")
        })

    filter_req = question.get("filter")
    is_filter_compliant = check_filter_compliance(hits, filter_req) if filter_req else None

    trace = {
        "id": question.get("id"),
        "split": question.get("split"),
        "type": question.get("type"),
        "question": question.get("question"),
        "gold_page": question.get("gold_page"),
        "evidence_quote": question.get("evidence_quote"),
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
