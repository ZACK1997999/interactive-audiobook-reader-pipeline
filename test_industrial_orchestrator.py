import json
import tempfile
import unittest
from pathlib import Path

from artifact_io import atomic_write_json
from industrial_orchestrator import run


class IndustrialOrchestratorTests(unittest.TestCase):
    def test_dry_run_persists_resumable_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            atomic_write_json(root / "demo_ch01_canonical_sentences.json", [{"id": "s-1", "text": "A sentence."}])
            state = root / "state.json"
            self.assertEqual(run(root, state, dry_run=True), 0)
            data = json.loads(state.read_text())
            self.assertEqual(data["status"], "dry_run_passed")
            self.assertEqual(data["intake"]["chapters"], 1)
            self.assertEqual(data["intake"]["canonical_records"], 1)
            self.assertEqual(data["chapters"]["1"]["attempts"]["linguistic"], 0)

    def test_missing_worker_is_explicitly_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            atomic_write_json(root / "demo_ch01_canonical_sentences.json", [{"id": "s-1", "text": "A sentence."}])
            state = root / "state.json"
            self.assertEqual(run(root, state), 1)
            data = json.loads(state.read_text())
            self.assertEqual(data["status"], "blocked")
            self.assertIn("worker command not configured", json.dumps(data))

    def test_existing_analysis_with_changed_source_text_is_not_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = [{"id": "s-1", "text": "Original sentence."}]
            atomic_write_json(root / "demo_ch01_canonical_sentences.json", canonical)
            atomic_write_json(root / "demo_ch01_full_analysis.json", [{
                "id": "s-1", "text": "Original sentence,改写了", "trans": "原句", "vocab": []
            }])
            state = root / "state.json"
            self.assertEqual(run(root, state), 1)
            data = json.loads(state.read_text())
            self.assertIn("existing artifact failed contract validation", json.dumps(data))


if __name__ == "__main__":
    unittest.main()
