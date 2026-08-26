import argparse
import os
import time

from acoustic_whisper import run_mlx_acoustic_extraction

CHAPTERS = range(3, 14)

def main():
    parser = argparse.ArgumentParser(description="Extract word timestamps for local chapter audio.")
    parser.add_argument("--book-dir", required=True)
    args = parser.parse_args()
    audio_dir = os.path.join(args.book_dir, "audio")
    for cnum in CHAPTERS:
        name = f"{cnum:02d}"
        audio_path = os.path.join(audio_dir, f"chapter_{name}.mp3")
        out_json = os.path.join(audio_dir, f"range_ch{name}_acoustic_words.json")
        if os.path.exists(out_json) and os.path.getsize(out_json) > 10000:
            print(f"Skipping Chapter {cnum}: {out_json}")
            continue
        print(f"Processing Chapter {cnum}: {audio_path}")
        try:
            started = time.time()
            run_mlx_acoustic_extraction(audio_path, out_json, model_name="mlx-community/whisper-large-v3-turbo")
            print(f"Completed in {time.time() - started:.1f}s")
        except Exception as exc:
            print(f"Error on Chapter {cnum}: {exc}")

if __name__ == "__main__":
    main()
