import json
import tempfile
import unittest
from pathlib import Path

from manifests import build_audio_manifest, write_audio_manifest
from run_manifest import update_manifest


class ManifestTests(unittest.TestCase):
    def test_audio_manifest_is_explicit_and_hashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for number in (2, 3):
                (root / f"{number:03d} - The Housemaid.mp3").write_bytes(bytes([number]))
            manifest = build_audio_manifest(root, "the-housemaid", "https://cdn.example", chapter_count=2)
            self.assertEqual(manifest["chapter_count"], 2)
            self.assertEqual(manifest["entries"][0]["object_key"], "the-housemaid/chapter_01.mp3")
            self.assertEqual(manifest["entries"][1]["object_key"], "the-housemaid/chapter_02.mp3")
            self.assertTrue(manifest["entries"][0]["source_sha256"])
            output = write_audio_manifest(root / "audio_manifest.json", manifest)
            self.assertEqual(json.loads(output.read_text())["book_id"], "the-housemaid")

    def test_run_manifest_preserves_run_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first_path = update_manifest(root, [], status="prepared")
            first = json.loads((root / "reader_run_manifest.json").read_text())
            first["source_files"] = [{"path": "book.epub", "sha256": "abc"}]
            first_path.write_text(json.dumps(first), encoding="utf-8")
            update_manifest(root, [], status="released")
            second = json.loads((root / "reader_run_manifest.json").read_text())
            self.assertEqual(first["run_id"], second["run_id"])
            self.assertEqual(first["created_at"], second["created_at"])
            self.assertEqual(second["status"], "released")
            self.assertEqual(second["source_files"][0]["sha256"], "abc")


if __name__ == "__main__":
    unittest.main()
