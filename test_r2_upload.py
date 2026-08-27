import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from r2_upload import CACHE_CONTROL, sync_manifest, upload_manifest


class _R2Client:
    def __init__(self, remote_hash=None):
        self.remote_hash = remote_hash
        self.uploads = []

    def head_object(self, **kwargs):
        if self.remote_hash is None:
            error = RuntimeError("not found")
            error.response = {"ResponseMetadata": {"HTTPStatusCode": 404}, "Error": {"Code": "NoSuchKey"}}
            raise error
        return {"Metadata": {"sha256": self.remote_hash}}

    def upload_file(self, *args, **kwargs):
        self.uploads.append((args, kwargs))


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

    def test_sha_match_skips_upload_and_changed_object_gets_immutable_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "chapter.mp3"
            source.write_bytes(b"audio")
            import hashlib
            digest = hashlib.sha256(b"audio").hexdigest()
            manifest = root / "audio_manifest.json"
            manifest.write_text(json.dumps({"entries": [{
                "source_path": str(source), "source_sha256": digest, "object_key": "book/chapter.mp3"
            }]}))
            env = {"R2_ACCESS_KEY_ID": "x", "R2_SECRET_ACCESS_KEY": "y"}
            with patch.dict(os.environ, env, clear=False):
                same = _R2Client(digest)
                self.assertEqual(sync_manifest(manifest, client=same)["skipped"], 1)
                self.assertEqual(same.uploads, [])
                changed = _R2Client("old")
                self.assertEqual(sync_manifest(manifest, client=changed)["uploaded"], 1)
            extra = changed.uploads[0][1]["ExtraArgs"]
            self.assertEqual(extra["Metadata"]["sha256"], digest)
            self.assertEqual(extra["CacheControl"], CACHE_CONTROL)


if __name__ == "__main__":
    unittest.main()
