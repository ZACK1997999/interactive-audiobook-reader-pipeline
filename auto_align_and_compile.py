import json, os, sys, time, html
from pathlib import Path
from dynamic_aligner import align_sentences_with_audio
from compile_live_reader import main as compile_reader

book_dir = Path(".runs/elon-musk-xiaoshu-20260827/book")
audio_dir = book_dir / "audio"

with open(book_dir / "raw_intake_mapping.json", encoding="utf-8") as f:
    mapping = json.load(f)

entries = mapping["entries"]
total_chapters = len(entries)

print(f"[PipelineLoop] Monitoring {total_chapters} chapters for dynamic alignment and hot compilation...")

aligned_count = 0
last_compiled_count = 0

while True:
    newly_aligned = 0
    for entry in entries:
        ch = entry["chapter"]
        analysis_path = book_dir / f"elon_musk_ch{ch:02d}_full_analysis.json"
        acoustic_path = audio_dir / f"elon_musk_ch{ch:02d}_acoustic_words.json"
        aligned_path = book_dir / f"elon_musk_ch{ch:02d}_aligned_sentences.json"
        
        if aligned_path.is_file() and aligned_path.stat().st_size > 0:
            continue
            
        if analysis_path.is_file() and acoustic_path.is_file():
            print(f"[PipelineLoop] >>> Aligning Chapter {ch:02d} ({entry.get('title', '')})...")
            try:
                aligned = align_sentences_with_audio(str(acoustic_path), str(analysis_path), str(aligned_path))
                matched = sum(1 for s in aligned if s.get("has_audio_match"))
                total = len(aligned)
                pct = round(matched / total * 100, 1) if total > 0 else 0
                print(f"[PipelineLoop] ✅ Chapter {ch:02d} aligned: {matched}/{total} ({pct}%)")
                newly_aligned += 1
            except Exception as e:
                print(f"[PipelineLoop] ❌ Chapter {ch:02d} alignment error: {e}")

    current_aligned = len(list(book_dir.glob("elon_musk_ch*_aligned_sentences.json")))
    if current_aligned > last_compiled_count:
        print(f"[PipelineLoop] 🔄 Recompiling reader with {current_aligned}/{total_chapters} chapters...")
        compile_reader()
        last_compiled_count = current_aligned
        print(f"[PipelineLoop] ✨ Reader hot-updated to {current_aligned} chapters!")
        
    if current_aligned >= total_chapters:
        print(f"[PipelineLoop] 🏁 All {total_chapters} chapters fully aligned and compiled!")
        break
        
    time.sleep(5)
