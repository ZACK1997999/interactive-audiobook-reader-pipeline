"""Batch orchestrator for Influence audiobook pipeline."""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(PIPELINE_DIR))

from acoustic_whisper import run_mlx_acoustic_extraction
from agy_linguistic_worker import process_canonical_sentences, PROMPT_PATH
from dynamic_aligner import align_sentences_with_audio
from artifact_io import atomic_write_json

BOOK_DIR = Path("/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Influence - Robert B. Cialdini").resolve()
AUDIO_DIR = BOOK_DIR / "audio"

CHAPTERS = [
    (0, "influence_ch00", "chapter_00.mp3", "Preface"),
    (1, "influence_ch01", "chapter_01.mp3", "Introduction"),
    (2, "influence_ch02", "chapter_02.mp3", "Chapter 1: Levers of Influence"),
    (3, "influence_ch03", "chapter_03.mp3", "Chapter 2: Reciprocation"),
    (4, "influence_ch04", "chapter_04.mp3", "Chapter 3: Liking"),
    (5, "influence_ch05", "chapter_05.mp3", "Chapter 4: Social Proof"),
    (6, "influence_ch06", "chapter_06.mp3", "Chapter 5: Authority"),
    (7, "influence_ch07", "chapter_07.mp3", "Chapter 6: Scarcity"),
    (8, "influence_ch08", "chapter_08.mp3", "Chapter 7: Commitment and Consistency"),
    (9, "influence_ch09", "chapter_09.mp3", "Chapter 8: Unity"),
    (10, "influence_ch10", "chapter_10.mp3", "Chapter 9: Instant Influence"),
]

def process_linguistic(ch_num, prefix):
    canonical_path = BOOK_DIR / f"{prefix}_canonical_sentences.json"
    analysis_path = BOOK_DIR / f"{prefix}_full_analysis.json"
    
    if analysis_path.is_file() and analysis_path.stat().st_size > 0:
        try:
            data = json.loads(analysis_path.read_text(encoding="utf-8"))
            canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
            if isinstance(data, list) and len(data) == len(canonical) and all(isinstance(item.get("trans"), str) and item.get("trans", "").strip() for item in data):
                print(f"[Linguistic] Chapter {ch_num:02d} ({prefix}) already complete ({len(data)} items). Skipping.")
                return True
        except Exception:
            pass

    print(f"[Linguistic] Starting analysis for Chapter {ch_num:02d} ({prefix})...")
    canonical_data = json.loads(canonical_path.read_text(encoding="utf-8"))
    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    
    results = process_canonical_sentences(
        canonical_data=canonical_data,
        base_prompt=base_prompt,
        cwd=PIPELINE_DIR,
        chunk_size=50,
        timeout=3700,
        max_batch_attempts=3,
    )
    
    atomic_write_json(analysis_path, results)
    print(f"[Linguistic] Successfully wrote Chapter {ch_num:02d} analysis -> {analysis_path} ({len(results)} items)")
    return True

def process_acoustic(ch_num, prefix, audio_name):
    audio_path = AUDIO_DIR / audio_name
    acoustic_path = AUDIO_DIR / f"{prefix}_acoustic_words.json"
    
    if acoustic_path.is_file() and acoustic_path.stat().st_size > 1000:
        try:
            data = json.loads(acoustic_path.read_text(encoding="utf-8"))
            if data.get("words") and len(data["words"]) > 0:
                print(f"[Acoustic] Chapter {ch_num:02d} ({prefix}) already extracted ({len(data['words'])} words). Skipping.")
                return True
        except Exception:
            pass

    print(f"[Acoustic] Starting Whisper extraction for Chapter {ch_num:02d} ({audio_name})...")
    run_mlx_acoustic_extraction(
        str(audio_path),
        str(acoustic_path),
        model_name="mlx-community/whisper-large-v3-turbo",
    )
    print(f"[Acoustic] Successfully extracted Chapter {ch_num:02d} words -> {acoustic_path}")
    return True

def main():
    print(f"=== Starting Batch Processing for Influence ({len(CHAPTERS)} chapters) ===")
    
    # 1. Run linguistic analysis sequentially across chapters
    print("\n--- Phase 1: Linguistic Analysis ---")
    for ch_num, prefix, audio_name, title in CHAPTERS:
        process_linguistic(ch_num, prefix)

    # 2. Run acoustic extraction sequentially across chapters
    print("\n--- Phase 2: Acoustic Word Timestamp Extraction ---")
    for ch_num, prefix, audio_name, title in CHAPTERS:
        process_acoustic(ch_num, prefix, audio_name)

    # 3. Run dynamic alignment for each chapter
    print("\n--- Phase 3: Dynamic Sentence-to-Audio Alignment ---")
    for ch_num, prefix, audio_name, title in CHAPTERS:
        analysis_path = BOOK_DIR / f"{prefix}_full_analysis.json"
        acoustic_path = AUDIO_DIR / f"{prefix}_acoustic_words.json"
        aligned_path = BOOK_DIR / f"{prefix}_aligned_sentences.json"
        align_sentences_with_audio(str(acoustic_path), str(analysis_path), str(aligned_path))

    print("\n=== All chapters aligned successfully! ===")

if __name__ == "__main__":
    main()
