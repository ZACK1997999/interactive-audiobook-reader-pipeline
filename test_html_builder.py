import json
import re
import tempfile
import unittest
from pathlib import Path

from html_builder import build_master_reader


class HTMLBuilderTests(unittest.TestCase):
    def test_zero_jitter_css_invariants(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            aligned = tmp_path / "aligned.json"
            aligned.write_text(
                json.dumps([
                    {
                        "id": "c1-s1",
                        "text": "A complete sentence.",
                        "translation": "一个完整的句子。",
                        "start": 0.0,
                        "end": 1.0,
                        "word_spans": [{"word": "A", "start": 0.0, "end": 0.2}],
                    }
                ], ensure_ascii=False),
                encoding="utf-8",
            )
            output = tmp_path / "reader.html"

            build_master_reader(
                book_title="Test Book",
                book_subtitle="A Test",
                book_author="Test Author",
                chapters_config=[{
                    "num": 1,
                    "title": "Chapter One",
                    "audio": "./audio/chapter_01.mp3",
                    "aligned_json": str(aligned),
                }],
                output_html_path=str(output),
            )

            rendered = output.read_text(encoding="utf-8")
            rules = re.findall(r"\.w\.active-word\s*\{(?P<body>.*?)\}", rendered, re.DOTALL)
            self.assertEqual(len(rules), 1)

            forbidden_properties = ("font-weight", "font-size", "letter-spacing", "line-height")
            self.assertFalse(any(
                re.search(rf"(?:^|;)\s*{re.escape(prop)}\s*:", rules[0])
                for prop in forbidden_properties
            ))


def test_diagnostics_are_concrete_and_placeholder_free(tmp_path: Path):
    aligned = tmp_path / "aligned.json"
    aligned.write_text(
        json.dumps([
            {
                "id": "c1-s1",
                "text": "A complete sentence.",
                "translation": "一个完整的句子。",
                "start": 0.0,
                "end": 1.0,
                "word_spans": [{"word": "A", "start": 0.0, "end": 0.2}],
            }
        ], ensure_ascii=False),
        encoding="utf-8",
    )
    output = tmp_path / "reader.html"

    build_master_reader(
        book_title="Test Book",
        book_subtitle="A Test",
        book_author="Test Author",
        chapters_config=[{
            "num": 1,
            "title": "Chapter One",
            "audio": "./audio/chapter_01.mp3",
            "aligned_json": str(aligned),
        }],
        output_html_path=str(output),
    )

    rendered = output.read_text(encoding="utf-8")
    assert "Status labels are hidden from the reading flow" not in rendered
    assert "<strong>Diagnostics</strong>" in rendered
    assert "Chapter 1: Chapter One" in rendered
    assert "status-verified" in rendered
