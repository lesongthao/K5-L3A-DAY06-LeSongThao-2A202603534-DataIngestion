"""Test obsolete chunk cleanup upon re-ingestion.
Verifies that when a document with N chunks is re-ingested with M < N chunks,
the N-M obsolete chunks are cleanly deleted from ChromaDB.
"""
import sys
import tempfile
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from starter.src.chunking import Chunk
from starter.src.store import ChromaVectorStore


def test_obsolete_cleanup():
    temp_dir = tempfile.mkdtemp()
    try:
        store = ChromaVectorStore(persist_dir=temp_dir, dimensions=4)
        store.create_schema()

        # Step 1: Ingest 3 chunks for doc 'doc_1'
        chunks_v1 = [
            Chunk(chunk_id="doc_1_p1_000", document_id="doc_1", source="data/test.pdf", page=1, text="Chunk 1", metadata={"page": 1}),
            Chunk(chunk_id="doc_1_p1_001", document_id="doc_1", source="data/test.pdf", page=1, text="Chunk 2", metadata={"page": 1}),
            Chunk(chunk_id="doc_1_p1_002", document_id="doc_1", source="data/test.pdf", page=1, text="Chunk 3", metadata={"page": 1}),
        ]
        vecs_v1 = [[0.1, 0.2, 0.3, 0.4]] * 3
        store.upsert("strategy_a", chunks_v1, vecs_v1)

        coll = store._get_collection("strategy_a")
        assert coll.count() == 3, f"Expected 3 chunks, got {coll.count()}"
        print(f"Initial ingestion: {coll.count()} chunks in store.")

        # Step 2: Re-ingest with only 1 chunk for 'doc_1'
        chunks_v2 = [
            Chunk(chunk_id="doc_1_p1_000", document_id="doc_1", source="data/test.pdf", page=1, text="Chunk 1 modified", metadata={"page": 1}),
        ]
        vecs_v2 = [[0.15, 0.25, 0.35, 0.45]]
        store.upsert("strategy_a", chunks_v2, vecs_v2)

        count_after = coll.count()
        print(f"After re-ingestion with 1 chunk: {count_after} chunks in store.")
        assert count_after == 1, f"Expected 1 chunk after cleanup, got {count_after} (obsolete chunks remained!)"

        # Check remaining chunk ID
        remaining_ids = coll.get()["ids"]
        assert remaining_ids == ["doc_1_p1_000"], f"Unexpected remaining IDs: {remaining_ids}"
        print("PASS: Obsolete chunks were cleanly and idempotently removed!")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_obsolete_cleanup()
