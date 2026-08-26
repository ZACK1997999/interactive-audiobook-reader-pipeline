import os
import zipfile
import json
import shutil

from extract_epub import extract_chapter_from_epub

epub_path = "/Users/lindy/Vault/audiobook/Range Why Generalists Triumph in a Specialized World/Range Why Generalists Triumph in a (7433)/Range Why Generalists Triumph i - David Epstein.epub"
audio_source_dir = "/Users/lindy/Vault/audiobook/Range Why Generalists Triumph in a Specialized World"
book_dir = "/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Range - David Epstein"
local_audio_dir = os.path.join(book_dir, "audio")
os.makedirs(local_audio_dir, exist_ok=True)

chapter_configs = [
    {"num": 3, "internal": "OEBPS/xhtml/11_CHAPTER_3_When_Less_o.xhtml", "track": "006 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "When Less of the Same Is More"},
    {"num": 4, "internal": "OEBPS/xhtml/12_CHAPTER_4_Learning_Fa.xhtml", "track": "007 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "Learning, Fast and Slow"},
    {"num": 5, "internal": "OEBPS/xhtml/13_CHAPTER_5_Thinking_Ou.xhtml", "track": "008 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "Thinking Outside Experience"},
    {"num": 6, "internal": "OEBPS/xhtml/14_CHAPTER_6_The_Trouble.xhtml", "track": "009 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "The Trouble with Too Much Grit"},
    {"num": 7, "internal": "OEBPS/xhtml/15_CHAPTER_7_Flirting_wi.xhtml", "track": "010 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "Flirting with Your Possible Selves"},
    {"num": 8, "internal": "OEBPS/xhtml/16_CHAPTER_8_The_Outside.xhtml", "track": "011 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "The Outsider Advantage"},
    {"num": 9, "internal": "OEBPS/xhtml/17_CHAPTER_9_Lateral_Thi.xhtml", "track": "012 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "Lateral Thinking with Withered Technology"},
    {"num": 10, "internal": "OEBPS/xhtml/18_CHAPTER_10_Fooled_by_.xhtml", "track": "013 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "Fooled by Expertise"},
    {"num": 11, "internal": "OEBPS/xhtml/19_CHAPTER_11_Learning_t.xhtml", "track": "014 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "Learning to Drop Your Familiar Tools"},
    {"num": 12, "internal": "OEBPS/xhtml/20_CHAPTER_12_Deliberate.xhtml", "track": "015 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "Deliberate Amateurs"},
    {"num": 13, "internal": "OEBPS/xhtml/21_CONCLUSION_Expanding_.xhtml", "track": "016 - Range Why Generalists Triumph in a Specialized World.mp3", "title": "CONCLUSION: Expanding Your Range"}
]

print("=== [1] Extracting Canonical Sentences and Copying Audio Files ===")
for c in chapter_configs:
    num = c["num"]
    num_str = f"{num:02d}"
    canon_out = os.path.join(book_dir, f"range_ch{num_str}_canonical_sentences.json")
    
    # 1. Extract sentences
    extract_chapter_from_epub(epub_path, c["internal"], canon_out)
    
    # 2. Copy audio file
    src_audio = os.path.join(audio_source_dir, c["track"])
    dst_audio = os.path.join(local_audio_dir, f"chapter_{num_str}.mp3")
    if not os.path.exists(dst_audio) or os.path.getsize(dst_audio) != os.path.getsize(src_audio):
        shutil.copyfile(src_audio, dst_audio)
        print(f"Copied audio -> {dst_audio}")
        
print("\nExtraction and audio copy completed for all chapters 3 through 13!")
