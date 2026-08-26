import tempfile
import unittest
from pathlib import Path

from chapter_resolver import discover_chapters
from pipeline import _find_chapter_audio


class ChapterResolverTests(unittest.TestCase):
    def test_discovers_chapter_artifacts_without_book_specific_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "audio").mkdir()
            canonical = root / "example_ch03_canonical_sentences.json"
            canonical.write_text("[]", encoding="utf-8")
            artifacts = discover_chapters(root)
            self.assertEqual(len(artifacts), 1)
            self.assertEqual(artifacts[0].chapter_number, 3)
            self.assertEqual(artifacts[0].analysis_path.name, "example_ch03_full_analysis.json")
            self.assertEqual(artifacts[0].acoustic_path.name, "example_ch03_acoustic_words.json")

    def test_audio_resolution_rejects_ambiguous_explicit_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio_dir = Path(tmp)
            (audio_dir / "narrator_ch03.mp3").write_bytes(b"a")
            (audio_dir / "bonus_ch03.mp3").write_bytes(b"b")
            self.assertIsNone(_find_chapter_audio(str(audio_dir), 3))


if __name__ == "__main__":
    unittest.main()
