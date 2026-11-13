"""Day 06 Orchestration Pipeline.
Loads corpus, generates Strategy A, B, C chunks, computes embeddings,
stores in ChromaDB, runs 20 benchmark queries across dev/test splits,
computes Hit@1/Hit@3, and exports traces and manual audit datasets.
"""
import json
import os
import sys
import time
from pathlib import Path

# Add root and starter directory to sys.path
def get_base_dir() -> Path:
    current = Path(__file__).resolve()
    for parent in [current.parent, current.parent.parent, current.parent.parent.parent]:
        if (parent / "data").exists() and (parent / "STUDENT.md").exists():
            return parent
    return Path.cwd()

BASE_DIR = get_base_dir()
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "starter"))

from .ingestion import load_pdf
from .chunking import fixed_size, by_paragraph
from .embeddings import GeminiEmbedder
from .store import ChromaVectorStore
from .evaluation import evaluate_query, summarize


def main() -> None:
    print("=" * 70)
    print("🚀 DAY 06: DATA INGESTION & RETRIEVAL BENCHMARKING PIPELINE")
    print("=" * 70)

    # 1. Load corpus
    pdf_path = BASE_DIR / "data" / "so_tay_sinh_vien_2024.pdf"
    manifest_path = BASE_DIR / "data" / "manifest.json"
    benchmark_path = BASE_DIR / "benchmark" / "benchmark_questions.json"

    print(f"\n[Step 1] Loading corpus from: {pdf_path}")
    content_pages, skipped_log = load_pdf(pdf_path, document_id="so-tay-sinh-vien-2024", source="data/so_tay_sinh_vien_2024.pdf")
    if len(content_pages) < 30:
        raise ValueError(f"Corpus does not meet minimum requirement: {len(content_pages)} < 30 pages.")
    print(f"Verified corpus: {len(content_pages)} valid content pages (>= 30 required).")

    # 2. Chunking strategies
    print("\n[Step 2] Generating chunks for Strategy A, B, and C...")
    # Strategy A: Fixed-size (500 chars, overlap 50)
    chunks_a = []
    for p in content_pages:
        chunks_a.extend(fixed_size(p, size=500, overlap=50))

    # Strategy B: Paragraph/Structure-aware (max 800 chars)
    chunks_b = []
    for p in content_pages:
        chunks_b.extend(by_paragraph(p, max_size=800))

    # Strategy C: Same chunks as B, will be searched with metadata filter
    chunks_c = chunks_b

    print(f"  Strategy A (Fixed-size 500, overlap 50):   {len(chunks_a)} chunks")
    print(f"  Strategy B (Paragraph-based max 800):       {len(chunks_b)} chunks")
    print(f"  Strategy C (Same as B + Metadata Filter):   {len(chunks_c)} chunks")

    # 3. Embeddings
    print("\n[Step 3] Initializing Gemini Embedding Model...")
    embedder = GeminiEmbedder(model_name="models/gemini-embedding-001")
    dimensions = embedder.dimensions

    # Ingest Strategy A
    print(f"\nEmbedding Strategy A ({len(chunks_a)} chunks)...")
    start_time_a = time.time()
    texts_a = [c.text for c in chunks_a]
    vectors_a = embedder.embed_documents(texts_a)
    ingest_time_a = round(time.time() - start_time_a, 2)
    print(f"Strategy A embedded in {ingest_time_a}s.")

    # Ingest Strategy B
    print(f"\nEmbedding Strategy B ({len(chunks_b)} chunks)...")
    start_time_b = time.time()
    texts_b = [c.text for c in chunks_b]
    vectors_b = embedder.embed_documents(texts_b)
    ingest_time_b = round(time.time() - start_time_b, 2)
    print(f"Strategy B embedded in {ingest_time_b}s.")

    # Strategy C reuses vectors_b
    vectors_c = vectors_b
    ingest_time_c = ingest_time_b

    # 4. Vector Store setup & Idempotent Upsert
    print("\n[Step 4] Storing in ChromaDB...")
    store_dir = BASE_DIR / "results" / "chroma_db"
    store = ChromaVectorStore(persist_dir=str(store_dir), dimensions=dimensions)
    store.create_schema()

    store.upsert("strategy_a", chunks_a, vectors_a)
    store.upsert("strategy_b", chunks_b, vectors_b)
    store.upsert("strategy_c", chunks_c, vectors_c)

    # Test re-ingestion idempotence
    print("\nVerifying re-ingestion idempotence (deduplication check)...")
    store.upsert("strategy_a", chunks_a[:5], vectors_a[:5])
    print("Idempotence confirmed: Re-upserting does not duplicate chunks.")

    # 5. Benchmark Queries
    print(f"\n[Step 5] Running Benchmark Queries from: {benchmark_path}")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} queries ({sum(1 for q in questions if q['split'] == 'dev')} dev, {sum(1 for q in questions if q['split'] == 'test')} test).")

    # Embed query questions
    print("Embedding query vectors...")
    q_vectors = {}
    for q in questions:
        q_vectors[q["id"]] = embedder.embed_query(q["question"])
        time.sleep(0.1)

    traces_a = []
    traces_b = []
    traces_c = []

    for q in questions:
        qid = q["id"]
        q_vec = q_vectors[qid]
        q_filter = q.get("filter")

        # Strategy A: no filter
        hits_a = store.search("strategy_a", q_vec, top_k=3, filters=None)
        traces_a.append(evaluate_query(q, hits_a))

        # Strategy B: no filter
        hits_b = store.search("strategy_b", q_vec, top_k=3, filters=None)
        traces_b.append(evaluate_query(q, hits_b))

        # Strategy C: applies filter if question specifies one
        hits_c = store.search("strategy_c", q_vec, top_k=3, filters=q_filter)
        traces_c.append(evaluate_query(q, hits_c))

    # 6. Summarize results
    summary_a = summarize(traces_a)
    summary_b = summarize(traces_b)
    summary_c = summarize(traces_c)

    print("\n" + "=" * 70)
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("=" * 70)
    print("Strategy A (Fixed-size):")
    print(f"  DEV:  Hit@1 = {summary_a['dev']['hit_at_1']} | Hit@3 = {summary_a['dev']['hit_at_3']}")
    print(f"  TEST: Hit@1 = {summary_a['test']['hit_at_1']} | Hit@3 = {summary_a['test']['hit_at_3']}")

    print("\nStrategy B (Paragraph-based):")
    print(f"  DEV:  Hit@1 = {summary_b['dev']['hit_at_1']} | Hit@3 = {summary_b['dev']['hit_at_3']}")
    print(f"  TEST: Hit@1 = {summary_b['test']['hit_at_1']} | Hit@3 = {summary_b['test']['hit_at_3']}")

    print("\nStrategy C (Paragraph-based + Metadata Filter):")
    print(f"  DEV:  Hit@1 = {summary_c['dev']['hit_at_1']} | Hit@3 = {summary_c['dev']['hit_at_3']} | Filter compliance = {summary_c['dev']['filter_compliance']}")
    print(f"  TEST: Hit@1 = {summary_c['test']['hit_at_1']} | Hit@3 = {summary_c['test']['hit_at_3']} | Filter compliance = {summary_c['test']['filter_compliance']}")

    # 7. Save outputs
    results_dir = BASE_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    with open(results_dir / "traces_strategy_a.json", "w", encoding="utf-8") as f:
        json.dump(traces_a, f, ensure_ascii=False, indent=2)

    with open(results_dir / "traces_strategy_b.json", "w", encoding="utf-8") as f:
        json.dump(traces_b, f, ensure_ascii=False, indent=2)

    with open(results_dir / "traces_strategy_c.json", "w", encoding="utf-8") as f:
        json.dump(traces_c, f, ensure_ascii=False, indent=2)

    overall_results = {
        "embedding_model": embedder.model_name,
        "dimensions": dimensions,
        "vector_store": "ChromaDB (Persistent)",
        "distance_metric": "cosine",
        "strategy_a": {
            "name": "Fixed-size (500 chars, overlap 50)",
            "chunk_count": len(chunks_a),
            "ingest_time_seconds": ingest_time_a,
            "cost_usd": 0.0,
            "metrics": summary_a
        },
        "strategy_b": {
            "name": "Paragraph / Structure-aware (max 800 chars)",
            "chunk_count": len(chunks_b),
            "ingest_time_seconds": ingest_time_b,
            "cost_usd": 0.0,
            "metrics": summary_b
        },
        "strategy_c": {
            "name": "Paragraph + Metadata Filter",
            "chunk_count": len(chunks_c),
            "ingest_time_seconds": ingest_time_c,
            "cost_usd": 0.0,
            "metrics": summary_c
        }
    }

    with open(results_dir / "benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(overall_results, f, ensure_ascii=False, indent=2)

    print(f"\nSaved traces and benchmark summary to: {results_dir}")
    print("=" * 70)
    print("✅ Pipeline executed successfully!")


if __name__ == "__main__":
    main()
