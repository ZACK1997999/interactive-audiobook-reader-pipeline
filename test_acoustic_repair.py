import json
import tempfile
import unittest
from pathlib import Path

from acoustic_repair import repair_acoustic_gaps, review_windows
from dynamic_aligner import align_sentences_with_audio


class AcousticRepairTests(unittest.TestCase):
    def test_review_windows_include_short_anchor_after_large_gap(self):
        records = [
            {"id": "s-1", "text": "long anchor sentence", "source_text": "long anchor sentence", "alignment_status": "validated", "audio_start": 1, "audio_end": 3},
            {"id": "s-2", "text": "Violet.", "source_text": "Violet.", "alignment_status": "validated", "audio_start": 20, "audio_end": 21},
            {"id": "s-3", "text": "missing sentence", "alignment_status": "review-required"},
            {"id": "s-4", "text": "following anchor", "alignment_status": "validated", "audio_start": 25, "audio_end": 27},
        ]
        windows = review_windows(records)
        self.assertEqual(windows[0]["first_sentence_id"], "s-2")
        self.assertEqual(windows[0]["start"], 2.0)

    def test_repair_is_accepted_only_when_review_count_drops(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "chapter.mp3"
            acoustic = root / "acoustic.json"
            analysis = root / "analysis.json"
            aligned = root / "aligned.json"
            audio.write_bytes(b"audio fixture")
            analysis.write_text(json.dumps([
                {"id": "s-1", "text": "opening anchor"},
                {"id": "s-2", "text": "recovered dialogue block"},
                {"id": "s-3", "text": "closing anchor"},
            ]), encoding="utf-8")
            words = [
                {"word": "opening", "start": 1, "end": 1.4},
                {"word": "anchor", "start": 1.4, "end": 2},
                {"word": "closing", "start": 8, "end": 8.4},
                {"word": "anchor", "start": 8.4, "end": 9},
            ]
            acoustic.write_text(json.dumps({"model": "fixture", "segments": [], "words": words}), encoding="utf-8")
            align_sentences_with_audio(acoustic, analysis, aligned)

            def fake_transcribe(audio_path, **kwargs):
                self.assertEqual(kwargs["condition_on_previous_text"], False)
                return {"segments": [{
                    "id": 1,
                    "start": 2.5,
                    "end": 7.5,
                    "text": " recovered dialogue block",
                    "words": [
                        {"word": "recovered", "start": 3, "end": 4, "probability": 0.9},
                        {"word": "dialogue", "start": 4, "end": 5, "probability": 0.9},
                        {"word": "block", "start": 5, "end": 6, "probability": 0.9},
                    ],
                }]}

            result = repair_acoustic_gaps(audio, acoustic, analysis, aligned, transcribe_fn=fake_transcribe)
            repaired = json.loads(aligned.read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["review_before"], 1)
        self.assertEqual(result["review_after"], 0)
        self.assertTrue(all(item["alignment_status"] == "validated" for item in repaired))


if __name__ == "__main__":
    unittest.main()
