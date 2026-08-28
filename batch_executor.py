"""Parallel batch orchestrator for Influence audiobook pipeline."""

import os
import sys
import json
import time
import concurrent.futures
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(PIPELINE_DIR))

from acoustic_whisper import run_mlx_acoustic_extraction
from agy_linguistic_worker import process_canonical_sentences, PROMPT_PATH
from dynamic_aligner import align_sentences_with_audio
from artifact_io import atomic_write_json
from pipeline import auto_discover_and_build

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

def run_acoustic_pipeline():
    """Extract acoustic word timestamps using MLX Whisper sequentially across chapters."""
    print(">>> [Acoustic Engine] Worker thread started...")
    for ch_num, prefix, audio_name, title in CHAPTERS:
        audio_path = AUDIO_DIR / audio_name
        acoustic_path = AUDIO_DIR / f"{prefix}_acoustic_words.json"
        
        if acoustic_path.is_file() and acoustic_path.stat().st_size > 1000:
            try:
                data = json.loads(acoustic_path.read_text(encoding="utf-8"))
                if data.get("words") and len(data["words"]) > 0:
                    print(f">>> [Acoustic] Chapter {ch_num:02d} ({prefix}) already cached ({len(data['words'])} words). Skipping.")
                    continue
            except Exception:
                pass

        print(f"\n>>> [Acoustic] Processing Chapter {ch_num:02d} ({audio_name} - {title})...")
        t0 = time.time()
        run_mlx_acoustic_extraction(
            str(audio_path),
            str(acoustic_path),
            model_name="mlx-community/whisper-large-v3-turbo",
        )
        print(f">>> [Acoustic] Chapter {ch_num:02d} finished in {time.time()-t0:.1f}s -> {acoustic_path.name}")
    print(">>> [Acoustic Engine] All chapters complete!")

def run_linguistic_pipeline():
    """Run LLM linguistic analysis sequentially chapter-by-chapter (with internal parallel batching)."""
    print(">>> [Linguistic Engine] Worker thread started...")
    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    
    for ch_num, prefix, audio_name, title in CHAPTERS:
        canonical_path = BOOK_DIR / f"{prefix}_canonical_sentences.json"
        analysis_path = BOOK_DIR / f"{prefix}_full_analysis.json"
        
        if analysis_path.is_file() and analysis_path.stat().st_size > 0:
            try:
                data = json.loads(analysis_path.read_text(encoding="utf-8"))
                canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
                if isinstance(data, list) and len(data) == len(canonical) and all(isinstance(item.get("trans"), str) and item.get("trans", "").strip() for item in data):
                    print(f">>> [Linguistic] Chapter {ch_num:02d} ({prefix}) already cached ({len(data)} sentences). Skipping.")
                    continue
            except Exception:
                pass

        print(f"\n>>> [Linguistic] Analyzing Chapter {ch_num:02d} ({title} - {prefix})...")
        t0 = time.time()
        canonical_data = json.loads(canonical_path.read_text(encoding="utf-8"))
        
        results = process_canonical_sentences(
            canonical_data=canonical_data,
            base_prompt=base_prompt,
            cwd=PIPELINE_DIR,
            chunk_size=50,
            timeout=3700,
            max_batch_attempts=3,
        )
        
        atomic_write_json(analysis_path, results)
        print(f">>> [Linguistic] Chapter {ch_num:02d} finished in {time.time()-t0:.1f}s ({len(results)} sentences) -> {analysis_path.name}")
    print(">>> [Linguistic Engine] All chapters complete!")

def main():
    print("=" * 60)
    print("   INFLUENCE AUDIOBOOK INDUSTRIAL PIPELINE BATCH RUNNER")
    print("=" * 60)
    
    # Run acoustic extraction and linguistic analysis in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f_acoustic = executor.submit(run_acoustic_pipeline)
        f_linguistic = executor.submit(run_linguistic_pipeline)
        
        # Wait for both pipelines to complete
        f_acoustic.result()
        f_linguistic.result()
    
    print("\n" + "=" * 60)
    print(">>> [Alignment & Master Compilation] Aligning all 11 chapters & compiling interactive reader HTML...")
    print("=" * 60)
    
    ready_count, html_path = auto_discover_and_build(
        book_dir=str(BOOK_DIR),
        book_title="Influence, New and Expanded",
        book_subtitle="The Psychology of Persuasion",
        book_author="Robert B. Cialdini",
        force_realign=True,
    )
    
    print(f"\nSUCCESS! Compiled {ready_count} chapters into: {html_path}")

if __name__ == "__main__":
    main()
