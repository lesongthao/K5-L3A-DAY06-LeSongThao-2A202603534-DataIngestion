"""Regressions for invalid chunk settings, failed writes and safe provider errors."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.chunking import by_paragraph, fixed_size, _split_oversized_unit
from src.models import Chunk, DocumentPage
from src.embeddings import GeminiEmbedder
from src.store import ChromaVectorStore
from src.ingestion import load_pdf
from src import run


class SafetyTests(unittest.TestCase):
    def test_bad_chunk_settings_fail_immediately(self):
        page = DocumentPage("d", "source", 1, "hello world")
        for size, overlap in ((0, 0), (10, -1), (10, 10)):
            with self.assertRaises(ValueError):
                fixed_size(page, size, overlap)
        with self.assertRaises(ValueError):
            by_paragraph(page, 0)
        with self.assertRaises(ValueError):
            _split_oversized_unit("hello", 0)

    def test_rejected_update_preserves_old_chunks(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
            store = ChromaVectorStore(temp, 4)
            old = [Chunk(f"c{i}", "doc", "source", 1, f"Text {i}") for i in range(3)]
            store.upsert("strategy_a", old, [[.1, .2, .3, .4]] * 3)
            bad = Chunk("c0", "doc", "source", "bad-page", "Replacement")
            with self.assertRaises(ValueError):
                store.upsert("strategy_a", [bad], [[.1, .2, .3, .4]])
            collection = store._get_collection("strategy_a")
            self.assertEqual(collection.count(), 3)
            with self.assertRaises(ValueError):
                store.upsert("strategy_a", old[:1], [[float("nan"), .2, .3, .4]])
            self.assertEqual(collection.count(), 3)
            with patch.object(type(collection), "upsert", side_effect=RuntimeError("write failed")):
                with self.assertRaises(RuntimeError):
                    store.upsert("strategy_a", old[:1], [[.1, .2, .3, .4]])
            self.assertEqual(collection.count(), 3)

    def provider(self, response=None, error=None):
        provider = GeminiEmbedder(api_key="test-only-value", validate_dimensions=False, max_retries=1)
        if error:
            provider.client = SimpleNamespace(models=SimpleNamespace(embed_content=lambda **_: (_ for _ in ()).throw(error)))
        else:
            provider.client = SimpleNamespace(models=SimpleNamespace(embed_content=lambda **_: response))
        return provider

    def test_provider_error_does_not_echo_credentials_or_text(self):
        provider = self.provider(error=RuntimeError("private-test-value: private query"))
        with self.assertRaises(RuntimeError) as error:
            provider.embed_query("private query")
        self.assertNotIn("private-test-value", str(error.exception))
        self.assertNotIn("private query", str(error.exception))

    def test_provider_rejects_wrong_vector_response(self):
        response = SimpleNamespace(embeddings=[SimpleNamespace(values=[.1] * 4)])
        with self.assertRaises(ValueError):
            self.provider(response=response).embed_query("test query")

    def audit_inputs(self):
        pdf = ROOT / "data/so_tay_sinh_vien_2024.pdf"
        pages, _ = load_pdf(pdf, "so-tay-sinh-vien-2024", "data/so_tay_sinh_vien_2024.pdf")
        traces = [json.loads((ROOT / f"results/traces_strategy_{s}.json").read_text(encoding="utf-8")) for s in "abc"]
        return pdf, pages, traces

    def test_confirmation_expires_when_labels_change(self):
        pdf, pages, traces = self.audit_inputs()
        self.assertEqual(run.build_audit_report(pages, *traces, pdf)["human_review_status"], "confirmed")
        avg_a, avg_b, details = copy.deepcopy(run.run_coherence_audit(pages))
        details[0]["strategy_a"]["reason"] += " Changed label."
        with patch.object(run, "run_coherence_audit", return_value=(avg_a, avg_b, details)):
            report = run.build_audit_report(pages, *traces, pdf)
        self.assertEqual(report["human_review_status"], "unconfirmed")
        self.assertIsNone(report["confirmation"])

    def test_confirmation_expires_when_corpus_changes(self):
        pdf, pages, traces = self.audit_inputs()
        with tempfile.TemporaryDirectory() as temp:
            changed = Path(temp) / "changed.pdf"
            changed.write_bytes(pdf.read_bytes() + b"\n")
            report = run.build_audit_report(pages, *traces, changed)
            self.assertEqual(report["human_review_status"], "unconfirmed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
