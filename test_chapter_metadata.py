import json
import tempfile
import unittest
from pathlib import Path

from chapter_metadata import load_chapter_metadata


class ChapterMetadataTests(unittest.TestCase):
    def _write(self, root: Path, chapters: list[dict]) -> Path:
        path = root / "chapter_metadata.json"
        path.write_text(json.dumps({"schema_version": 1, "chapters": chapters}), encoding="utf-8")
        return path

    def test_front_matter_and_printed_chapters_are_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), [
                {"chapter": 0, "role": "preface", "title": "Preface"},
                {"chapter": 1, "role": "introduction", "title": "Introduction"},
                {"chapter": 2, "role": "chapter", "display_number": 1, "title": "Levers"},
            ])
            metadata = load_chapter_metadata(path, expected_chapters=[0, 1, 2])
            self.assertIsNone(metadata[1]["display_number"])
            self.assertEqual(metadata[2]["display_number"], 1)

    def test_missing_track_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), [
                {"chapter": 1, "role": "chapter", "display_number": 1, "title": "One"},
            ])
            with self.assertRaisesRegex(ValueError, "missing=\\[2\\]"):
                load_chapter_metadata(path, expected_chapters=[1, 2])

    def test_front_matter_cannot_claim_a_printed_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), [
                {"chapter": 0, "role": "preface", "display_number": 1, "title": "Preface"},
            ])
            with self.assertRaisesRegex(ValueError, "cannot have display_number"):
                load_chapter_metadata(path)


if __name__ == "__main__":
    unittest.main()
