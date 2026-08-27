import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from r2_upload import upload_manifest


class R2UploadTests(unittest.TestCase):
    def test_dry_run_requires_all_manifest_files_and_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "chapter.mp3"
            source.write_bytes(b"audio")
            manifest = root / "audio_manifest.json"
            manifest.write_text(json.dumps({"entries": [{"source_path": str(source), "object_key": "book/chapter_01.mp3"}]}))
            environment = {"R2_ACCESS_KEY_ID": "configured", "R2_SECRET_ACCESS_KEY": "configured"}
            with patch.dict(os.environ, environment, clear=False):
                self.assertEqual(upload_manifest(manifest, dry_run=True), 1)

    def test_missing_credentials_are_rejected_before_upload(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "audio_manifest.json"
            manifest.write_text(json.dumps({"entries": [{"source_path": "/missing.mp3", "object_key": "book/chapter_01.mp3"}]}))
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "Missing R2 environment configuration"):
                    upload_manifest(manifest, dry_run=False)


if __name__ == "__main__":
    unittest.main()
