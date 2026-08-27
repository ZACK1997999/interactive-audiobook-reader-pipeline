import json
import re
import tempfile
import unittest
from pathlib import Path

from html_builder import build_master_reader
from validate_outputs import validate_for_release


def _make_release_token(tmp_path: Path):
    (tmp_path / "audio").mkdir(exist_ok=True)
    (tmp_path / "audio" / "chapter_01.mp3").write_bytes(b"fixture")
    canonical = [{"id": "s-1", "text": "A complete sentence."}]
    analysis = [{"id": "s-1", "text": "A complete sentence.", "trans": "一个完整的句子。", "vocab": []}]
    aligned = [{
        **analysis[0], "word_spans": [{"word": "A", "start": 0.0, "end": 0.2}],
        "raw_start": 0.0, "raw_end": 1.0, "has_audio_match": True,
        "fallback_used": False, "alignment_status": "validated",
        "matched_token_count": 3, "source_token_count": 3, "match_ratio": 1.0,
    }]
    for suffix, data in (("canonical_sentences", canonical), ("full_analysis", analysis), ("aligned_sentences", aligned)):
        (tmp_path / f"book_ch01_{suffix}.json").write_text(json.dumps(data), encoding="utf-8")
    report_path = tmp_path / "reader_validation_report.json"
    _, token = validate_for_release(tmp_path, report_path)
    return token, report_path


