import fcntl
import json
import sys
import tempfile
import unittest
from pathlib import Path

from artifact_io import atomic_write_json
from industrial_orchestrator import run, run_orchestrator


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

    def test_acoustic_dictionary_resumption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "audio").mkdir()
            canonical = [{"id": "s-1", "text": "A sentence."}]
            analysis = [{"id": "s-1", "text": "A sentence.", "trans": "一个句子。", "vocab": []}]
            acoustic_dict = {
                "words": [{"word": "A", "start": 0.0, "end": 0.5}, {"word": "sentence", "start": 0.6, "end": 1.2}],
                "segments": [{"start": 0.0, "end": 1.2, "text": "A sentence."}],
            }
            atomic_write_json(root / "demo_ch01_canonical_sentences.json", canonical)
            atomic_write_json(root / "demo_ch01_full_analysis.json", analysis)
            atomic_write_json(root / "audio" / "demo_ch01_acoustic_words.json", acoustic_dict)
            state = root / "state.json"
            self.assertEqual(run(root, state), 0)
            data = json.loads(state.read_text())
            self.assertEqual(data["status"], "ready_for_pipeline")
            self.assertEqual(data["chapters"]["1"]["status"], "acoustic_passed")

    def test_worker_retry_exhaustion_leads_to_blocked_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            atomic_write_json(root / "demo_ch01_canonical_sentences.json", [{"id": "s-1", "text": "A sentence."}])
            state = root / "state.json"
            failing_cmd = f"{sys.executable} -c 'import sys; sys.exit(1)'"
            self.assertEqual(run(root, state, linguistic_command=failing_cmd, max_attempts=2), 1)
            data = json.loads(state.read_text())
            self.assertEqual(data["status"], "blocked")
            self.assertEqual(data["chapters"]["1"]["status"], "linguistic_failed")
            self.assertEqual(data["chapters"]["1"]["attempts"]["linguistic"], 2)
            self.assertEqual(len(data["chapters"]["1"]["failures"]), 2)

    def test_natural_sorting_of_audio_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audio_dir = root / "audio"
            audio_dir.mkdir()
            for ch in (1, 2, 10):
                prefix = f"demo_ch{ch:02d}"
                atomic_write_json(root / f"{prefix}_canonical_sentences.json", [{"id": f"s-{ch}", "text": f"Chapter {ch}"}])
            (audio_dir / "chapter_1.mp3").write_bytes(b"audio 1")
            (audio_dir / "chapter_2.mp3").write_bytes(b"audio 2")
            (audio_dir / "chapter_10.mp3").write_bytes(b"audio 10")
            state = root / "state.json"
            self.assertEqual(run(root, state, dry_run=True), 0)
            data = json.loads(state.read_text())
            self.assertTrue(data["chapters"]["1"]["audio"].endswith("chapter_1.mp3"))
            self.assertTrue(data["chapters"]["2"]["audio"].endswith("chapter_2.mp3"))
            self.assertTrue(data["chapters"]["10"]["audio"].endswith("chapter_10.mp3"))

    def test_concurrency_flock_prevention(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            atomic_write_json(root / "demo_ch01_canonical_sentences.json", [{"id": "s-1", "text": "A sentence."}])
            state = root / "state.json"
            lock_path = root / ".orchestrator.lock"
            with lock_path.open("w", encoding="utf-8") as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaises(RuntimeError) as ctx:
                    run(root, state, dry_run=True)
                self.assertIn("Another orchestrator run is active", str(ctx.exception))
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            self.assertEqual(run(root, state, dry_run=True), 0)


if __name__ == "__main__":
    unittest.main()
