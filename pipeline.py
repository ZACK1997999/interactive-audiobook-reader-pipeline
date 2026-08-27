"""
Module: pipeline.py
Description: Release orchestrator for prepared audiobook-reader artifacts.
It aligns, validates, and compiles prepared chapter data. EPUB extraction and MLX Whisper
transcription are separate preparation stages.
"""

import os
import sys
import argparse
import json
import glob
import re
import hashlib
from pathlib import Path

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PIPELINE_DIR)

from dynamic_aligner import align_sentences_with_audio
from html_builder import build_master_reader
from validate_outputs import validate_for_release
from chapter_resolver import discover_chapters
from audio_resolver import resolve_chapter_audio
from run_manifest import update_manifest


def _file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _analysis_ready(path, canonical_path):
    """Require complete, non-empty analysis before alignment can begin."""
    try:
        with open(path, encoding="utf-8") as handle:
            analysis = json.load(handle)
        with open(canonical_path, encoding="utf-8") as handle:
            canonical = json.load(handle)
    except (OSError, ValueError, TypeError):
        return False
    return (
        isinstance(analysis, list)
        and len(analysis) == len(canonical)
        and all(isinstance(item.get("trans"), str) and item.get("trans", "").strip() for item in analysis)
    )


def _find_chapter_audio(audio_dir, chapter_number):
    """Return a path only when exactly one explicit chapter candidate exists."""
    resolution = resolve_chapter_audio(audio_dir, chapter_number)
    return str(resolution.path) if resolution.path else None

def auto_discover_and_build(book_dir, book_title=None, book_subtitle="Bilingual Synchronized Reader", book_author=None, force_realign=False):
    """
    Universally auto-discovers all chapters in a book directory,
    runs global alignment on ready pairs, and compiles the Master Interactive Reader.
    """
    book_dir = os.path.abspath(book_dir)
    audio_dir = os.path.join(book_dir, "audio")
    
    # Auto-infer book metadata if omitted
    folder_name = os.path.basename(book_dir)
    if " - " in folder_name and (not book_title or not book_author):
        parts = folder_name.split(" - ")
        if not book_title:
            book_title = parts[0].strip()
        if not book_author:
            book_author = parts[1].strip()
    elif not book_title:
        book_title = folder_name
    if not book_author:
        book_author = "Author"
        
    master_html_name = f"{book_title.replace(' ', '_')}_Interactive_Reader.html"
    master_html_path = os.path.join(book_dir, master_html_name)
    
    # Discover all chapter artifacts through the shared resolver.
    chapter_artifacts = discover_chapters(book_dir)
    if not chapter_artifacts:
        print(f"No canonical sentence files found in {book_dir}")
        return 0, master_html_path
        
    aligned_configs = []
    manifest_chapters = []
    
    for artifact in chapter_artifacts:
        c_path = str(artifact.canonical_path)
        prefix = artifact.prefix
        ch_num = artifact.chapter_number
            
        analysis_path = str(artifact.analysis_path)
        aligned_path = os.path.join(book_dir, f"{prefix}_aligned_sentences.json")
        acoustic_path = str(artifact.acoustic_path)
        
        # Audio file matching
        audio_file = _find_chapter_audio(audio_dir, ch_num)
        audio_file_rel = f"./audio/{os.path.basename(audio_file)}" if audio_file else f"./audio/chapter_{ch_num:02d}.mp3"
                
        has_analysis = os.path.exists(analysis_path) and _analysis_ready(analysis_path, c_path)
        has_acoustic = os.path.exists(acoustic_path) and os.path.getsize(acoustic_path) > 1000
        manifest_chapters.append({
            "chapter": ch_num,
            "status": "ready" if has_analysis and has_acoustic else "blocked",
            "canonical": os.path.relpath(c_path, book_dir),
            "analysis": os.path.relpath(analysis_path, book_dir),
            "acoustic": os.path.relpath(acoustic_path, book_dir),
            "aligned": os.path.relpath(aligned_path, book_dir),
            "analysis_sha256": _file_sha256(analysis_path) if os.path.exists(analysis_path) else None,
            "acoustic_sha256": _file_sha256(acoustic_path) if os.path.exists(acoustic_path) else None,
        })
        
        if has_analysis and has_acoustic:
            needs_align = force_realign or not os.path.exists(aligned_path)
            if not needs_align:
                if os.path.getmtime(acoustic_path) > os.path.getmtime(aligned_path) or os.path.getmtime(analysis_path) > os.path.getmtime(aligned_path):
                    needs_align = True
                    
            if needs_align:
                print(f"--> Aligning {prefix} with Full-Chapter Non-Monotonic Aligner...")
                align_sentences_with_audio(acoustic_path, analysis_path, aligned_path)
                
            # Extract Chapter Title
            with open(c_path, 'r', encoding='utf-8') as f:
                c_data = json.load(f)
            h_texts = [d["text"] for d in c_data if d.get("is_heading")]
            if ch_num == 0:
                title = "Preface"
            elif len(h_texts) >= 2:
                title = h_texts[1]
            elif len(h_texts) >= 1:
                title = h_texts[0]
            else:
                title = f"Chapter {ch_num}"
                
            aligned_configs.append({
                "num": ch_num,
                "title": title,
                "audio": audio_file_rel,
                "aligned_json": aligned_path
            })
            
    for entry in manifest_chapters:
        aligned_file = Path(book_dir) / entry["aligned"]
        if aligned_file.exists():
            entry["aligned_sha256"] = _file_sha256(aligned_file)
            if entry["status"] == "ready":
                entry["status"] = "aligned"
    update_manifest(book_dir, manifest_chapters, status="prepared")
    print(f"\nDiscovered {len(aligned_configs)} / {len(chapter_artifacts)} ready aligned chapters for {book_title}")
    if not aligned_configs:
        update_manifest(book_dir, manifest_chapters, status="blocked")
        print("Release blocked: no chapters have complete analysis and acoustic artifacts.")
        return 0, master_html_path
    if aligned_configs:
        report_path = os.path.join(book_dir, "reader_validation_report.json")
        report, release_token = validate_for_release(Path(book_dir), Path(report_path))
        if release_token is None:
            update_manifest(book_dir, manifest_chapters, status="blocked")
            print(f"Release blocked. See {report_path}")
            return 0, master_html_path
        print("--> Compiling Master Multi-Chapter Interactive Reader...")
        build_master_reader(
            book_title=book_title,
            book_subtitle=book_subtitle,
            book_author=book_author,
            chapters_config=aligned_configs,
            output_html_path=master_html_path,
            release_token=release_token,
            release_report_path=report_path,
        )
        update_manifest(book_dir, manifest_chapters, status="released")
        print(f"Successfully generated/updated: {master_html_path}")
        
    return len(aligned_configs), master_html_path

def main():
    parser = argparse.ArgumentParser(description="Universal Interactive Audiobook Reader Industrial Pipeline")
    parser.add_argument("--book-dir", required=True, help="Path to book directory in Obsidian")
    parser.add_argument("--title", help="Book title (inferred automatically if omitted)")
    parser.add_argument("--author", help="Book author (inferred automatically if omitted)")
    parser.add_argument("--subtitle", default="Bilingual Synchronized Reader", help="Book subtitle")
    parser.add_argument("--realign", action="store_true", help="Force re-alignment across all chapters")
    
    args = parser.parse_args()
    ready_count, _ = auto_discover_and_build(
        book_dir=args.book_dir,
        book_title=args.title,
        book_subtitle=args.subtitle,
        book_author=args.author,
        force_realign=args.realign
    )
    if ready_count == 0:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
