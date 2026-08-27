import json
import tempfile
import unittest
from pathlib import Path

from artifact_io import atomic_write_json
from pipeline import _public_audio_url, auto_discover_and_build
from quality_gate import smoke_check_html, validate_semantic_review


class PipelineSafetyTests(unittest.TestCase):
    def test_public_audio_url_uses_canonical_one_based_chapters(self):
        self.assertEqual(
            _public_audio_url("https://cdn.example/", "the-housemaid", 0),
            "https://cdn.example/the-housemaid/chapter_01.mp3",
        )
        self.assertEqual(
            _public_audio_url("https://cdn.example", "the-housemaid", 63),
            "https://cdn.example/the-housemaid/chapter_63.mp3",
        )
        self.assertIsNone(_public_audio_url("https://cdn.example", None, 1))

    def test_incomplete_analysis_blocks_compilation_and_records_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "audio").mkdir()
            (root / "audio" / "chapter_01.mp3").write_bytes(b"fixture")
            (root / "audio" / "book_ch01_acoustic_words.json").write_text(
                json.dumps({"words": []}), encoding="utf-8"
            )
            (root / "book_ch01_canonical_sentences.json").write_text(
                json.dumps([{"id": "s-1", "text": "A sentence."}]), encoding="utf-8"
            )
            (root / "book_ch01_full_analysis.json").write_text(
                json.dumps([{"id": "s-1", "text": "A sentence.", "trans": "", "vocab": []}]),
                encoding="utf-8",
            )

            ready, output = auto_discover_and_build(root)

            self.assertEqual(ready, 0)
            self.assertFalse(Path(output).exists())
            manifest = json.loads((root / "reader_run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "blocked")
            self.assertEqual(manifest["chapters"][0]["status"], "blocked")

    def test_atomic_json_write_leaves_no_temporary_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "nested" / "artifact.json"
            atomic_write_json(output, {"status": "complete"})
            self.assertEqual(json.loads(output.read_text()), {"status": "complete"})
            self.assertEqual(list(output.parent.glob("*.tmp")), [])
            self.assertEqual(list(output.parent.glob(f".{output.name}.*")), [])

    def test_quality_smoke_check_requires_reader_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reader.html"
            path.write_text("<html><body></body></html>", encoding="utf-8")
            report = smoke_check_html(path)
            self.assertEqual(report["status"], "failed")
            self.assertIn("missing HTML5 doctype", report["errors"])

    def test_semantic_review_requires_explicit_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reader_semantic_review.json"
            path.write_text(json.dumps({
                "schema_version": 1,
                "status": "approved",
                "reviewer": "owner",
                "reviewed_at": "2026-08-27",
                "method": "beginning-middle-end sample",
                "samples": [{
                    "chapter": 1,
                    "sentence_ids": ["s-1"],
                    "checks": {
                        "translation_accuracy": True,
                        "alignment_semantics": True,
                        "vocabulary_quality": True,
                    },
                }],
            }), encoding="utf-8")
            self.assertEqual(validate_semantic_review(path, required_chapters=[1])["status"], "passed")

    def test_book_run_lock_rejects_concurrent_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            from pipeline import _book_run_lock
            with _book_run_lock(tmp):
                with self.assertRaises(RuntimeError):
                    with _book_run_lock(tmp):
                        pass


if __name__ == "__main__":
    unittest.main()
