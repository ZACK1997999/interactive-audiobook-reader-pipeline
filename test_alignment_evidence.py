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
        self.assertFalse(item["fallback_used"])
        self.assertIsNone(item["start"])
        self.assertIsNone(item["end"])

    def test_out_of_order_global_match_requires_review(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate("second exact phrase filler first exact phrase".split())]
        result = self.run_alignment(words, [{"id": "s-1", "text": "first exact phrase"}, {"id": "s-2", "text": "second exact phrase"}])
        self.assertEqual(result[0]["alignment_status"], "validated")
        self.assertEqual(result[1]["alignment_reason"], "global_match_out_of_order")

    def test_word_spans_follow_matching_blocks_after_audio_insertion(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate("alpha extra beta gamma".split())]
        result = self.run_alignment(words, [{"id": "s-1", "text": "alpha beta gamma"}])[0]
        self.assertEqual([span["word"] for span in result["word_spans"]], ["alpha", "beta", "gamma"])
        self.assertEqual(result["word_spans"][1]["start"], 2)
        self.assertEqual(result["word_spans"][2]["start"], 3)

    def test_unmatched_word_is_interpolated_between_adjacent_matches(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate("alpha beta".split())]
        item = self.run_alignment(words, [{"id": "s-1", "text": "alpha UNKNOWN beta"}])[0]
        unknown = item["word_spans"][1]
        self.assertGreaterEqual(unknown["start"], 0.5)
        self.assertLessEqual(unknown["end"], 1.0)

    def test_ambiguous_short_sentence_requires_review(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate("No. Maybe no.".split())]
        item = self.run_alignment(words, [{"id": "s-1", "text": "No."}])[0]
        self.assertEqual(item["alignment_status"], "review-required")
        self.assertEqual(item["alignment_reason"], "ambiguous_short_sentence")

    def test_short_exact_match_uses_unique_neighbor_bounded_occurrence(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate(
            "opening context excuse me closing context excuse me".split()
        )]
        result = self.run_alignment(words, [
            {"id": "s-1", "text": "opening context"},
            {"id": "s-2", "text": "Excuse me!"},
            {"id": "s-3", "text": "closing context"},
        ])
        self.assertEqual(result[1]["alignment_status"], "validated")
        self.assertEqual(result[1]["alignment_method"], "contextual_short_exact_match")
        self.assertEqual(result[1]["word_spans"][0]["start"], 2)

    def test_common_contraction_matches_spoken_expansion(self):
        words = [{"word": word, "start": index, "end": index + 0.5} for index, word in enumerate("I did not know".split())]
        item = self.run_alignment(words, [{"id": "s-1", "text": "I didn't know."}])[0]
        self.assertEqual(item["alignment_status"], "validated")
        self.assertEqual(item["matched_token_count"], 4)
        self.assertEqual(item["word_spans"][1]["start"], 1)

    def test_real_chapter_two_leading_attribution_is_bound_before_printed_quote(self):
        words = [{"word": word, "start": start, "end": end} for word, start, end in [
            ("Chapter", 0.0, 0.6), ("2.", 0.6, 0.9),
            ("A", 3.04, 3.76), ("quote", 3.76, 4.14), ("from", 4.14, 4.54),
            ("Major", 4.54, 5.24), ("Ofendra's", 5.24, 5.96), ("Guide", 5.96, 6.32),
            ("to", 6.32, 6.52), ("the", 6.52, 6.64), ("Writer's", 6.64, 7.0),
            ("Quadrant,", 7.0, 7.5), ("Unauthorized", 7.76, 8.76), ("Edition.", 8.76, 9.12),
            ("There's", 10.44, 11.16), ("a", 11.16, 11.26),
            ("misconception", 11.26, 11.86), ("that", 11.86, 12.42),
            ("it's", 12.42, 12.62), ("kill", 12.62, 13.16), ("or", 13.16, 13.42),
            ("be", 13.42, 13.72), ("killed", 13.72, 14.16), ("in", 14.16, 14.36),
            ("the", 14.36, 14.46), ("Writer's", 14.46, 14.82), ("Quadrant.", 14.82, 15.28),
        ]]
        result = self.run_alignment(words, [
            {"id": "s-0", "text": "There’s a misconception that it’s kill or be killed in the Riders Quadrant."},
            {"id": "s-1", "text": "—Major Afendra’s Guide to the Riders Quadrant (Unauthorized Edition)"},
        ])
        attribution = result[1]
        self.assertEqual(attribution["alignment_method"], "leading_epigraph_attribution")
        self.assertEqual(attribution["audio_start"], 3.04)
        self.assertEqual(attribution["audio_end"], 9.12)
        self.assertEqual(attribution["audio_order"], 5)
        self.assertTrue(attribution["has_audio_match"])
        self.assertEqual(result[0]["audio_start"], 10.44)
