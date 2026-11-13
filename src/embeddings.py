"""Gemini embeddings with bounded retries and credential-safe logging."""
import logging
import math
import os
from pathlib import Path
import time
from typing import Protocol

from dotenv import load_dotenv
from google import genai
from google.genai import types

LOGGER = logging.getLogger(__name__)
_root = next((p for p in Path(__file__).resolve().parents if (p / "STUDENT.md").is_file()), None)
if _root:
    for _env in (_root / ".env", _root / "starter/.env"):
        load_dotenv(_env, override=False)


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, question: str) -> list[float]: ...


class GeminiEmbedder:
    def __init__(self, model_name="models/gemini-embedding-001", api_key=None,
                 max_retries=3, timeout_ms=15000, validate_dimensions=True):
        if not 1 <= max_retries <= 6 or not 1000 <= timeout_ms <= 30000:
            raise ValueError("Invalid provider retry/timeout limits")
        self.model_name = model_name
        self.dimensions = 3072
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment or project .env")
        self.max_retries = max_retries
        self.client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(timeout=timeout_ms))
        self._cache = {}
        if validate_dimensions:
            self._embed_single("Xin chào")

    def _remember(self, text, vector):
        if text not in self._cache and len(self._cache) >= 256:
            self._cache.pop(next(iter(self._cache)))
        self._cache[text] = vector

    def _request(self, contents):
        expected = 1 if isinstance(contents, str) else len(contents)
        for attempt in range(self.max_retries):
            try:
                response = self.client.models.embed_content(model=self.model_name, contents=contents)
            except Exception as exc:
                code = getattr(exc, "code", None)
                transient = code in (408, 429, 500, 502, 503, 504) or type(exc).__name__ in (
                    "ConnectError", "ReadError", "RemoteProtocolError", "ReadTimeout", "ConnectTimeout", "TimeoutException")
                if not transient or attempt + 1 == self.max_retries:
                    raise RuntimeError(f"Embedding provider failed ({type(exc).__name__}); check configuration/quota") from None
                LOGGER.warning("Transient embedding error (%s); retry %d/%d", type(exc).__name__, attempt + 1, self.max_retries)
                time.sleep(min(2 ** (attempt + 1), 8))
                continue
            embeddings = response.embeddings
            if not embeddings or len(embeddings) != expected:
                raise ValueError("Embedding response count does not match inputs")
            vectors = [e.values for e in embeddings]
            if any(v is None or len(v) != self.dimensions or not all(math.isfinite(x) for x in v) for v in vectors):
                raise ValueError("Embedding response has invalid dimensions or non-finite values")
            return vectors
        raise RuntimeError("Embedding provider unavailable")

    def _embed_single(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Embedding input must be nonempty text")
        if text not in self._cache:
            self._remember(text, self._request(text)[0])
        return self._cache[text]

    def embed_documents(self, texts):
        if any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError("Document embeddings require nonempty text")
        vectors = {t: self._cache[t] for t in texts if t in self._cache}
        pending = list(dict.fromkeys(t for t in texts if t not in vectors))
        for start in range(0, len(pending), 20):
            batch = pending[start:start + 20]
            for text, vector in zip(batch, self._request(batch)):
                vectors[text] = vector
                self._remember(text, vector)
        return [vectors[t] for t in texts]

    def embed_query(self, question):
        return self._embed_single(question)
