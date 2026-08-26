import json
import tempfile
import unittest
from pathlib import Path

from validate_outputs import _chapter_audio_exists, validate
from dynamic_aligner import align_sentences_with_audio
from pipeline import _find_chapter_audio


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

    def test_reviewed_out_of_order_alignment_can_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "audio").mkdir()
            (root / "audio" / "chapter_01.mp3").write_bytes(b"fixture")
            sentences = [{"id": "s-1", "text": "first exact phrase"}, {"id": "s-2", "text": "second exact phrase"}]
            analysis_path = root / "book_ch01_full_analysis.json"
            analysis_path.write_text(json.dumps(sentences), encoding="utf-8")
            (root / "book_ch01_canonical_sentences.json").write_text(json.dumps(sentences), encoding="utf-8")
            acoustic_path = root / "audio" / "book_ch01_acoustic_words.json"
            acoustic_path.write_text(json.dumps({"words": [
                {"word": word, "start": index, "end": index + 0.5}
                for index, word in enumerate("second exact phrase filler first exact phrase".split())
            ]}), encoding="utf-8")
            aligned_path = root / "book_ch01_aligned_sentences.json"
            align_sentences_with_audio(acoustic_path, analysis_path, aligned_path)
            self.assertNotEqual(validate(root), 0)

            aligned = json.loads(aligned_path.read_text(encoding="utf-8"))
            aligned[1]["alignment_status"] = "reviewed"
            aligned_path.write_text(json.dumps(aligned), encoding="utf-8")
            self.assertEqual(validate(root), 0)

    def test_audio_fallback_matches_explicit_chapter_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio_dir = Path(tmp)
            (audio_dir / "narration_ch10.mp3").write_bytes(b"10")
            (audio_dir / "narration_ch11.mp3").write_bytes(b"11")
            self.assertIsNone(_find_chapter_audio(str(audio_dir), 1))
            self.assertEqual(Path(_find_chapter_audio(str(audio_dir), 11)).name, "narration_ch11.mp3")
            self.assertFalse(_chapter_audio_exists(audio_dir, 1))
            self.assertTrue(_chapter_audio_exists(audio_dir, 11))


if __name__ == "__main__":
    unittest.main()
