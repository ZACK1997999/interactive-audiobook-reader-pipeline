"""
Full End-to-End Industrial Pipeline Runner for 'Fourth Wing'.

Coordinates:
1. Apple Silicon MLX Whisper acoustic word timestamp extraction (Ch 1-39).
2. Parallel high-throughput Agy linguistic analysis (Ch 1-39).
3. Real-time dynamic alignment as chapter pairs become ready.
4. Deterministic quality gate validation and release token generation.
5. Compilation of standalone master interactive reader (HTML).
6. Smoke checking and publication manifest updates.
"""

from __future__ import annotations

import os
import sys
import time
import json
import subprocess
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

PIPELINE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_DIR))

from acoustic_whisper import run_mlx_acoustic_extraction
from agy_linguistic_worker import process_canonical_sentences, PROMPT_PATH
from dynamic_aligner import align_sentences_with_audio
from validate_outputs import validate_for_release
from html_builder import build_master_reader
import shutil
from quality_gate import smoke_check_html, validate_semantic_review
from run_manifest import update_manifest
from artifact_io import atomic_write_json
from chapter_metadata import load_chapter_metadata

BOOK_DIR = Path('/Users/lindy/Vault/audiobook/Fourth Wing').resolve()
AUDIO_DIR = BOOK_DIR / 'audio'
TOTAL_CHAPTERS = 39


