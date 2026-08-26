import argparse
import os
import shutil

from extract_epub import extract_chapter_from_epub

CHAPTER_CONFIGS = [
    {"num": 3, "internal": "OEBPS/xhtml/11_CHAPTER_3_When_Less_o.xhtml", "track": "006 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 4, "internal": "OEBPS/xhtml/12_CHAPTER_4_Learning_Fa.xhtml", "track": "007 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 5, "internal": "OEBPS/xhtml/13_CHAPTER_5_Thinking_Ou.xhtml", "track": "008 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 6, "internal": "OEBPS/xhtml/14_CHAPTER_6_The_Trouble.xhtml", "track": "009 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 7, "internal": "OEBPS/xhtml/15_CHAPTER_7_Flirting_wi.xhtml", "track": "010 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 8, "internal": "OEBPS/xhtml/16_CHAPTER_8_The_Outside.xhtml", "track": "011 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 9, "internal": "OEBPS/xhtml/17_CHAPTER_9_Lateral_Thi.xhtml", "track": "012 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 10, "internal": "OEBPS/xhtml/18_CHAPTER_10_Fooled_by_.xhtml", "track": "013 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 11, "internal": "OEBPS/xhtml/19_CHAPTER_11_Learning_t.xhtml", "track": "014 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 12, "internal": "OEBPS/xhtml/20_CHAPTER_12_Deliberate.xhtml", "track": "015 - Range Why Generalists Triumph in a Specialized World.mp3"},
    {"num": 13, "internal": "OEBPS/xhtml/21_CONCLUSION_Expanding_.xhtml", "track": "016 - Range Why Generalists Triumph in a Specialized World.mp3"},
]

def main():
    parser = argparse.ArgumentParser(description="Extract chapters and copy local audiobook tracks.")
    parser.add_argument("--epub", required=True)
    parser.add_argument("--audio-source-dir", required=True)
    parser.add_argument("--book-dir", required=True)
    args = parser.parse_args()
    local_audio_dir = os.path.join(args.book_dir, "audio")
    os.makedirs(local_audio_dir, exist_ok=True)
    print("=== Extracting canonical sentences and copying audio ===")
    for chapter in CHAPTER_CONFIGS:
        num_str = f"{chapter['num']:02d}"
        canon_out = os.path.join(args.book_dir, f"range_ch{num_str}_canonical_sentences.json")
        extract_chapter_from_epub(args.epub, chapter["internal"], canon_out)
        src = os.path.join(args.audio_source_dir, chapter["track"])
        dst = os.path.join(local_audio_dir, f"chapter_{num_str}.mp3")
        if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
            shutil.copyfile(src, dst)
            print(f"Copied audio -> {dst}")

if __name__ == "__main__":
    main()
