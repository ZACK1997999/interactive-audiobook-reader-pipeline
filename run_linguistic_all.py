"""Run linguistic analysis across all chapters of Influence."""

import os
import sys
import json
import time
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(PIPELINE_DIR))

from agy_linguistic_worker import process_canonical_sentences, PROMPT_PATH
from artifact_io import atomic_write_json

BOOK_DIR = Path("/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Influence - Robert B. Cialdini").resolve()

CHAPTERS = [
    (0, "influence_ch00"),
    (1, "influence_ch01"),
    (2, "influence_ch02"),
    (3, "influence_ch03"),
    (4, "influence_ch04"),
    (5, "influence_ch05"),
    (6, "influence_ch06"),
    (7, "influence_ch07"),
    (8, "influence_ch08"),
    (9, "influence_ch09"),
    (10, "influence_ch10"),
]

def main():
    print(f"=== Starting Linguistic Analysis for Influence ({len(CHAPTERS)} chapters) ===")
    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    
    for ch_num, prefix in CHAPTERS:
        canonical_path = BOOK_DIR / f"{prefix}_canonical_sentences.json"
        analysis_path = BOOK_DIR / f"{prefix}_full_analysis.json"
        
        if analysis_path.is_file() and analysis_path.stat().st_size > 0:
            try:
                data = json.loads(analysis_path.read_text(encoding="utf-8"))
                canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
                if isinstance(data, list) and len(data) == len(canonical) and all(isinstance(item.get("trans"), str) and item.get("trans", "").strip() for item in data):
                    print(f"[Linguistic] Chapter {ch_num:02d} ({prefix}) already complete ({len(data)} items). Skipping.")
                    continue
            except Exception:
                pass

        print(f"\n[Linguistic] Starting Chapter {ch_num:02d} ({prefix})...")
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
        print(f"[Linguistic] Successfully wrote Chapter {ch_num:02d} analysis -> {analysis_path} ({len(results)} items)")

    print("\n=== Linguistic Analysis Complete for All Chapters! ===")

if __name__ == "__main__":
    main()
