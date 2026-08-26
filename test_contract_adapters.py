import json
import tempfile
import unittest
from pathlib import Path

from alignment_backend import CurrentGlobalAlignmentBackend
from contract_adapters import (
    acoustic_words_from_json,
    alignment_record_to_json,
    alignment_records_from_json,
    canonical_sentences_from_json,
    linguistic_analysis_from_json,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "phase0"


class ContractAdapterTests(unittest.TestCase):
    def test_legacy_fixture_maps_to_stable_models(self):
        canonical = json.loads((FIXTURE_DIR / "example_ch01_canonical_sentences.json").read_text())
        analysis = json.loads((FIXTURE_DIR / "example_ch01_full_analysis.json").read_text())
        acoustic = json.loads((FIXTURE_DIR / "example_ch01_acoustic_words.json").read_text())
        aligned = json.loads((FIXTURE_DIR / "example_ch01_aligned_sentences.json").read_text())

        self.assertEqual([item.sentence_id for item in canonical_sentences_from_json(canonical)], ["s-1", "s-2"])
        self.assertEqual(linguistic_analysis_from_json(analysis)[0].translation, "阿尔法开始了。")
        self.assertEqual(acoustic_words_from_json(acoustic)[0].token_index, 0)
        records = alignment_records_from_json(aligned)
        self.assertEqual(records[0].alignment_status, "validated")
        self.assertEqual(alignment_record_to_json(records[0])["id"], "s-1")

    def test_current_backend_preserves_existing_alignment_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            acoustic = root / "acoustic.json"
            analysis = root / "analysis.json"
            output = root / "aligned.json"
            acoustic.write_text(json.dumps({"words": [
                {"word": "Alpha", "start": 0.0, "end": 0.3},
                {"word": "begins", "start": 0.3, "end": 0.7},
            ]}), encoding="utf-8")
            analysis.write_text(json.dumps([{"id": "s-1", "text": "Alpha begins."}]), encoding="utf-8")

            records = CurrentGlobalAlignmentBackend().align(acoustic, analysis, output)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].sentence_id, "s-1")
            self.assertEqual(records[0].alignment_status, "validated")
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
