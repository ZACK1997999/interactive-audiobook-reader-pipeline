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
from pathlib import Path

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PIPELINE_DIR)

from dynamic_aligner import align_sentences_with_audio
from html_builder import build_master_reader
from validate_outputs import validate
from audio_resolver import resolve_chapter_audio


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
    
    # Discover all canonical files
    canon_files = sorted(glob.glob(os.path.join(book_dir, "*canonical_sentences.json")))
    if not canon_files:
        print(f"No canonical sentence files found in {book_dir}")
        return 0, master_html_path
        
    aligned_configs = []
    
    for c_path in canon_files:
        base_name = os.path.basename(c_path)
        prefix = base_name.replace("_canonical_sentences.json", "")
        
        # Determine chapter number
        ch_num = 0
        digits = [int(s) for s in re.findall(r'\d+', prefix)]
        if digits:
            ch_num = digits[0]
            
        analysis_path = os.path.join(book_dir, f"{prefix}_full_analysis.json")
        aligned_path = os.path.join(book_dir, f"{prefix}_aligned_sentences.json")
        acoustic_path = os.path.join(audio_dir, f"{prefix}_acoustic_words.json")
        
        # Audio file matching
        audio_file = _find_chapter_audio(audio_dir, ch_num)
        audio_file_rel = f"./audio/{os.path.basename(audio_file)}" if audio_file else f"./audio/chapter_{ch_num:02d}.mp3"
                
        has_analysis = os.path.exists(analysis_path) and os.path.getsize(analysis_path) > 1000
        has_acoustic = os.path.exists(acoustic_path) and os.path.getsize(acoustic_path) > 1000
        
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
            
    print(f"\nDiscovered {len(aligned_configs)} / {len(canon_files)} ready aligned chapters for {book_title}")
    if aligned_configs:
        report_path = os.path.join(book_dir, "reader_validation_report.json")
        if validate(Path(book_dir), Path(report_path)) != 0:
            print(f"Release blocked. See {report_path}")
            return 0, master_html_path
        print("--> Compiling Master Multi-Chapter Interactive Reader...")
        build_master_reader(
            book_title=book_title,
            book_subtitle=book_subtitle,
            book_author=book_author,
            chapters_config=aligned_configs,
            output_html_path=master_html_path
        )
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
