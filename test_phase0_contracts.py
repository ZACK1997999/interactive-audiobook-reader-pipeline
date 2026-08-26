import json
import unittest
from pathlib import Path

from models import (
    AcousticWord,
    AlignmentRecord,
    AudioTrack,
    CanonicalSentence,
    LinguisticAnalysis,
    SCHEMA_VERSION,
    ValidationReport,
    VocabularyItem,
    WordSpan,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "phase0"


class Phase0ContractTests(unittest.TestCase):
    def test_synthetic_fixture_preserves_ids_and_order(self):
        canonical = json.loads((FIXTURE_DIR / "example_ch01_canonical_sentences.json").read_text())
        analysis = json.loads((FIXTURE_DIR / "example_ch01_full_analysis.json").read_text())
        aligned = json.loads((FIXTURE_DIR / "example_ch01_aligned_sentences.json").read_text())
        ids = [item["id"] for item in canonical]
        self.assertEqual([item["id"] for item in analysis], ids)
        self.assertEqual([item["id"] for item in aligned], ids)
        self.assertTrue(all(item["alignment_status"] == "validated" for item in aligned))

    def test_domain_models_cover_the_stable_boundary(self):
        sentence = CanonicalSentence("s-1", "Alpha begins.", source_index=0)
        track = AudioTrack("track-1", "audio/chapter_01.mp3", chapter_number=1)
        word = AcousticWord("Alpha", 0.0, 0.3, token_index=0)
        span = WordSpan("Alpha", 0.0, 0.3, source_word_index=0, acoustic_word_start=0, acoustic_word_end=0)
        record = AlignmentRecord("s-1", sentence.text, 0.0, 0.7, [span], has_audio_match=True, alignment_status="validated")
        item = VocabularyItem("begin", "v.", "开始")
        analysis = LinguisticAnalysis("s-1", sentence.text, "阿尔法开始了。", [item])
        report = ValidationReport("/private/example", release_ready=True)

        self.assertEqual(SCHEMA_VERSION, "1.0")
        self.assertEqual(track.chapter_number, 1)
        self.assertEqual(word.token_index, 0)
        self.assertTrue(record.has_audio_match)
        self.assertEqual(analysis.vocabulary[0].definition, "开始")
        self.assertTrue(report.release_ready)


if __name__ == "__main__":
    unittest.main()
