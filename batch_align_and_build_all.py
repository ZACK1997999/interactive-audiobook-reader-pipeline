"""
Module: batch_align_and_build_all.py
Description: Batch aligns all chapters (1 to 13) and compiles the unified master interactive reader.
"""

import os
import json
import difflib
import re

from dynamic_aligner import align_sentences_with_audio
from html_builder import build_master_reader
from deploy_pages import deploy_to_audible

book_dir = "/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Range - David Epstein"
audio_dir = os.path.join(book_dir, "audio")
master_html_path = os.path.join(book_dir, "Range_Interactive_Reader.html")

chapter_titles = {
    1: "The Cult of the Head Start",
    2: "How the Wicked World Was Made",
    3: "When Less of the Same Is More",
    4: "Learning, Fast and Slow",
    5: "Thinking Outside Experience",
    6: "The Trouble with Too Much Grit",
    7: "Flirting with Your Possible Selves",
    8: "The Outsider Advantage",
    9: "Lateral Thinking with Withered Technology",
    10: "Fooled by Expertise",
    11: "Learning to Drop Your Familiar Tools",
    12: "Deliberate Amateurs",
    13: "CONCLUSION: Expanding Your Range"
}

def main():
    print("=== [Step 1] Aligning Sentences for All Available Chapters ===")
    aligned_chapters = []
    
    for cnum in range(1, 14):
        cnum_str = f"{cnum:02d}"
        analysis_file = os.path.join(book_dir, f"range_ch{cnum_str}_full_analysis.json")
        acoustic_file = os.path.join(audio_dir, f"range_ch{cnum_str}_acoustic_words.json")
        aligned_file = os.path.join(book_dir, f"range_ch{cnum_str}_aligned_sentences.json")
        audio_file = f"./audio/chapter_{cnum_str}.mp3"
        
        if not os.path.exists(analysis_file):
            print(f"Skipping Ch {cnum}: linguistic analysis not ready yet ({analysis_file})")
            continue
            
        if os.path.exists(acoustic_file) and os.path.getsize(acoustic_file) > 5000:
            print(f"Aligning Chapter {cnum} with acoustic words...")
            align_sentences_with_audio(acoustic_file, analysis_file, aligned_file)
        elif not os.path.exists(aligned_file):
            print(f"Notice: Ch {cnum} acoustic words not ready yet, generating provisional fallback alignment...")
            # Fallback estimation if acoustic extraction still running
            with open(analysis_file, 'r', encoding='utf-8') as f:
                sents = json.load(f)
            provisional = []
            cur_t = 0.0
            for s in sents:
                words = s['text'].split()
                dur = max(1.5, len(words) * 0.35)
                word_spans = []
                w_t = cur_t
                w_dur = dur / max(1, len(words))
                for w in words:
                    word_spans.append({"word": w, "start": round(w_t, 2), "end": round(w_t + w_dur, 2)})
                    w_t += w_dur
                provisional.append({
                    **s,
                    "start": round(cur_t, 2),
                    "end": round(cur_t + dur, 2),
                    "raw_start": round(cur_t, 2),
                    "raw_end": round(cur_t + dur, 2),
                    "word_spans": word_spans
                })
                cur_t += dur + 0.2
            with open(aligned_file, 'w', encoding='utf-8') as f:
                json.dump(provisional, f, ensure_ascii=False, indent=2)
                
        if os.path.exists(aligned_file):
            aligned_chapters.append({
                "num": cnum,
                "title": chapter_titles.get(cnum, f"Chapter {cnum}"),
                "audio": audio_file,
                "aligned_json": aligned_file
            })
            
    print(f"\n=== [Step 2] Compiling Master Multi-Chapter Reader with {len(aligned_chapters)} Chapters ===")
    if aligned_chapters:
        build_master_reader(
            book_title="Range",
            book_subtitle="Why Generalists Triumph in a Specialized World",
            book_author="David Epstein",
            chapters_config=aligned_chapters,
            output_html_path=master_html_path
        )
        print(f"Master Reader successfully built with {len(aligned_chapters)} chapters!")
        
    print(f"\n=== [Step 3] Deploying to GitHub Pages ===")
    audio_full_paths = [os.path.join(audio_dir, f"chapter_{c['num']:02d}.mp3") for c in aligned_chapters]
    deploy_to_audible(master_html_path, audio_full_paths, commit_message=f"feat: update Range master reader with {len(aligned_chapters)} chapters")

if __name__ == "__main__":
    main()
