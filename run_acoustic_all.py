"""Run MLX Whisper acoustic extraction across all chapters of Influence."""

import os
import sys
import json
import time
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(PIPELINE_DIR))

from acoustic_whisper import run_mlx_acoustic_extraction

BOOK_DIR = Path("/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Influence - Robert B. Cialdini").resolve()
AUDIO_DIR = BOOK_DIR / "audio"

CHAPTERS = [
    (0, "influence_ch00", "chapter_00.mp3"),
    (1, "influence_ch01", "chapter_01.mp3"),
    (2, "influence_ch02", "chapter_02.mp3"),
    (3, "influence_ch03", "chapter_03.mp3"),
    (4, "influence_ch04", "chapter_04.mp3"),
    (5, "influence_ch05", "chapter_05.mp3"),
    (6, "influence_ch06", "chapter_06.mp3"),
    (7, "influence_ch07", "chapter_07.mp3"),
    (8, "influence_ch08", "chapter_08.mp3"),
    (9, "influence_ch09", "chapter_09.mp3"),
    (10, "influence_ch10", "chapter_10.mp3"),
]

def main():
    print(f"=== Starting MLX Whisper Acoustic Extraction for Influence ({len(CHAPTERS)} chapters) ===")
    
    for ch_num, prefix, audio_name in CHAPTERS:
        audio_path = AUDIO_DIR / audio_name
        acoustic_path = AUDIO_DIR / f"{prefix}_acoustic_words.json"
        
        if acoustic_path.is_file() and acoustic_path.stat().st_size > 1000:
            try:
                data = json.loads(acoustic_path.read_text(encoding="utf-8"))
                if data.get("words") and len(data["words"]) > 0:
                    print(f"[Acoustic] Chapter {ch_num:02d} ({prefix}) already extracted ({len(data['words'])} words). Skipping.")
                    continue
            except Exception:
                pass

        print(f"\n[Acoustic] Starting Chapter {ch_num:02d} ({audio_name})...")
        run_mlx_acoustic_extraction(
            str(audio_path),
            str(acoustic_path),
            model_name="mlx-community/whisper-large-v3-turbo",
        )
        print(f"[Acoustic] Successfully extracted Chapter {ch_num:02d} words -> {acoustic_path}")

    print("\n=== MLX Whisper Extraction Complete for All Chapters! ===")

if __name__ == "__main__":
    main()