class HTMLBuilderTests(unittest.TestCase):
    def test_zero_jitter_css_invariants(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            output = tmp_path / "reader.html"
            token, report_path = _make_release_token(tmp_path)

            build_master_reader(
                book_title="Test Book",
                book_subtitle="A Test",
                book_author="Test Author",
                chapters_config=[{
                    "num": 1,
                    "title": "Chapter One",
                    "audio": "./audio/chapter_01.mp3",
                    "aligned_json": str(tmp_path / "book_ch01_aligned_sentences.json"),
                }],
                output_html_path=str(output),
                release_token=token,
                release_report_path=report_path,
            )

            rendered = output.read_text(encoding="utf-8")
            rules = re.findall(r"\.w\.active-word\s*\{(?P<body>.*?)\}", rendered, re.DOTALL)
            self.assertEqual(len(rules), 1)

            forbidden_properties = ("font-weight", "font-size", "letter-spacing", "line-height")
            self.assertFalse(any(
                re.search(rf"(?:^|;)\s*{re.escape(prop)}\s*:", rules[0])
                for prop in forbidden_properties
            ))

    def test_namespaced_storage_keys_and_default_book_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            output = tmp_path / "reader.html"
            token, report_path = _make_release_token(tmp_path)

            build_master_reader(
                book_title="The 48 Laws of Power: Special Edition!",
                book_subtitle="A Comprehensive Guide",
                book_author="Robert Greene",
                chapters_config=[{
                    "num": 1,
                    "title": "Chapter One",
                    "audio": "./audio/chapter_01.mp3",
                    "aligned_json": str(tmp_path / "book_ch01_aligned_sentences.json"),
                }],
                output_html_path=str(output),
                release_token=token,
                release_report_path=report_path,
            )

            rendered = output.read_text(encoding="utf-8")
            self.assertIn('window.__BOOK_ID__ = "the_48_laws_of_power_special_edition";', rendered)
            self.assertIn("const STORAGE_PREFIX = 'reader_' + (window.__BOOK_ID__ || 'default') + '_';", rendered)

            expected_namespaced_keys = (
                "STORAGE_PREFIX + 'active_ch'",
                "STORAGE_PREFIX + 'autoscroll'",
                "STORAGE_PREFIX + 'drawer_open'",
                "STORAGE_PREFIX + 'theme'",
                "STORAGE_PREFIX + 'font_size'",
                "STORAGE_PREFIX + 'last_sentence_c'",
            )
            for key in expected_namespaced_keys:
                self.assertIn(key, rendered)

            unnamespaced_keys = (
                "'book_active_ch'",
                "'book_autoscroll'",
                "'book_drawer_open'",
                "'book_theme'",
                "'book_font_size'",
                "'book_last_sentence_c'",
            )
            for key in unnamespaced_keys:
                self.assertNotIn(key, rendered)

    def test_namespaced_storage_keys_with_custom_book_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            output = tmp_path / "reader.html"
            token, report_path = _make_release_token(tmp_path)

            build_master_reader(
                book_title="Any Book Title",
                book_subtitle="Subtitle",
                book_author="Author",
                chapters_config=[{
                    "num": 1,
                    "title": "Chapter One",
                    "audio": "./audio/chapter_01.mp3",
                    "aligned_json": str(tmp_path / "book_ch01_aligned_sentences.json"),
                }],
                output_html_path=str(output),
                release_token=token,
                release_report_path=report_path,
                book_id="the-housemaid-p0",
            )

            rendered = output.read_text(encoding="utf-8")
            self.assertIn('window.__BOOK_ID__ = "the-housemaid-p0";', rendered)
            self.assertIn("const STORAGE_PREFIX = 'reader_' + (window.__BOOK_ID__ || 'default') + '_';", rendered)
            self.assertIn("STORAGE_PREFIX + 'active_ch'", rendered)
            self.assertIn("STORAGE_PREFIX + 'autoscroll'", rendered)
            self.assertIn("STORAGE_PREFIX + 'drawer_open'", rendered)
            self.assertIn("STORAGE_PREFIX + 'theme'", rendered)
            self.assertIn("STORAGE_PREFIX + 'font_size'", rendered)
            self.assertIn("STORAGE_PREFIX + 'last_sentence_c'", rendered)

    def test_html_builder_rejects_missing_release_authorization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            aligned = tmp_path / "aligned.json"
            aligned.write_text("[]", encoding="utf-8")
            with self.assertRaises(Exception) as ctx:
                build_master_reader(
                    "Test", "Test", "Author", [], str(tmp_path / "reader.html"),
                    release_token=None, release_report_path=tmp_path / "missing.json",
                )
            self.assertIn("ReleaseToken", str(ctx.exception))

    def test_p2_reader_uses_binary_sync_and_sleeps_when_paused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            output = tmp_path / "reader.html"
            token, report_path = _make_release_token(tmp_path)
            build_master_reader(
                "Test", "Study", "Author", [{
                    "num": 1, "title": "One", "audio": "./audio/chapter_01.mp3",
                    "public_audio": "https://cdn.example/book/chapter_01.mp3",
                    "aligned_json": str(tmp_path / "book_ch01_aligned_sentences.json"),
                }], str(output), release_token=token, release_report_path=report_path,
            )
            rendered = output.read_text(encoding="utf-8")
            self.assertIn("function findSentenceAt(time)", rendered)
            self.assertIn("while (low <= high)", rendered)
            self.assertNotIn("for (let u of sentenceUnits)", rendered)
            self.assertIn("cancelAnimationFrame(syncFrameId)", rendered)
            self.assertIn("document.addEventListener('visibilitychange'", rendered)
            self.assertIn("data-public-audio=\"https://cdn.example/book/chapter_01.mp3\"", rendered)

    def test_p2_reader_has_native_speed_shadowing_and_anki_tsv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            output = tmp_path / "reader.html"
            token, report_path = _make_release_token(tmp_path)
            build_master_reader(
                "Test", "Study", "Author", [{
                    "num": 1, "title": "One", "audio": "./audio/chapter_01.mp3",
                    "aligned_json": str(tmp_path / "book_ch01_aligned_sentences.json"),
                }], str(output), release_token=token, release_report_path=report_path,
            )
            rendered = output.read_text(encoding="utf-8")
            self.assertIn("audio.playbackRate = rate", rendered)
            self.assertIn("audio.preservesPitch = true", rendered)
            for state in ("'idle'", "'playing'", "'pause_buffer'", "'replaying'"):
                self.assertIn(state, rendered)
            self.assertIn("text/tab-separated-values;charset=utf-8", rendered)
            self.assertIn("'[背景]。你说：“'", rendered)