def _is_acoustic_ready(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 1000:
        return False
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return (isinstance(data, dict) and bool(data.get('words'))) or (isinstance(data, list) and bool(data))
    except Exception:
        return False


def _is_analysis_ready(path: Path, canonical_path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 100:
        return False
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        canonical = json.loads(canonical_path.read_text(encoding='utf-8'))
        if not isinstance(data, list) or len(data) != len(canonical):
            return False
        for gen, src in zip(data, canonical):
            if gen.get('id') != src.get('id') or gen.get('text') != src.get('text'):
                return False
            if not isinstance(gen.get('trans'), str) or not gen['trans'].strip():
                return False
            if not isinstance(gen.get('vocab'), list):
                return False
        return True
    except Exception:
        return False


def run_acoustic_loop():
    print('=== [Acoustic Worker Thread Started] ===', flush=True)
    for ch in range(1, TOTAL_CHAPTERS + 1):
        prefix = f'fourth_wing_ch{ch:02d}'
        audio_file = AUDIO_DIR / f'chapter_{ch:02d}.mp3'
        acoustic_out = AUDIO_DIR / f'{prefix}_acoustic_words.json'

        if _is_acoustic_ready(acoustic_out):
            print(f'[Acoustic] Chapter {ch:02d} already complete: {acoustic_out.name}', flush=True)
            continue

        print(f'[Acoustic] Processing Chapter {ch:02d}/{TOTAL_CHAPTERS} ({audio_file.name})...', flush=True)
        t0 = time.time()
        try:
            run_mlx_acoustic_extraction(str(audio_file), str(acoustic_out))
            elapsed = time.time() - t0
            print(f'[Acoustic] Chapter {ch:02d} finished in {elapsed:.1f}s -> {acoustic_out.name}', flush=True)
        except Exception as exc:
            print(f'[Acoustic ERROR] Chapter {ch:02d} failed: {exc}', file=sys.stderr, flush=True)
    print('=== [Acoustic Worker Thread Finished All Chapters] ===', flush=True)


def process_chapter_linguistics(ch: int, base_prompt: str):
    prefix = f'fourth_wing_ch{ch:02d}'
    canonical_file = BOOK_DIR / f'{prefix}_canonical_sentences.json'
    analysis_out = BOOK_DIR / f'{prefix}_full_analysis.json'

    if _is_analysis_ready(analysis_out, canonical_file):
        print(f'[Linguistic] Chapter {ch:02d} already complete.', flush=True)
        return ch, True

    if not canonical_file.is_file():
        print(f'[Linguistic ERROR] Chapter {ch:02d} missing canonical file: {canonical_file}', file=sys.stderr, flush=True)
        return ch, False

    canonical_data = json.loads(canonical_file.read_text(encoding='utf-8'))
    print(f'[Linguistic] Processing Chapter {ch:02d} ({len(canonical_data)} sentences)...', flush=True)
    t0 = time.time()
    try:
        analyzed_data = process_canonical_sentences(
            canonical_data=canonical_data,
            base_prompt=base_prompt,
            cwd=BOOK_DIR,
            chunk_size=40,
            timeout=3700,
            max_batch_attempts=3,
            max_workers=3,
        )
        atomic_write_json(analysis_out, analyzed_data)
        elapsed = time.time() - t0
        print(f'[Linguistic] Chapter {ch:02d} complete in {elapsed:.1f}s -> {analysis_out.name}', flush=True)
        return ch, True
    except Exception as exc:
        print(f'[Linguistic ERROR] Chapter {ch:02d} failed: {exc}', file=sys.stderr, flush=True)
        return ch, False


def run_alignment_check(ch: int) -> bool:
    prefix = f'fourth_wing_ch{ch:02d}'
    canonical_path = BOOK_DIR / f'{prefix}_canonical_sentences.json'
    analysis_path = BOOK_DIR / f'{prefix}_full_analysis.json'
    acoustic_path = AUDIO_DIR / f'{prefix}_acoustic_words.json'
    aligned_path = BOOK_DIR / f'{prefix}_aligned_sentences.json'

    if not _is_analysis_ready(analysis_path, canonical_path):
        return False
    if not _is_acoustic_ready(acoustic_path):
        return False

    needs_align = not aligned_path.is_file()
    if not needs_align:
        if (
            acoustic_path.stat().st_mtime > aligned_path.stat().st_mtime
            or analysis_path.stat().st_mtime > aligned_path.stat().st_mtime
        ):
            needs_align = True

    if needs_align:
        print(f'[Alignment] Aligning Chapter {ch:02d} ({prefix})...', flush=True)
        t0 = time.time()
        align_sentences_with_audio(str(acoustic_path), str(analysis_path), str(aligned_path))
        print(f'[Alignment] Chapter {ch:02d} aligned in {time.time() - t0:.2f}s -> {aligned_path.name}', flush=True)
    return True


def run_pipeline():
    print('================================================================================', flush=True)
    print('      Starting Industrial End-to-End Pipeline for Fourth Wing (39 Chapters)     ', flush=True)
    print('================================================================================', flush=True)

    base_prompt = PROMPT_PATH.read_text(encoding='utf-8')

    # Start Acoustic Worker in a dedicated background thread
    acoustic_thread = threading.Thread(target=run_acoustic_loop, daemon=True, name='AcousticWorker')
    acoustic_thread.start()

    # Run Linguistic Analysis across chapters
    print('=== [Starting Linguistic Processing Pool] ===', flush=True)
    for ch in range(1, TOTAL_CHAPTERS + 1):
        process_chapter_linguistics(ch, base_prompt)
        # Attempt alignment if acoustic is already ready
        run_alignment_check(ch)

    print('=== [Waiting for Acoustic Extraction to Complete] ===', flush=True)
    acoustic_thread.join()

    # Align any remaining chapters
    print('=== [Finalizing Dynamic Alignment Across All 39 Chapters] ===', flush=True)
    all_aligned = True
    for ch in range(1, TOTAL_CHAPTERS + 1):
        success = run_alignment_check(ch)
        if not success:
            print(f'[WARNING] Chapter {ch:02d} could not be aligned!', file=sys.stderr, flush=True)
            all_aligned = False

    if not all_aligned:
        print('[ERROR] Not all chapters were aligned successfully. Halting release.', file=sys.stderr, flush=True)
        return 1

    # Quality Gate Validation & Compilation
    print("\n=== [Running Release Quality Gate] ===", flush=True)
    report_path = BOOK_DIR / "reader_validation_report.json"
    report, release_token = validate_for_release(BOOK_DIR, report_path)
    if release_token is None:
        print(f"[ERROR] Release gate blocked! See report at: {report_path}", file=sys.stderr, flush=True)
        return 1

    print(f"[Quality Gate Passed] Generated Release Token: {release_token}", flush=True)

    # Build Master Interactive Reader
    print("\n=== [Compiling Master Multi-Chapter Interactive Reader HTML] ===", flush=True)
    master_html_path = BOOK_DIR / "Fourth_Wing_Interactive_Reader.html"
    metadata_path = BOOK_DIR / "chapter_metadata.json"
    chapter_metadata = load_chapter_metadata(metadata_path, expected_chapters=range(1, TOTAL_CHAPTERS + 1))

    chapters_config = []
    for ch in range(1, TOTAL_CHAPTERS + 1):
        prefix = f"fourth_wing_ch{ch:02d}"
        aligned_path = BOOK_DIR / f"{prefix}_aligned_sentences.json"
        meta = chapter_metadata[ch]
        chapters_config.append({
            "num": ch,
            "title": meta["title"],
            "audio": f"./audio/chapter_{ch:02d}.mp3",
            "aligned_json": str(aligned_path),
            **meta,
        })

    build_master_reader(
        book_title="Fourth Wing",
        book_subtitle="Bilingual Synchronized Reader",
        book_author="Rebecca Yarros",
        chapters_config=chapters_config,
        output_html_path=str(master_html_path),
        release_token=release_token,
        release_report_path=str(report_path),
        book_id="fourth-wing",
    )

    # Semantic Quality Review Check
    print("\n=== [Running Semantic Quality Gate Check] ===", flush=True)
    semantic_path = BOOK_DIR / "reader_semantic_review.json"
    if semantic_path.exists():
        sem_check = validate_semantic_review(semantic_path, required_chapters=[1, 18, 25, 36, 39])
        if sem_check["status"] != "passed":
            print(f"[ERROR] Semantic review validation failed: {sem_check['errors']}", file=sys.stderr, flush=True)
            return 1
        print(f"[SUCCESS] Semantic Review Verified with {sem_check['sample_count']} sampled chapters!", flush=True)
    else:
        print("[WARNING] reader_semantic_review.json not found! Semantic quality check skipped.", file=sys.stderr, flush=True)

    # Smoke Check on Master HTML
    print("\n=== [Running Reader Smoke Check] ===", flush=True)
    smoke = smoke_check_html(master_html_path, expected_chapters=TOTAL_CHAPTERS)
    if smoke["status"] != "passed":
        print(f"[ERROR] Reader smoke check failed: {smoke['errors']}", file=sys.stderr, flush=True)
        return 1

    print(f"\n[SUCCESS] Reader Smoke Check Passed with 0 errors! Total chapters: {smoke['chapter_count']}", flush=True)
    print(f"[SUCCESS] Standalone Interactive Reader compiled at: {master_html_path}", flush=True)

    # Synchronize & Deploy to Audible Portal
    print("\n=== [Deploying & Synchronizing to Audible Central Portal] ===", flush=True)
    audible_book_dir = Path("/Users/lindy/Vault/Audible/books/fourth-wing")
    audible_book_dir.mkdir(parents=True, exist_ok=True)
    audible_html_path = audible_book_dir / "index.html"
    shutil.copy2(master_html_path, audible_html_path)

    # Ensure Audio Symlink
    audible_audio_link = audible_book_dir / "audio"
    if not audible_audio_link.exists():
        try:
            audible_audio_link.symlink_to(BOOK_DIR / "audio", target_is_directory=True)
            print(f"[Audible Portal] Created audio symlink -> {audible_audio_link}", flush=True)
        except Exception as e:
            print(f"[WARNING] Could not create audio symlink: {e}", file=sys.stderr, flush=True)

    # Run Smoke Check on Deployed Portal Reader
    portal_smoke = smoke_check_html(audible_html_path, expected_chapters=TOTAL_CHAPTERS)
    if portal_smoke["status"] != "passed":
        print(f"[ERROR] Audible portal smoke check failed: {portal_smoke['errors']}", file=sys.stderr, flush=True)
        return 1
    print(f"[SUCCESS] Audible Portal Deployment Verified at {audible_html_path}", flush=True)

    print("================================================================================", flush=True)
    print("                     ALL 39 CHAPTERS PROCESSED SUCCESSFULLY                     ", flush=True)
    print("================================================================================", flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(run_pipeline())
