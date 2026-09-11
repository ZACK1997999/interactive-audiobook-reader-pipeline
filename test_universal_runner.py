"""Unit and integration tests for universal_runner.py."""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from universal_runner import (
    sanitize_slug,
    detect_book_prefix,
    infer_chapter_role_and_label,
    discover_epub_chapters,
    build_reader_pipeline,
)


def _create_mock_epub(epub_path: Path) -> None:
    container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""

    content_opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Test Sample Book</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:language>en</dc:language>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="cover-image" href="cover.jpg" media-type="image/jpeg"/>
    <item id="cover" href="cover.html" media-type="application/xhtml+xml"/>
    <item id="toc" href="contents.html" media-type="application/xhtml+xml"/>
    <item id="pref" href="preface.html" media-type="application/xhtml+xml"/>
    <item id="ch1" href="ch01.html" media-type="application/xhtml+xml"/>
    <item id="ch2" href="ch02.html" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover"/>
    <itemref idref="toc"/>
    <itemref idref="pref"/>
    <itemref idref="ch1"/>
    <itemref idref="ch2"/>
  </spine>
</package>"""

    toc_ncx = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <navMap>
    <navPoint id="np1" playOrder="1">
      <navLabel><text>Author's Preface</text></navLabel>
      <content src="preface.html"/>
    </navPoint>
    <navPoint id="np2" playOrder="2">
      <navLabel><text>I. The Beginning</text></navLabel>
      <content src="ch01.html"/>
    </navPoint>
    <navPoint id="np3" playOrder="3">
      <navLabel><text>II. The Continuation</text></navLabel>
      <content src="ch02.html"/>
    </navPoint>
  </navMap>
</ncx>"""

    cover_html = "<html><body><p>Cover</p></body></html>"
    contents_html = "<html><body><h1>Table of Contents</h1><p>Chapter list</p></body></html>"
    pref_html = "<html><body><h1>Author's Preface</h1><p>This is a substantive preface introducing the core thesis of the book with thoughtful exposition.</p></body></html>"
    ch1_html = "<html><body><h1>I. The Beginning</h1><p>First sentence of chapter one. Second sentence explaining concepts clearly and thoroughly.</p></body></html>"
    ch2_html = "<html><body><h1>II. The Continuation</h1><p>The journey continues into deeper territory with further discussion and rigorous analysis.</p></body></html>"

    with zipfile.ZipFile(epub_path, "w") as zf:
        zf.writestr("META-INF/container.xml", container_xml)
        zf.writestr("OEBPS/content.opf", content_opf)
        zf.writestr("OEBPS/toc.ncx", toc_ncx)
        zf.writestr("OEBPS/cover.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00")
        zf.writestr("OEBPS/cover.html", cover_html)
        zf.writestr("OEBPS/contents.html", contents_html)
        zf.writestr("OEBPS/preface.html", pref_html)
        zf.writestr("OEBPS/ch01.html", ch1_html)
        zf.writestr("OEBPS/ch02.html", ch2_html)


class UniversalRunnerTests(unittest.TestCase):
    def test_sanitize_slug(self):
        self.assertEqual(sanitize_slug("Denationalization of Money"), "denationalization_of_money")
        self.assertEqual(sanitize_slug("Fourth Wing (Book #1)!"), "fourth_wing_book_1")
        self.assertEqual(sanitize_slug(""), "book")

    def test_detect_book_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.assertEqual(detect_book_prefix(d, "fallback"), "fallback")
            (d / "denationalization_ch00_canonical_sentences.json").write_text("[]", encoding="utf-8")
            self.assertEqual(detect_book_prefix(d, "fallback"), "denationalization")

    def test_infer_chapter_role_and_label(self):
        role, disp, label = infer_chapter_role_and_label(0, "Editorial Preface", "OEBPS/Text/preface.html")
        self.assertEqual(role, "preface")
        self.assertIsNone(disp)
        self.assertEqual(label, "Editorial Preface")

        role, disp, label = infer_chapter_role_and_label(1, "I. The Practical Proposal", "OEBPS/Text/ch01.html")
        self.assertEqual(role, "chapter")
        self.assertEqual(disp, 1)
        self.assertEqual(label, "Chapter 1")

        role, disp, label = infer_chapter_role_and_label(2, "Chapter 12: Advanced Topics", "OEBPS/Text/ch12.html")
        self.assertEqual(role, "chapter")
        self.assertEqual(disp, 12)
        self.assertEqual(label, "Chapter 12")

        role, disp, label = infer_chapter_role_and_label(3, "Questions for Discussion", "OEBPS/Text/questions.html")
        self.assertEqual(role, "appendix")
        self.assertIsNone(disp)
        self.assertEqual(label, "Questions")

    def test_discover_epub_chapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            epub_path = Path(tmp) / "test.epub"
            _create_mock_epub(epub_path)

            meta, chapters, cover = discover_epub_chapters(epub_path, min_chars=50)
            self.assertEqual(meta.get("title"), "Test Sample Book")
            self.assertEqual(meta.get("creator"), "Test Author")
            self.assertEqual(cover, "OEBPS/cover.jpg")

            # cover and contents are filtered out; preface, ch1, ch2 are kept
            self.assertEqual(len(chapters), 3)
            self.assertEqual(chapters[0]["title"], "Author's Preface")
            self.assertEqual(chapters[1]["title"], "I. The Beginning")
            self.assertEqual(chapters[2]["title"], "II. The Continuation")

    @patch("universal_runner.process_canonical_sentences")
    def test_build_reader_pipeline_text_only_end_to_end(self, mock_process_linguistics):
        def fake_linguistics(canonical_data, **kwargs):
            return [
                {
                    "id": item["id"],
                    "elem_idx": item.get("elem_idx", 0),
                    "tag": item.get("tag", "p"),
                    "text": item["text"],
                    "trans": f"【译文】{item['text']}",
                    "vocab": [],
                    "is_heading": item.get("is_heading", False),
                }
                for item in canonical_data
            ]

        mock_process_linguistics.side_effect = fake_linguistics

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            epub_path = root / "sample.epub"
            book_dir = root / "output_book"
            _create_mock_epub(epub_path)

            out_html = build_reader_pipeline(
                epub_path=epub_path,
                book_dir=book_dir,
                text_only=True,
                concurrency=2,
                min_chars=50,
                open_in_browser=False,
            )

            self.assertTrue(out_html.is_file())
            self.assertGreater(out_html.stat().st_size, 1000)

            # Check audio_content_profile.json
            profile = json.loads((book_dir / "audio_content_profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["audio_content_mode"], "text_only")

            # Check chapter_metadata.json
            meta_json = json.loads((book_dir / "chapter_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(len(meta_json["chapters"]), 3)

            # Check validation report
            rep = json.loads((book_dir / "reader_validation_report.json").read_text(encoding="utf-8"))
            self.assertTrue(rep["release_ready"])
            self.assertEqual(rep["audio_content_mode"], "text_only")


if __name__ == "__main__":
    unittest.main()
