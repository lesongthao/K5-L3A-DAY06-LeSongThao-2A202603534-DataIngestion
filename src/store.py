"""Persistent Vector Store implementation using ChromaDB on disk.
Fully supports persistent storage, cosine similarity search, and metadata filtering.
Guarantees idempotence (re-ingestion deduplication) and cleans obsolete chunks
when a document version changes or reduces in chunk count.
"""
from pathlib import Path
import math
from typing import Any
import chromadb
from chromadb.config import Settings
from .models import Chunk


class ChromaVectorStore:
    """Persistent local vector store backed by ChromaDB with cosine distance."""

    def __init__(self, persist_dir: str = "./results/chroma_db", dimensions: int = 3072) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.dimensions = dimensions
        self.client = chromadb.PersistentClient(path=str(self.persist_dir), settings=Settings(anonymized_telemetry=False))
        self.collections: dict[str, Any] = {}
        print(f"Initialized ChromaVectorStore at: {self.persist_dir} (dimensions={dimensions})")

    def create_schema(self) -> None:
        """Create or get collections for strategies with cosine similarity space."""
        for strategy in ["strategy_a", "strategy_b", "strategy_c"]:
            collection = self.client.get_or_create_collection(
                name=strategy,
                metadata={"hnsw:space": "cosine"}
            )
            self.collections[strategy] = collection
        print("Created schema/collections for strategy_a, strategy_b, strategy_c.")

    def _get_collection(self, strategy: str):
        strat_key = strategy if strategy.startswith("strategy_") else f"strategy_{strategy.lower()}"
        if strat_key not in self.collections:
            self.collections[strat_key] = self.client.get_or_create_collection(
                name=strat_key,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[strat_key]

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Validate lengths and dimensions, write stable IDs without duplicates.
        
        Guarantees idempotency and obsolete chunk removal:
        - Overwrites chunks with identical chunk_id.
        - Identifies and deletes older chunks belonging to the same document_id
          that are no longer present in the updated chunk list.
        """
        if len(chunks) != len(vectors):
            raise ValueError(f"Length mismatch: {len(chunks)} chunks vs {len(vectors)} vectors.")

        if not chunks:
            return

        collection = self._get_collection(strategy)

        # Validate vector dimensions
        for i, vec in enumerate(vectors):
            if len(vec) != self.dimensions or not all(math.isfinite(x) for x in vec):
                raise ValueError(
                    f"Vector {i} dimension mismatch: expected {self.dimensions}, got {len(vec)}"
                )

        ids = [c.chunk_id for c in chunks]
        if len(ids) != len(set(ids)) or any(not c.chunk_id or not c.document_id or not c.text.strip() for c in chunks):
            raise ValueError("Chunk IDs must be unique; IDs and text must be nonempty")
        documents = [c.text for c in chunks]
        new_ids_set = set(ids)
        
        # Flatten metadata for Chroma compatibility (strings, ints, floats, bools)
        metadatas = []
        for c in chunks:
            meta = {
                "chunk_id": str(c.chunk_id),
                "document_id": str(c.document_id),
                "source": str(c.source),
                "page": int(c.page),
                "section": str(c.metadata.get("section", "unknown")),
                "year": int(c.metadata.get("year", 2024)),
                "chunk_strategy": str(c.metadata.get("chunk_strategy", strategy))
            }
            metadatas.append(meta)

        # Batch upsert in chunks of 50 to avoid memory spikes
        batch_size = 50
        for i in range(0, len(ids), batch_size):
            b_ids = ids[i:i + batch_size]
            b_docs = documents[i:i + batch_size]
            b_vecs = vectors[i:i + batch_size]
            b_metas = metadatas[i:i + batch_size]
            collection.upsert(
                ids=b_ids,
                documents=b_docs,
                embeddings=b_vecs,
                metadatas=b_metas
            )

        # Delete stale IDs only after all input validation and new writes succeed.
        for doc_id in {c.document_id for c in chunks}:
            existing = collection.get(where={"document_id": doc_id})
            obsolete_ids = [cid for cid in existing["ids"] if cid not in new_ids_set]
            if obsolete_ids:
                collection.delete(ids=obsolete_ids)
                print(f"[{strategy}] Cleaned up {len(obsolete_ids)} obsolete chunks for document '{doc_id}'.")

        print(f"[{strategy}] Upserted {len(chunks)} chunks successfully. Total in collection: {collection.count()}")

    def search(
        self,
        strategy: str,
        query_vector: list[float],
        top_k: int = 3,
        filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Filter metadata, rank by cosine similarity, and return top-k hits."""
        if not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")
        if len(query_vector) != self.dimensions or not all(math.isfinite(x) for x in query_vector):
            raise ValueError(
                f"Query vector dimension mismatch: expected {self.dimensions}, got {len(query_vector)}"
            )

        collection = self._get_collection(strategy)
        where_filter = filters if filters else None

        # Query using vector embedding
        query_args: dict[str, Any] = {
            "query_embeddings": [query_vector],
            "n_results": top_k
        }
        if where_filter:
            query_args["where"] = where_filter

        results = collection.query(**query_args)

        hits: list[dict[str, Any]] = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for rank in range(len(results["ids"][0])):
                chunk_id = results["ids"][0][rank]
                doc_text = results["documents"][0][rank] if results["documents"] else ""
                metadata = results["metadatas"][0][rank] if results["metadatas"] else {}
                distance = results["distances"][0][rank] if results.get("distances") else 0.0
                
                # Cosine distance d in [0, 2] -> similarity = 1 - d
                similarity_score = round(1.0 - distance, 4)
                
                hits.append({
                    "chunk_id": chunk_id,
                    "text": doc_text,
                    "score": similarity_score,
                    "distance": round(distance, 4),
                    "metadata": metadata
                })

        return hits


# Alias for compatibility if needed
PgVectorStore = ChromaVectorStore
