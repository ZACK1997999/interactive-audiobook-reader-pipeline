import json
import tempfile
import unittest
from pathlib import Path

from dynamic_aligner import align_sentences_with_audio


class AlignmentEvidenceTests(unittest.TestCase):
    def run_alignment(self, words, sentences):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            acoustic = root / "acoustic.json"
            analysis = root / "analysis.json"
            output = root / "aligned.json"
            acoustic.write_text(json.dumps({"words": words}), encoding="utf-8")
            analysis.write_text(json.dumps(sentences), encoding="utf-8")
            return align_sentences_with_audio(acoustic, analysis, output)

    def test_exact_match_has_evidence(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate("The quick brown fox".split())]
        item = self.run_alignment(words, [{"id": "s-1", "text": "The quick brown fox."}])[0]
        self.assertEqual(item["alignment_status"], "validated")
        self.assertEqual(item["matched_token_count"], 4)
        self.assertEqual(item["match_ratio"], 1.0)

    def test_weak_match_requires_review(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate("noise only one token here".split())]
        item = self.run_alignment(words, [{"id": "s-1", "text": "one entirely different sentence"}])[0]
        self.assertEqual(item["alignment_status"], "review-required")
        self.assertTrue(item["fallback_used"])

    def test_out_of_order_global_match_requires_review(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate("second exact phrase filler first exact phrase".split())]
        result = self.run_alignment(words, [{"id": "s-1", "text": "first exact phrase"}, {"id": "s-2", "text": "second exact phrase"}])
        self.assertEqual(result[0]["alignment_status"], "validated")
        self.assertEqual(result[1]["alignment_reason"], "global_match_out_of_order")
