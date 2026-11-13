"""Offline consistency checks; no embedding API and no result files are changed."""
import ast
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.chunking import by_paragraph, fixed_size
from src.evaluation import evaluate_query, normalize_whitespace, summarize
from src.ingestion import load_pdf
from src.run import build_audit_report


def read_json(relative):
    return json.loads((BASE_DIR / relative).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    for folder in ("src", "starter/src", "scripts", "demo"):
        for path in (BASE_DIR / folder).glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    pairs = [(path, BASE_DIR / "starter" / "src" / path.name)
             for path in (BASE_DIR / "src").glob("*.py")]
    pairs.extend((BASE_DIR / p, BASE_DIR / "starter" / p)
                 for p in ("data/manifest.json", "data/so_tay_sinh_vien_2024.pdf"))
    pairs.append((BASE_DIR / "benchmark/benchmark_questions.json",
                  BASE_DIR / "starter/data/benchmark_questions.json"))
    for source, mirror in pairs:
        require(mirror.exists() and source.read_bytes() == mirror.read_bytes(), f"Mirror differs: {mirror}")
    require({p.name for p in (BASE_DIR / 'src').glob('*.py')} ==
            {p.name for p in (BASE_DIR / 'starter/src').glob('*.py')}, 'Extra source mirror files')
    print(f"PASS: syntax and {len(pairs)} mirrored files")

    pdf_path = BASE_DIR / "data/so_tay_sinh_vien_2024.pdf"
    pages, skipped = load_pdf(pdf_path, "so-tay-sinh-vien-2024", "data/so_tay_sinh_vien_2024.pdf")
    manifest = read_json("data/manifest.json")
    require(len(pages) >= 30, "Fewer than 30 content pages")
    require(manifest["total_content_pages"] == len(pages), "Manifest page count")
    require(manifest["total_content_characters"] == sum(len(p.text) for p in pages), "Manifest characters")
    require(manifest["sha256"] == hashlib.sha256(pdf_path.read_bytes()).hexdigest(), "Corpus hash")
    require({p["page_number"]: p["character_count"] for p in manifest["content_pages"]} ==
            {p.page: len(p.text) for p in pages}, "Manifest page boundaries/counts")
    require(read_json("results/skipped_pages.json") == skipped, "Skipped-page log")

    questions = read_json("benchmark/benchmark_questions.json")
    by_id = {q["id"]: q for q in questions}
    splits = Counter(q["split"] for q in questions)
    require(len(by_id) == len(questions) >= 20 and splits["dev"] >= 15 and splits["test"] >= 5, "Benchmark split")
    filtered = [q for q in questions if q.get("filter")]
    require(len(filtered) >= 3 and any(q["split"] == "test" for q in filtered), "Filter coverage")
    by_page = {p.page: p for p in pages}
    for q in questions:
        quotes = q.get("evidence_quotes") or [q.get("evidence_quote")]
        text = normalize_whitespace(by_page[q["gold_page"]].text)
        require(all(normalize_whitespace(e) and normalize_whitespace(e) in text for e in quotes),
                f"Evidence missing: {q['id']}")
    print("PASS: corpus, manifest, skipped pages, evidence and dev/test split")

    summary = read_json("results/benchmark_summary.json")
    trace_sets = []
    for strategy in "abc":
        chunks = {c.chunk_id: c for p in pages
                  for c in (fixed_size(p) if strategy == "a" else by_paragraph(p))}
        require(summary[f"strategy_{strategy}"]["chunk_count"] == len(chunks), f"Chunk count {strategy}")
        limit = 500 if strategy == "a" else 800
        require(all(0 < len(c.text) <= limit for c in chunks.values()), f"Chunk size {strategy}")
        traces = read_json(f"results/traces_strategy_{strategy}.json")
        require([t['id'] for t in traces] == [q['id'] for q in questions], f"Trace query order {strategy}")
        rebuilt = []
        for trace in traces:
            q = by_id[trace["id"]]
            require(len(trace["hits"]) == 3, f"Top-3 missing: {strategy}/{q['id']}")
            hits = []
            for h in trace["hits"]:
                c = chunks[h["chunk_id"]]
                metadata = {"document_id": c.document_id, "source": c.source, "page": c.page, **c.metadata}
                require(h["text"] == c.text, f"Trace text: {strategy}/{q['id']}/{c.chunk_id}")
                require(all(h.get(k) == metadata[k] for k in ("document_id", "source", "page", "section", "year")),
                        f"Trace metadata: {strategy}/{q['id']}")
                hits.append({"chunk_id": c.chunk_id, "text": c.text, "metadata": metadata,
                             "score": h["score"], "distance": h.get("distance")})
            rebuilt_trace = evaluate_query(q, hits)
            require(rebuilt_trace == trace, f"Trace evaluation mismatch: {strategy}/{q['id']}")
            rebuilt.append(rebuilt_trace)
        require(summarize(rebuilt) == summary[f"strategy_{strategy}"]["metrics"], f"Metrics {strategy}")
        trace_sets.append(traces)
    print("PASS: 60 queries / 180 full-text hits, source metadata and all summary metrics")
    audit = read_json("results/audit_report.json")
    require(audit == build_audit_report(pages, *trace_sets, pdf_path), "Audit differs from shared generator")
    print("PASS: audit artifacts agree with pipeline and offline generator")

    with (BASE_DIR / "artifacts/experiment_log.csv").open(encoding="utf-8", newline="") as stream:
        log = {row["strategy"].lower(): row for row in csv.DictReader(stream)}
    for strategy in "abc":
        metrics = summary[f"strategy_{strategy}"]["metrics"]
        for split in ("dev", "test"):
            for k in (1, 3):
                require(log[strategy][f"{split}_hit{k}"] == metrics[split][f"hit_at_{k}"],
                        f"Experiment log metrics: {strategy}/{split}/hit{k}")
    for strategy in "ab":
        cost = summary["cost_accounting"][f"strategy_{strategy}"]
        require(cost["commercial_estimated_cost_usd"] == round(cost["approx_tokens"] * 0.15 / 1_000_000, 6),
                f"Cost estimate: {strategy}")
    print("PASS: experiment log and documented cost estimates")
    if audit.get("human_review_status") != "confirmed":
        print("REVIEW NEEDED: coherence/grounding labels require author confirmation; scripts cannot certify human review.")
    print("REVIEW NEEDED: test questions were reused after earlier results were inspected; see report limitations.")
    if "chưa chốt" in (BASE_DIR / "STUDENT.md").read_text(encoding="utf-8"):
        print("FINALIZE NEEDED: commit the reviewed changes, record the submission SHA and push before sharing the repository link.")
    print("Offline consistency checks passed. No provider calls or new retrieval run were performed.")


if __name__ == "__main__":
    main()
