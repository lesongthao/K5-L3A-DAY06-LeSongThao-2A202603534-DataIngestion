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

        self.client = genai.Client(api_key=self.api_key)
        # Validate dimensions dynamically
        test_resp = self._embed_single("Xin chào")
        self.dimensions = len(test_resp)
        print(f"Initialized GeminiEmbedder: model={self.model_name}, dimensions={self.dimensions}")

    def _embed_single(self, text: str) -> list[float]:
        """Embed a single string with retry on rate limit."""
        max_retries = 5
        base_delay = 2.0
        for attempt in range(max_retries):
            try:
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text
                )
                return response.embeddings[0].values
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    delay = base_delay * (2 ** attempt)
                    print(f"Rate limited (429). Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(delay)
                else:
                    raise e
        raise RuntimeError(f"Failed to embed after {max_retries} retries due to rate limiting.")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents, respecting API rate limits with small batches."""
        results: list[list[float]] = []
        batch_size = 5
        total = len(texts)

        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                vector = self._embed_single(text)
                results.append(vector)
                time.sleep(0.3)  # Gentle delay to avoid RPM spikes
            if (i + batch_size) < total:
                print(f"  Embedded {min(i + batch_size, total)}/{total} chunks...")

        return results

    def embed_query(self, question: str) -> list[float]:
        """Embed a query text with semantic search semantics."""
        return self._embed_single(question)
