import unittest
from extract_epub import split_into_atomic_sentences

class SentenceBoundaryTests(unittest.TestCase):
    def test_parenthetical_sentence_is_separate(self):
        text = "First sentence. (A second sentence.) Two years later, a third sentence."
        self.assertEqual(split_into_atomic_sentences(text), [
            "First sentence.", "(A second sentence.)", "Two years later, a third sentence."
        ])

    def test_abbreviations_do_not_split(self):
        self.assertEqual(split_into_atomic_sentences("Dr. Smith arrived. He spoke."), [
            "Dr. Smith arrived.", "He spoke."
        ])

if __name__ == "__main__":
    unittest.main()
