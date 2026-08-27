import json
import tempfile
import unittest
from pathlib import Path

from artifact_io import atomic_write_json
from pipeline import auto_discover_and_build


class PipelineSafetyTests(unittest.TestCase):
    def test_incomplete_analysis_blocks_compilation_and_records_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "audio").mkdir()
            (root / "audio" / "chapter_01.mp3").write_bytes(b"fixture")
            (root / "audio" / "book_ch01_acoustic_words.json").write_text(
                json.dumps({"words": []}), encoding="utf-8"
            )
            (root / "book_ch01_canonical_sentences.json").write_text(
                json.dumps([{"id": "s-1", "text": "A sentence."}]), encoding="utf-8"
            )
            (root / "book_ch01_full_analysis.json").write_text(
                json.dumps([{"id": "s-1", "text": "A sentence.", "trans": "", "vocab": []}]),
                encoding="utf-8",
            )

            ready, output = auto_discover_and_build(root)

            self.assertEqual(ready, 0)
            self.assertFalse(Path(output).exists())
            manifest = json.loads((root / "reader_run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "blocked")
            self.assertEqual(manifest["chapters"][0]["status"], "blocked")

    def test_atomic_json_write_leaves_no_temporary_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "nested" / "artifact.json"
            atomic_write_json(output, {"status": "complete"})
            self.assertEqual(json.loads(output.read_text()), {"status": "complete"})
            self.assertEqual(list(output.parent.glob("*.tmp")), [])
            self.assertEqual(list(output.parent.glob(f".{output.name}.*")), [])


if __name__ == "__main__":
    unittest.main()
