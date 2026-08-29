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
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

PIPELINE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_DIR))

from acoustic_whisper import ACOUSTIC_PROFILE_VERSION, run_mlx_acoustic_extraction
from acoustic_repair import repair_acoustic_gaps
from agy_linguistic_worker import process_canonical_sentences, PROMPT_PATH
from dynamic_aligner import align_sentences_with_audio
from validate_outputs import validate_for_release
from html_builder import build_master_reader
from quality_gate import smoke_check_html, validate_semantic_review
from manifests import build_audio_manifest, write_audio_manifest
from run_manifest import update_manifest
from artifact_io import atomic_write_json
from chapter_metadata import load_chapter_metadata

BOOK_DIR = Path('/Users/lindy/Vault/audiobook/Fourth Wing').resolve()
AUDIO_DIR = BOOK_DIR / 'audio'
TOTAL_CHAPTERS = 39


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _chapter_hashes(ch: int):
    prefix = f"fourth_wing_ch{ch:02d}"
    paths = {
        "canonical_sha256": BOOK_DIR / f"{prefix}_canonical_sentences.json",
        "analysis_sha256": BOOK_DIR / f"{prefix}_full_analysis.json",
        "acoustic_sha256": AUDIO_DIR / f"{prefix}_acoustic_words.json",
        "aligned_sha256": BOOK_DIR / f"{prefix}_aligned_sentences.json",
        "audio_sha256": AUDIO_DIR / f"chapter_{ch:02d}.mp3",
    }
    return {key: _sha256(path) if path.is_file() else None for key, path in paths.items()}


def _write_run_manifest(status: str):
    rows = []
    for ch in range(1, TOTAL_CHAPTERS + 1):
        rows.append({"chapter": ch, **_chapter_hashes(ch)})
    input_files = [("prompt", PROMPT_PATH)]
    for ch in range(1, TOTAL_CHAPTERS + 1):
        input_files.extend([
            ("canonical", BOOK_DIR / f"fourth_wing_ch{ch:02d}_canonical_sentences.json"),
            ("audio", AUDIO_DIR / f"chapter_{ch:02d}.mp3"),
        ])
    return update_manifest(BOOK_DIR, rows, status=status, input_files=input_files)


def _alignment_is_current(ch: int, aligned_path: Path) -> bool:
    manifest_path = BOOK_DIR / "reader_run_manifest.json"
    if not aligned_path.is_file() or not manifest_path.is_file():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = next(item for item in manifest.get("chapters", []) if item.get("chapter") == ch)
    except (OSError, ValueError, TypeError, StopIteration):
        return False
    current = _chapter_hashes(ch)
    return all(entry.get(key) == value for key, value in current.items())


def _is_acoustic_ready(path: Path, *, require_current_profile: bool = False) -> bool:
    if not path.is_file() or path.stat().st_size < 1000:
        return False
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            if require_current_profile and data.get('acoustic_profile_version') != ACOUSTIC_PROFILE_VERSION:
                return False
            return bool(data.get('words'))
        return bool(data) and not require_current_profile
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

        # A non-empty legacy artifact is not safe input for a new run.  The
        # acoustic profile is part of the reproducibility contract: if it is
        # stale, regenerate it before alignment or bounded repair.
        if _is_acoustic_ready(acoustic_out, require_current_profile=True):
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
    if not _is_acoustic_ready(acoustic_path, require_current_profile=True):
        return False

    needs_align = not _alignment_is_current(ch, aligned_path)

    if needs_align:
        print(f'[Alignment] Aligning Chapter {ch:02d} ({prefix})...', flush=True)
        t0 = time.time()
        align_sentences_with_audio(str(acoustic_path), str(analysis_path), str(aligned_path))
        print(f'[Alignment] Chapter {ch:02d} aligned in {time.time() - t0:.2f}s -> {aligned_path.name}', flush=True)
    return True


