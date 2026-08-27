import json
import tempfile
import unittest
from pathlib import Path

from artifact_io import atomic_write_json
from publisher import STEPS, publish, update_library_manifest


def _config(root: Path):
    reader = root / "reader.html"
    audio = root / "audio.mp3"
    cover = root / "cover.jpg"
    manifest = root / "audio_manifest.json"
    reader.write_text("<html>reader</html>")
    audio.write_bytes(b"audio")
    cover.write_bytes(b"cover")
    atomic_write_json(manifest, {"entries": [{"source_path": str(audio), "object_key": "book/1.mp3"}]})
    return {
        "book_id": "book", "reader_html": str(reader), "audio_manifest": str(manifest),
        "cover": str(cover), "portal_repo": str(root / "portal"),
        "manifest_entry": {"id": "book", "title": "Book"},
        "public_reader_url": "https://example.test/books/book/",
    }


class PublisherTests(unittest.TestCase):
    def test_journal_resumes_after_failure_without_repeating_completed_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _config(root)
            journal = root / "journal.json"
            calls = {step: 0 for step in STEPS}
            fail_once = {"value": True}

            def action(step):
                def run(config, context):
                    calls[step] += 1
                    if step == "remote_verify" and fail_once["value"]:
                        fail_once["value"] = False
                        raise RuntimeError("network down")
                    return {"step": step}
                return run

            actions = {step: action(step) for step in STEPS}
            with self.assertRaisesRegex(RuntimeError, "network down"):
                publish(config, journal, actions)
            result = publish(config, journal, actions)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(calls["preflight"], 1)
            self.assertEqual(calls["archive"], 1)
            self.assertEqual(calls["r2_upload"], 1)
            self.assertEqual(calls["remote_verify"], 2)
            self.assertEqual(calls["git_push"], 1)

            publish(config, journal, actions)
            self.assertEqual(calls["git_push"], 1)

    def test_changed_release_cannot_reuse_completed_journal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _config(root)
            journal = root / "journal.json"
            actions = {step: (lambda config, context: {}) for step in STEPS}
            publish(config, journal, actions)
            Path(config["reader_html"]).write_text("<html>changed</html>")
            with self.assertRaisesRegex(RuntimeError, "inputs changed"):
                publish(config, journal, actions)

    def test_manifest_update_replaces_book_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            atomic_write_json(path, {"books": [{"id": "book", "title": "Old"}, {"id": "other"}]})
            update_library_manifest(path, {"id": "book", "title": "New"})
            data = json.loads(path.read_text())
            self.assertEqual([book["id"] for book in data["books"]], ["book", "other"])
            self.assertEqual(data["books"][0]["title"], "New")


if __name__ == "__main__":
    unittest.main()
