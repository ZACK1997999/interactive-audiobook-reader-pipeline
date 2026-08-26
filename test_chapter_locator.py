import unittest

from chapter_locator import locate_chapter_start


class ChapterLocatorTests(unittest.TestCase):
    def test_finds_unique_chapter_start_after_audio_intro(self):
        words = [{"word": word} for word in "publisher introduction alpha begins the real chapter continues".split()]
        location = locate_chapter_start("Alpha begins the real chapter continues", words)
        self.assertEqual(location.status, "resolved")
        self.assertEqual(location.selected.start_token, 2)

    def test_exposes_duplicate_chapter_starts_as_ambiguous(self):
        words = [{"word": word} for word in "alpha begins now filler alpha begins now".split()]
        location = locate_chapter_start("Alpha begins now", words)
        self.assertEqual(location.status, "ambiguous")
        self.assertGreaterEqual(len(location.candidates), 2)

    def test_missing_chapter_is_not_silently_selected(self):
        words = [{"word": word} for word in "unrelated narration only".split()]
        location = locate_chapter_start("Alpha begins now", words)
        self.assertEqual(location.status, "no-match")


if __name__ == "__main__":
    unittest.main()