def run_bounded_acoustic_repairs():
    print('=== [Repairing Bounded Acoustic Failure Windows] ===', flush=True)
    results = []
    for ch in range(1, TOTAL_CHAPTERS + 1):
        prefix = f'fourth_wing_ch{ch:02d}'
        result = repair_acoustic_gaps(
            AUDIO_DIR / f'chapter_{ch:02d}.mp3',
            AUDIO_DIR / f'{prefix}_acoustic_words.json',
            BOOK_DIR / f'{prefix}_full_analysis.json',
            BOOK_DIR / f'{prefix}_aligned_sentences.json',
        )
        results.append({"chapter": ch, **result})
        print(
            f"[Acoustic Repair] Chapter {ch:02d}: {result['status']} "
            f"({result.get('review_before', 0)} -> {result.get('review_after', result.get('review_before', 0))})",
            flush=True,
        )
    atomic_write_json(BOOK_DIR / 'acoustic_repair_report.json', results)
    return results


def run_pipeline():
    print('================================================================================', flush=True)
    print('      Starting Industrial End-to-End Pipeline for Fourth Wing (39 Chapters)     ', flush=True)
    print('================================================================================', flush=True)

    audio_files = [AUDIO_DIR / f"chapter_{ch:02d}.mp3" for ch in range(1, TOTAL_CHAPTERS + 1)]
    if not all(path.is_file() for path in audio_files):
        print("[ERROR] Explicit chapter audio set is incomplete; halting before processing.", file=sys.stderr, flush=True)
        return 1
    write_audio_manifest(
        BOOK_DIR / "audio_manifest.json",
        build_audio_manifest(AUDIO_DIR, "fourth-wing", chapter_count=TOTAL_CHAPTERS, source_files=audio_files),
    )
    _write_run_manifest("prepared")

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
        _write_run_manifest("blocked")
        return 1

    run_bounded_acoustic_repairs()
    _write_run_manifest("validation")

    # Quality Gate Validation & Compilation
    print("\n=== [Running Release Quality Gate] ===", flush=True)
    report_path = BOOK_DIR / "reader_validation_report.json"
    report, release_token = validate_for_release(BOOK_DIR, report_path, require_provenance=True)
    if release_token is None:
        print(f"[ERROR] Release gate blocked! See report at: {report_path}", file=sys.stderr, flush=True)
        _write_run_manifest("blocked")
        return 1

    print(f"[Quality Gate Passed] Generated Release Token: {release_token}", flush=True)

    # Semantic review is a release prerequisite, not a post-build warning.
    print("\n=== [Running Semantic Quality Gate Check] ===", flush=True)
    semantic_path = BOOK_DIR / "reader_semantic_review.json"
    if not semantic_path.exists():
        print("[ERROR] reader_semantic_review.json is required before compilation.", file=sys.stderr, flush=True)
        _write_run_manifest("blocked")
        return 1
    sem_check = validate_semantic_review(semantic_path, required_chapters=[1, 18, 25, 36, 39])
    if sem_check["status"] != "passed":
        print(f"[ERROR] Semantic review validation failed: {sem_check['errors']}", file=sys.stderr, flush=True)
        _write_run_manifest("blocked")
        return 1
    print(f"[SUCCESS] Semantic Review Verified with {sem_check['sample_count']} sampled chapters!", flush=True)

    # Build Master Interactive Reader only after all release prerequisites pass.
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

    # Smoke Check on Master HTML
    print("\n=== [Running Reader Smoke Check] ===", flush=True)
    smoke = smoke_check_html(master_html_path, expected_chapters=TOTAL_CHAPTERS)
    if smoke["status"] != "passed":
        print(f"[ERROR] Reader smoke check failed: {smoke['errors']}", file=sys.stderr, flush=True)
        _write_run_manifest("blocked")
        return 1

    print(f"\n[SUCCESS] Reader Smoke Check Passed with 0 errors! Total chapters: {smoke['chapter_count']}", flush=True)
    print(f"[SUCCESS] Standalone Interactive Reader compiled at: {master_html_path}", flush=True)

    print("================================================================================", flush=True)
    print("                     ALL 39 CHAPTERS COMPILED AND VERIFIED                    ", flush=True)
    print("================================================================================", flush=True)
    _write_run_manifest("compiled")
    return 0


if __name__ == '__main__':
    raise SystemExit(run_pipeline())
