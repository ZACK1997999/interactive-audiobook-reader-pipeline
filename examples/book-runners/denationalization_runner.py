"""
End-to-End Pipeline Runner for Friedrich Hayek's 'Denationalisation of Money'.

Coordinates:
1. EPUB extraction of all front matter, 25 chapters, and discussion questions.
2. Text-only audio content profile and chapter metadata registration.
3. Parallel high-throughput linguistic analysis (Chinese translation + B2/C1/C2 vocabulary).
4. Deterministic text-only aligned sentence synthesis.
5. Release gate validation and cryptographic ReleaseToken issuance.
6. Standalone Apple Books-grade interactive HTML reader compilation.
7. Automated smoke checks and local inspection readiness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_DIR))

from extract_epub import extract_chapter_from_epub
from agy_linguistic_worker import process_canonical_sentences, PROMPT_PATH, verify_analysis
from validate_outputs import validate
from release_token import issue_release_token
from html_builder import build_master_reader
from quality_gate import smoke_check_html
from artifact_io import atomic_write_json, atomic_write_text

DEFAULT_EPUB = Path(os.path.expanduser(
    "~/Downloads/Denationalization of Money (Friedrich August Hayek) (z-library.sk, 1lib.sk, z-lib.sk).epub"
))
DEFAULT_BOOK_DIR = Path(os.path.expanduser(
    "~/Vault/audiobook/Denationalisation of Money"
))

TRACKS = [
    (0, "preface", None, "Editorial Preface by Jeffrey A. Tucker", "OEBPS/Text/TuckerPreface.html", "Editorial Preface"),
    (1, "preface", None, "Preface to the First Edition", "OEBPS/Text/FirstEditionPreface.html", "Preface (1st Ed)"),
    (2, "preface", None, "Preface to the Second (Extended) Edition", "OEBPS/Text/SecondEditionPreface.html", "Preface (2nd Ed)"),
    (3, "introduction", None, "Author's Introduction", "OEBPS/Text/AuthorsIntroduction.html", "Author's Intro"),
    (4, "preface", None, "A Note to the Second Edition", "OEBPS/Text/SecondEditionNote.html", "Note (2nd Ed)"),
    (5, "introduction", None, "Introduction to the Third Edition", "OEBPS/Text/ThirdEditionIntroduction.html", "Intro (3rd Ed)"),
    (6, "chapter", 1, "I. The Practical Proposal", "OEBPS/Text/chapter01.html", "Chapter 1"),
    (7, "chapter", 2, "II. The Generalization of the Underlying Principle", "OEBPS/Text/chapter02.html", "Chapter 2"),
    (8, "chapter", 3, "III. The Origin of the Government Prerogative of Making Money", "OEBPS/Text/chapter03.html", "Chapter 3"),
    (9, "chapter", 4, "IV. The Persistent Abuse of the Government Prerogative", "OEBPS/Text/chapter04.html", "Chapter 4"),
    (10, "chapter", 5, "V. The Mystique of Legal Tender", "OEBPS/Text/chapter05.html", "Chapter 5"),
    (11, "chapter", 6, "VI. The Confusion About Gresham's Law", "OEBPS/Text/chapter06.html", "Chapter 6"),
    (12, "chapter", 7, "VII. The Limited Experience with Parallel Currencies and Trade Coins", "OEBPS/Text/chapter07.html", "Chapter 7"),
    (13, "chapter", 8, "VIII. Putting Private Token Money into Circulation", "OEBPS/Text/chapter08.html", "Chapter 8"),
    (14, "chapter", 9, "IX. Competition Between Banks Issuing Different Currencies", "OEBPS/Text/chapter09.html", "Chapter 9"),
    (15, "chapter", 10, "X. A Digression on the Definition of Money", "OEBPS/Text/chapter10.html", "Chapter 10"),
    (16, "chapter", 11, "XI. The Possibility of Controlling The Value of A Competitive Currency", "OEBPS/Text/chapter11.html", "Chapter 11"),
    (17, "chapter", 12, "XII. Which Sort of Currency Would The Public Select?", "OEBPS/Text/chapter12.html", "Chapter 12"),
    (18, "chapter", 13, "XIII. Which Value of Money?", "OEBPS/Text/chapter13.html", "Chapter 13"),
    (19, "chapter", 14, "XIV. The Uselessness of the Quantity Theory For Our Purposes", "OEBPS/Text/chapter14.html", "Chapter 14"),
    (20, "chapter", 15, "XV. The Desirable Behavior of the Supply of Currency", "OEBPS/Text/chapter15.html", "Chapter 15"),
    (21, "chapter", 16, "XVI. Free Banking", "OEBPS/Text/chapter16.html", "Chapter 16"),
    (22, "chapter", 17, "XVII. No More General Inflation Or Deflation?", "OEBPS/Text/chapter17.html", "Chapter 17"),
    (23, "chapter", 18, "XVIII. Monetary Policy Neither Desirable Nor Possible", "OEBPS/Text/chapter18.html", "Chapter 18"),
    (24, "chapter", 19, "XIX. A Better Discipline Than Fixed Rates of Exchange", "OEBPS/Text/chapter19.html", "Chapter 19"),
    (25, "chapter", 20, "XX. Should There Be Separate Currency Areas?", "OEBPS/Text/chapter20.html", "Chapter 20"),
    (26, "chapter", 21, "XXI. The Effects on Government Finance and Expenditure", "OEBPS/Text/chapter21.html", "Chapter 21"),
    (27, "chapter", 22, "XXII. Problems of Transition", "OEBPS/Text/chapter22.html", "Chapter 22"),
    (28, "chapter", 23, "XXIII. Protection against the State", "OEBPS/Text/chapter23.html", "Chapter 23"),
    (29, "chapter", 24, "XXIV. The Long-Run Prospects", "OEBPS/Text/chapter24.html", "Chapter 24"),
    (30, "chapter", 25, "XXV. Conclusions", "OEBPS/Text/chapter25.html", "Chapter 25"),
    (31, "appendix", None, "Questions for Discussion", "OEBPS/Text/questions.html", "Questions"),
]


def _is_analysis_valid(analysis_path: Path, canonical_path: Path) -> bool:
    if not analysis_path.is_file() or not canonical_path.is_file():
        return False
    try:
        c_data = json.loads(canonical_path.read_text(encoding="utf-8"))
        a_data = json.loads(analysis_path.read_text(encoding="utf-8"))
        if not isinstance(a_data, list) or len(a_data) != len(c_data):
            return False
        verify_analysis(a_data, c_data)
        return True
    except Exception:
        return False


def setup_book_scaffolding(book_dir: Path, epub_path: Path):
    book_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Copy EPUB
    dest_epub = book_dir / "Denationalization_of_Money.epub"
    if not dest_epub.exists() and epub_path.exists():
        dest_epub.write_bytes(epub_path.read_bytes())
        print(f"[Setup] EPUB copied to {dest_epub}")

    # 2. Extract cover
    cover_path = book_dir / "cover.jpg"
    if not cover_path.exists() and epub_path.exists():
        with zipfile.ZipFile(epub_path, "r") as z:
            if "OEBPS/Images/cover.jpg" in z.namelist():
                cover_path.write_bytes(z.read("OEBPS/Images/cover.jpg"))
                print(f"[Setup] Extracted cover to {cover_path}")

    # 3. audio_content_profile.json
    profile_path = book_dir / "audio_content_profile.json"
    atomic_write_json(profile_path, {
        "schema_version": 1,
        "audio_content_mode": "text_only"
    })
    print(f"[Setup] Wrote text_only audio_content_profile.json")

    # 4. chapter_metadata.json
    metadata_rows = []
    for num, role, disp_num, title, _, label in TRACKS:
        row = {
            "chapter": num,
            "role": role,
            "title": title,
            "label": label,
        }
        if disp_num is not None:
            row["display_number"] = disp_num
        metadata_rows.append(row)

    metadata_path = book_dir / "chapter_metadata.json"
    atomic_write_json(metadata_path, {
        "schema_version": 1,
        "chapters": metadata_rows
    })
    print(f"[Setup] Wrote chapter_metadata.json ({len(metadata_rows)} tracks)")


def extract_all_sentences(book_dir: Path, epub_path: Path):
    print(f"\n=== [Stage 1: EPUB Sentence Extraction ({len(TRACKS)} tracks)] ===", flush=True)
    for num, role, disp_num, title, internal_path, label in TRACKS:
        prefix = f"denationalization_ch{num:02d}"
        can_path = book_dir / f"{prefix}_canonical_sentences.json"
        if can_path.is_file() and can_path.stat().st_size > 50:
            continue
        extract_chapter_from_epub(str(epub_path), internal_path, str(can_path))
    print("[Stage 1] All canonical sentences extracted.")


def process_linguistics_for_track(num: int, book_dir: Path, base_prompt: str, max_workers: int = 4) -> bool:
    prefix = f"denationalization_ch{num:02d}"
    can_path = book_dir / f"{prefix}_canonical_sentences.json"
    ana_path = book_dir / f"{prefix}_full_analysis.json"

    if _is_analysis_valid(ana_path, can_path):
        return True

    if not can_path.is_file():
        print(f"[Linguistic ERROR] Track {num:02d} missing canonical: {can_path}", file=sys.stderr)
        return False

    can_data = json.loads(can_path.read_text(encoding="utf-8"))
    print(f"[Linguistic] Processing Track {num:02d} ({len(can_data)} sentences)...", flush=True)
    t0 = time.time()
    try:
        analyzed_data = process_canonical_sentences(
            canonical_data=can_data,
            base_prompt=base_prompt,
            cwd=book_dir,
            chunk_size=40,
            timeout=3600,
            max_batch_attempts=3,
            max_workers=max_workers,
        )
        atomic_write_json(ana_path, analyzed_data)
        elapsed = time.time() - t0
        print(f"[Linguistic] Track {num:02d} complete in {elapsed:.1f}s -> {ana_path.name}", flush=True)
        return True
    except Exception as exc:
        print(f"[Linguistic ERROR] Track {num:02d} failed: {exc}", file=sys.stderr, flush=True)
        return False


def synthesize_aligned_sentences(book_dir: Path):
    print(f"\n=== [Stage 3: Synthesizing Aligned Sentences (Text-Only)] ===", flush=True)
    for num, _, _, _, _, _ in TRACKS:
        prefix = f"denationalization_ch{num:02d}"
        can_path = book_dir / f"{prefix}_canonical_sentences.json"
        ana_path = book_dir / f"{prefix}_full_analysis.json"
        alg_path = book_dir / f"{prefix}_aligned_sentences.json"

        c_data = json.loads(can_path.read_text(encoding="utf-8"))
        a_data = json.loads(ana_path.read_text(encoding="utf-8"))
        c_map = {item["id"]: item for item in c_data}

        aligned_items = []
        for item in a_data:
            cid = item["id"]
            c_info = c_map[cid]
            aligned_items.append({
                "id": cid,
                "elem_idx": c_info["elem_idx"],
                "tag": c_info["tag"],
                "text": item["text"],
                "trans": item["trans"],
                "vocab": item.get("vocab", []),
                "is_heading": c_info.get("is_heading", False),
                "has_audio_match": False,
                "start": None,
                "end": None,
                "word_spans": []
            })
        atomic_write_json(alg_path, aligned_items)
    print("[Stage 3] All aligned sentences synthesized.")


def run_full_pipeline(book_dir: Path = DEFAULT_BOOK_DIR, epub_path: Path = DEFAULT_EPUB, max_workers: int = 4):
    t_start = time.time()
    print("=====================================================================")
    print(" Denationalisation of Money — Text-Only Interactive Reader Pipeline ")
    print("=====================================================================")
    print(f"EPUB: {epub_path}")
    print(f"Target Book Dir: {book_dir}\n")

    setup_book_scaffolding(book_dir, epub_path)
    extract_all_sentences(book_dir, epub_path)

    print(f"\n=== [Stage 2: High-Throughput Linguistic Analysis via agy ({max_workers} parallel workers)] ===", flush=True)
    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    from concurrent.futures import as_completed
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_linguistics_for_track, num, book_dir, base_prompt, 1): (num, label)
            for num, _, _, title, _, label in TRACKS
        }
        for f in as_completed(futures):
            num, label = futures[f]
            ok = f.result()
            if not ok:
                raise RuntimeError(f"Linguistic analysis failed on track {num:02d} ({label})")

    synthesize_aligned_sentences(book_dir)

    print(f"\n=== [Stage 4: Quality Gate & Validation] ===", flush=True)
    rep_path = book_dir / "reader_validation_report.json"
    code = validate(book_dir, rep_path)
    if code != 0:
        raise RuntimeError("Validation report failed quality gate")
    report = json.loads(rep_path.read_text(encoding="utf-8"))
    token = issue_release_token(book_dir, rep_path, report)
    print(f"[Stage 4] ReleaseToken issued: {token.nonce[:16]}... (Report validated)")

    print(f"\n=== [Stage 5: Master Interactive Reader Compilation] ===", flush=True)
    out_html = book_dir / "Denationalisation_of_Money_Interactive_Reader.html"
    chapters_config = []
    for num, role, disp_num, title, _, label in TRACKS:
        cfg = {
            "num": num,
            "title": title,
            "role": role,
            "label": label,
            "audio": "",
            "aligned_json": str(book_dir / f"denationalization_ch{num:02d}_aligned_sentences.json")
        }
        if disp_num is not None:
            cfg["display_number"] = disp_num
        chapters_config.append(cfg)

    build_master_reader(
        book_title="Denationalisation of Money",
        book_subtitle="The Argument Refined: An Analysis of the Theory and Practice of Concurrent Currencies",
        book_author="Friedrich August Hayek",
        chapters_config=chapters_config,
        output_html_path=str(out_html),
        release_token=token,
        release_report_path=str(rep_path),
        book_id="denationalisation-of-money"
    )

    print(f"\n=== [Stage 6: Reader Smoke Check] ===", flush=True)
    smoke = smoke_check_html(out_html, expected_chapters=len(TRACKS))
    if smoke["status"] != "passed":
        raise RuntimeError(f"HTML smoke check failed: {smoke['errors']}")
    print(f"[Stage 6] Smoke check passed: 100% compliant ({smoke['chapter_count']} chapters, {out_html.stat().st_size:,} bytes)")

    elapsed = time.time() - t_start
    print("\n=====================================================================")
    print(f" PIPELINE COMPLETE in {elapsed:.1f}s")
    print(f" Standalone Reader: {out_html}")
    print("=====================================================================")
    return out_html


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Denationalisation of Money reader pipeline")
    parser.add_argument("--workers", type=int, default=4, help="Max parallel workers for agy")
    parser.add_argument("--book-dir", type=str, default=str(DEFAULT_BOOK_DIR))
    args = parser.parse_args()
    run_full_pipeline(book_dir=Path(args.book_dir), max_workers=args.workers)
