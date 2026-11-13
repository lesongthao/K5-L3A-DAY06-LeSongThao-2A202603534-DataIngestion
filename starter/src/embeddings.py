"""Real embedding provider adapter using Google Gemini API (gemini-embedding-001).
Strictly adheres to the Embedder protocol; does NOT use mock/random vectors.
"""
import os
import time
from typing import Protocol
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
load_dotenv("starter/.env")


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class GeminiEmbedder:
    """Production embedder using Google GenAI API with retry and rate-limiting."""

    def __init__(self, model_name: str = "models/gemini-embedding-001", api_key: str | None = None) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")

        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=30000)
        )
        self._cache: dict[str, list[float]] = {}
        # Validate dimensions dynamically
        test_resp = self._embed_single("Xin chào")
        self.dimensions = len(test_resp)
        print(f"Initialized GeminiEmbedder: model={self.model_name}, dimensions={self.dimensions}", flush=True)

    def _embed_single(self, text: str) -> list[float]:
        """Embed a single string with retry on rate limit and network drops."""
        if text in self._cache:
            return self._cache[text]

        max_retries = 6
        base_delay = 2.0
        for attempt in range(max_retries):
            try:
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text
                )
                vec = response.embeddings[0].values
                self._cache[text] = vec
                return vec
            except Exception as e:
                err_msg = str(e)
                delay = base_delay * (2 ** attempt)
                print(f"Embedding transient error ({type(e).__name__}): {err_msg[:80]}. Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...", flush=True)
                time.sleep(delay)
                # Re-initialize client on connection drops
                if "RemoteProtocolError" in err_msg or "Connection" in err_msg or "httpcore" in err_msg or "Timeout" in err_msg:
                    try:
                        self.client = genai.Client(
                            api_key=self.api_key,
                            http_options=types.HttpOptions(timeout=30000)
                        )
                    except Exception:
                        pass

        raise RuntimeError(f"Failed to embed text after {max_retries} retries: {text[:60]}...")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents in batches with retry and caching."""
        uncached_indices = [i for i, t in enumerate(texts) if t not in self._cache]
        batch_size = 20
        total_uncached = len(uncached_indices)

        for b_start in range(0, total_uncached, batch_size):
            batch_idxs = uncached_indices[b_start:b_start + batch_size]
            batch_texts = [texts[idx] for idx in batch_idxs]

            max_retries = 5
            base_delay = 2.0
            success = False
            for attempt in range(max_retries):
                try:
                    response = self.client.models.embed_content(
                        model=self.model_name,
                        contents=batch_texts
                    )
                    for idx, emb in zip(batch_idxs, response.embeddings):
                        self._cache[texts[idx]] = emb.values
                    success = True
                    break
                except Exception as e:
                    err_msg = str(e)
                    delay = base_delay * (2 ** attempt)
                    print(f"Batch embedding error ({type(e).__name__}): {err_msg[:80]}. Retrying in {delay:.1f}s...", flush=True)
                    time.sleep(delay)
                    if "RemoteProtocolError" in err_msg or "Connection" in err_msg or "httpcore" in err_msg or "Timeout" in err_msg:
                        try:
                            self.client = genai.Client(
                                api_key=self.api_key,
                                http_options=types.HttpOptions(timeout=30000)
                            )
                        except Exception:
                            pass

            if not success:
                print("  Falling back to individual embedding for batch...", flush=True)
                for idx in batch_idxs:
                    self._embed_single(texts[idx])

            done = min(b_start + batch_size, total_uncached)
            print(f"  Embedded {done}/{total_uncached} uncached chunks (total {len(texts)} chunks)...", flush=True)
            time.sleep(0.5)

        return [self._cache[t] for t in texts]

    def embed_query(self, question: str) -> list[float]:
        """Embed a query text with semantic search semantics."""
        return self._embed_single(question)
