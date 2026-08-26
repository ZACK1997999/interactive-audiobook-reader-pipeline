import os
import sys
import time

from acoustic_whisper import run_mlx_acoustic_extraction

book_dir = "/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Range - David Epstein"
audio_dir = os.path.join(book_dir, "audio")

chapters_to_run = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

print("=== Starting Batch Acoustic Extraction for Chapters 3 through 13 ===")
for cnum in chapters_to_run:
    cnum_str = f"{cnum:02d}"
    audio_path = os.path.join(audio_dir, f"chapter_{cnum_str}.mp3")
    out_json = os.path.join(audio_dir, f"range_ch{cnum_str}_acoustic_words.json")
    
    if os.path.exists(out_json) and os.path.getsize(out_json) > 10000:
        print(f"Skipping Chapter {cnum}, acoustic words already exist: {out_json}")
        continue
        
    print(f"\n--- Processing Acoustic Extraction for Chapter {cnum} ({audio_path}) ---")
    start_t = time.time()
    try:
        run_mlx_acoustic_extraction(audio_path, out_json, model_name="mlx-community/whisper-large-v3-turbo")
        print(f"Chapter {cnum} completed in {time.time() - start_t:.1f}s")
    except Exception as e:
        print(f"Error on Chapter {cnum}: {e}")

print("\nAll batch acoustic extractions finished!")
