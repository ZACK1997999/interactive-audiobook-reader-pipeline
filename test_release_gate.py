import json
import hashlib
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

    def test_owner_review_ledger_accepts_explicit_audio_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            aligned = root / "book_ch01_aligned_sentences.json"
            data = json.loads(aligned.read_text(encoding="utf-8"))
            data[0]["has_audio_match"] = False
            data[0]["fallback_used"] = True
            aligned.write_text(json.dumps(data), encoding="utf-8")
            (root / "reader_review_ledger.json").write_text(json.dumps({
                "schema_version": 1,
                "reviews": [{
                    "chapter": 1,
                    "sentence_id": "s-1",
                    "decision": "accepted",
                    "reviewer": "project_owner",
                    "evidence": "Reviewed audiobook wording discrepancy.",
                }],
            }), encoding="utf-8")
            self.assertEqual(validate(root), 0)

    def test_reviewed_out_of_order_alignment_can_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "audio").mkdir()
            (root / "audio" / "chapter_01.mp3").write_bytes(b"fixture")
            sentences = [
                {"id": "s-1", "text": "first exact phrase", "trans": "第一个准确短语", "vocab": []},
                {"id": "s-2", "text": "second exact phrase", "trans": "第二个准确短语", "vocab": []},
            ]
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
            aligned[1]["review_evidence"] = "Verified against the acoustic word sequence."
            aligned_path.write_text(json.dumps(aligned), encoding="utf-8")
            self.assertEqual(validate(root), 0)

    def test_empty_translation_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            analysis = root / "book_ch01_full_analysis.json"
            data = json.loads(analysis.read_text(encoding="utf-8"))
            data[0]["trans"] = ""
            analysis.write_text(json.dumps(data), encoding="utf-8")
            self.assertNotEqual(validate(root), 0)

    def test_malformed_vocabulary_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            analysis = root / "book_ch01_full_analysis.json"
            data = json.loads(analysis.read_text(encoding="utf-8"))
            data[0]["vocab"] = [{"word": "only-word"}]
            analysis.write_text(json.dumps(data), encoding="utf-8")
            self.assertNotEqual(validate(root), 0)

    def test_manifest_detects_post_alignment_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            aligned = root / "book_ch01_aligned_sentences.json"
            digest = hashlib.sha256(aligned.read_bytes()).hexdigest()
            (root / "reader_run_manifest.json").write_text(json.dumps({
                "schema_version": 2,
                "chapters": [{"chapter": 1, "aligned_sha256": digest}],
            }), encoding="utf-8")
            aligned.write_text(aligned.read_text() + "\n", encoding="utf-8")
            self.assertNotEqual(validate(root), 0)

    def test_audio_fallback_matches_explicit_chapter_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio_dir = Path(tmp)
            (audio_dir / "narration_ch10.mp3").write_bytes(b"10")
            (audio_dir / "narration_ch11.mp3").write_bytes(b"11")
            self.assertIsNone(_find_chapter_audio(str(audio_dir), 1))
            self.assertEqual(Path(_find_chapter_audio(str(audio_dir), 11)).name, "narration_ch11.mp3")
            self.assertFalse(_chapter_audio_exists(audio_dir, 1))
            self.assertTrue(_chapter_audio_exists(audio_dir, 11))

    def test_ambiguous_audio_candidates_block_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            (root / "audio" / "bonus_ch01.mp3").write_bytes(b"bonus")
            self.assertIsNone(_find_chapter_audio(str(root / "audio"), 1))
            self.assertFalse(_chapter_audio_exists(root / "audio", 1))
            self.assertNotEqual(validate(root), 0)


if __name__ == "__main__":
    unittest.main()
