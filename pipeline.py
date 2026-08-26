"""
Module: pipeline.py
Description: Master CLI Orchestrator for the Interactive Audiobook Reader Pipeline.
"""

import os
import sys
import argparse
import json

from extract_epub import extract_chapter_from_epub
from acoustic_whisper import run_mlx_acoustic_extraction
from dynamic_aligner import align_sentences_with_audio
from html_builder import build_master_reader
from deploy_pages import deploy_to_audible

def main():
    parser = argparse.ArgumentParser(description="Interactive Audiobook Reader Industrial Pipeline")
    parser.add_argument("--book-dir", help="Output directory (or set READER_BOOK_DIR)")
    parser.add_argument("--epub", help="Path to source EPUB file")
    parser.add_argument("--internal-path", help="Internal XHTML path inside EPUB (e.g. OEBPS/xhtml/11_CHAPTER_3_When_Less_o.xhtml)")
    parser.add_argument("--audio-source", help="Source MP3 track path")
    parser.add_argument("--chapter-num", type=int, help="Chapter number (e.g. 3)")
    parser.add_argument("--chapter-title", help="Chapter Title (e.g. When Less of the Same Is More)")
    parser.add_argument("--action", choices=["extract", "acoustic", "align", "build-html", "deploy", "all"], default="all")
    
    args = parser.parse_args()
    
    from config import path_arg
    book_dir = str(path_arg(args.book_dir, "READER_BOOK_DIR"))
    os.makedirs(book_dir, exist_ok=True)
    os.makedirs(os.path.join(book_dir, "audio"), exist_ok=True)
    
    cnum = args.chapter_num
    cnum_str = f"{cnum:02d}" if cnum else "01"
    
    canon_json = os.path.join(book_dir, f"range_ch{cnum_str}_canonical_sentences.json")
    acoustic_json = os.path.join(book_dir, "audio", f"range_ch{cnum_str}_acoustic_words.json")
    aligned_json = os.path.join(book_dir, f"range_ch{cnum_str}_aligned_sentences.json")
    analysis_json = os.path.join(book_dir, f"range_ch{cnum_str}_full_analysis.json")
    local_audio = os.path.join(book_dir, "audio", f"chapter_{cnum_str}.mp3")
    master_html = os.path.join(book_dir, "Range_Interactive_Reader.html")
    
    print("=" * 60)
    print("Interactive Audiobook Reader Industrial Pipeline")
    print(f"Book Dir: {book_dir}")
    print(f"Chapter: {cnum} - {args.chapter_title}")
    print("=" * 60)
    
    # 1. Extraction
    if args.action in ["extract", "all"] and args.epub and args.internal_path:
        print("\n[Step 1] Extracting canonical sentences from EPUB...")
        extract_chapter_from_epub(args.epub, args.internal_path, canon_json)
        
    # 2. Acoustic Extraction
    if args.action in ["acoustic", "all"] and args.audio_source:
        import shutil
        if not os.path.exists(local_audio) or os.path.getsize(local_audio) != os.path.getsize(args.audio_source):
            shutil.copyfile(args.audio_source, local_audio)
            print(f"Copied audio {args.audio_source} -> {local_audio}")
        print("\n[Step 2] Running Apple Silicon MLX Whisper acoustic extraction...")
        run_mlx_acoustic_extraction(local_audio, acoustic_json)
        
    # 3. Dynamic Alignment
    if args.action in ["align", "all"] and os.path.exists(acoustic_json) and os.path.exists(analysis_json):
        print("\n[Step 3] Running global dynamic acoustic alignment...")
        align_sentences_with_audio(acoustic_json, analysis_json, aligned_json)
        
    # 4. Build Master Reader
    if args.action in ["build-html", "all"]:
        print("\n[Step 4] Compiling Master Multi-Chapter Interactive Reader...")
        # Auto-discover all aligned chapters in book_dir
        discovered_chapters = []
        for i in range(1, 30):
            ch_aligned = os.path.join(book_dir, f"range_ch{i:02d}_aligned_sentences.json")
            ch_audio = f"./audio/chapter_{i:02d}.mp3"
            if os.path.exists(ch_aligned):
                # Discover title
                with open(ch_aligned, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                title = f"Chapter {i}"
                for s in data:
                    if s.get("is_heading") and "CHAPTER" not in s["text"].upper():
                        title = s["text"]
                        break
                discovered_chapters.append({
                    "num": i,
                    "title": title,
                    "audio": ch_audio,
                    "aligned_json": ch_aligned
                })
        if discovered_chapters:
            build_master_reader(
                book_title="Range",
                book_subtitle="Why Generalists Triumph in a Specialized World",
                book_author="David Epstein",
                chapters_config=discovered_chapters,
                output_html_path=master_html
            )
            
    # 5. Deploy
    if args.action in ["deploy", "all"] and os.path.exists(master_html):
        print("\n[Step 5] Deploying to GitHub Pages...")
        audio_files = [os.path.join(book_dir, "audio", f"chapter_{c['num']:02d}.mp3") for c in discovered_chapters]
        deploy_to_audible(master_html, audio_files, commit_message=f"update: deploy Range chapters up to Chapter {len(discovered_chapters)}")

if __name__ == "__main__":
    main()
