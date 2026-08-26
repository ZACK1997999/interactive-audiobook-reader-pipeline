import json
import tempfile
import unittest
from pathlib import Path

from validate_outputs import validate


class ReleaseGateTests(unittest.TestCase):
    def _write_fixture(self, root: Path, *, status="validated"):
        (root / "audio").mkdir()
        (root / "audio" / "chapter_01.mp3").write_bytes(b"fixture")
        canonical = [{"id": "s-1", "text": "A sentence."}]
        analysis = [{"id": "s-1", "text": "A sentence.", "trans": "一个句子。", "vocab": []}]
        aligned = [{
            "id": "s-1", "text": "A sentence.", "word_spans": [{"word": "A", "start": 0.0, "end": 0.2}],
            "raw_start": 0.0, "raw_end": 0.4, "has_audio_match": True,
            "fallback_used": False, "alignment_status": status,
            "matched_token_count": 2, "source_token_count": 2, "match_ratio": 1.0,
        }]
        for suffix, data in (("canonical_sentences", canonical), ("full_analysis", analysis), ("aligned_sentences", aligned)):
            (root / f"book_ch01_{suffix}.json").write_text(json.dumps(data), encoding="utf-8")

    def test_valid_fixture_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            self.assertEqual(validate(root), 0)

    def test_review_required_fixture_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root, status="review-required")
            self.assertNotEqual(validate(root), 0)


if __name__ == "__main__":
    unittest.main()
