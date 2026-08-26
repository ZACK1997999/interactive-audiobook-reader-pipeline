"""
Script: sync_48laws_continuous.py
Description: Background auto-sync daemon for The 48 Laws of Power.
Monitors acoustic transcription from MLX Whisper, aligns new chapters with 100% sentence coverage, and automatically updates the Master Interactive Reader.
"""

import os
import sys
import time
import json
import glob

PIPELINE_DIR = "/Users/lindy/Vault/My Python Productivity Script 2/interactive_reader_pipeline"
sys.path.append(PIPELINE_DIR)

from dynamic_aligner import align_sentences_with_audio
from html_builder import build_master_reader

BOOK_DIR = "/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/The 48 Laws of Power - Robert Greene"
AUDIO_DIR = os.path.join(BOOK_DIR, "audio")
OUT_HTML = os.path.join(BOOK_DIR, "The_48_Laws_of_Power_Interactive_Reader.html")

def get_chapter_title(ch_num):
    canon_path = os.path.join(BOOK_DIR, f"48laws_ch{ch_num:02d}_canonical_sentences.json")
    if not os.path.exists(canon_path):
        canon_path = os.path.join(BOOK_DIR, "48laws_preface_canonical_sentences.json")
    if os.path.exists(canon_path):
        with open(canon_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            h_texts = [d["text"] for d in data if d.get("is_heading")]
            if ch_num == 0:
                return "Preface"
            elif len(h_texts) >= 2:
                return f"Law {ch_num}: {h_texts[1]}"
            elif len(h_texts) >= 1:
                return f"Law {ch_num}: {h_texts[0]}"
    return f"Chapter {ch_num:02d}"

def sync_once():
    updated_any = False
    aligned_configs = []
    
    for ch in range(49):
        canon_json = os.path.join(BOOK_DIR, f"48laws_ch{ch:02d}_canonical_sentences.json")
        if not os.path.exists(canon_json) and ch == 0:
            canon_json = os.path.join(BOOK_DIR, "48laws_preface_canonical_sentences.json")
            
        analysis_json = os.path.join(BOOK_DIR, f"48laws_ch{ch:02d}_full_analysis.json")
        if not os.path.exists(analysis_json) and ch == 0:
            analysis_json = os.path.join(BOOK_DIR, "48laws_preface_full_analysis.json")
            
        acoustic_json = os.path.join(AUDIO_DIR, f"48laws_ch{ch:02d}_acoustic_words.json")
        aligned_json = os.path.join(BOOK_DIR, f"48laws_ch{ch:02d}_aligned_sentences.json")
        audio_rel = f"./audio/chapter_{ch:02d}.mp3"
        
        has_analysis = os.path.exists(analysis_json) and os.path.getsize(analysis_json) > 1000
        has_acoustic = os.path.exists(acoustic_json) and os.path.getsize(acoustic_json) > 1000
        
        if has_analysis and has_acoustic:
            needs_align = False
            if not os.path.exists(aligned_json):
                needs_align = True
            else:
                an_mtime = os.path.getmtime(analysis_json)
                ac_mtime = os.path.getmtime(acoustic_json)
                al_mtime = os.path.getmtime(aligned_json)
                if ac_mtime > al_mtime or an_mtime > al_mtime:
                    needs_align = True
            
            if needs_align:
                print(f"--> [Auto-Sync] Aligning Chapter {ch:02d} with Global Monotonic Aligner...")
                align_sentences_with_audio(acoustic_json, analysis_json, aligned_json)
                updated_any = True
                
            title = get_chapter_title(ch)
            aligned_configs.append({
                "num": ch,
                "title": title,
                "audio": audio_rel,
                "aligned_json": aligned_json
            })
            
    if updated_any:
        print(f"--> [Auto-Sync] Rebuilding Master Interactive Reader ({len(aligned_configs)} / 49 chapters)...")
        build_master_reader(
            book_title="The 48 Laws of Power",
            book_subtitle="Bilingual Synchronized Reader",
            book_author="Robert Greene",
            chapters_config=aligned_configs,
            output_html_path=OUT_HTML
        )
        print(f"--> Successfully updated {OUT_HTML} with {len(aligned_configs)} chapters!")
        
    return len(aligned_configs), updated_any

if __name__ == "__main__":
    count, updated = sync_once()
    print(f"Sync check finished. Total live chapters: {count} / 49. (Updated: {updated})")
