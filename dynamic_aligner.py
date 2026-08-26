"""
Module: dynamic_aligner.py
Description: High-Precision Monotonic Sequence Aligner for Audiobooks with Word-Level Timestamps.
"""

import json
import re
import difflib
import sys

def norm_word(w):
    return re.sub(r'[^a-zA-Z0-9]', '', w).lower()

def align_sentences_with_audio(acoustic_json_path, analysis_json_path, aligned_out_path):
    with open(acoustic_json_path, "r", encoding="utf-8") as f:
        acoustic_data = json.load(f)
    acoustic_words = acoustic_data["words"]
    
    with open(analysis_json_path, "r", encoding="utf-8") as f:
        sentences = json.load(f)
        
    total_ac = len(acoustic_words)
    total_s = len(sentences)
    ac_tokens = [norm_word(w["word"]) for w in acoustic_words]
    
    aligned = []
    current_ac = 0
    prev_st = 0.0
    
    for s_idx, s in enumerate(sentences):
        raw_words = s["text"].split()
        clean = [norm_word(w) for w in raw_words if norm_word(w)]
        
        if not clean:
            # Empty sentence fallback
            aligned.append({
                **s,
                "start": round(prev_st, 2),
                "end": round(prev_st + 1.0, 2),
                "raw_start": round(prev_st, 2),
                "raw_end": round(prev_st + 1.0, 2),
                "word_spans": []
            })
            continue
            
        # Search window in forward acoustic stream
        search_window_size = max(300, len(clean) * 8)
        search_window = ac_tokens[current_ac:min(total_ac, current_ac + search_window_size)]
        
        matcher = difflib.SequenceMatcher(None, clean, search_window)
        m = matcher.find_longest_match(0, len(clean), 0, len(search_window))
        
        if m.size >= 1:
            matched_start = current_ac + m.b - m.a
            matched_end = current_ac + m.b + m.size + (len(clean) - m.a - m.size) - 1
            c_start = max(current_ac, min(total_ac - 1, matched_start))
            c_end = max(c_start, min(total_ac - 1, matched_end))
            current_ac = min(total_ac - 1, c_end + 1)
        else:
            # Fallback estimation forward from current_ac
            c_start = current_ac
            c_end = min(total_ac - 1, current_ac + len(clean) - 1)
            current_ac = min(total_ac - 1, c_end + 1)
            
        raw_st = max(prev_st, acoustic_words[c_start]["start"])
        raw_et = max(raw_st + 0.4, acoustic_words[c_end]["end"])
        prev_st = raw_st
        
        # Word spans
        word_spans = []
        span_count = len(raw_words)
        for w_i, rw in enumerate(raw_words):
            target_ac = min(total_ac - 1, c_start + w_i)
            if target_ac <= c_end:
                ws = max(raw_st, acoustic_words[target_ac]["start"])
                we = max(ws, acoustic_words[target_ac]["end"])
            else:
                w_frac = w_i / max(1, span_count)
                w_frac_next = (w_i + 1) / max(1, span_count)
                ws = round(raw_st + w_frac * (raw_et - raw_st), 2)
                we = round(raw_st + w_frac_next * (raw_et - raw_st), 2)
            word_spans.append({"word": rw, "start": round(ws, 2), "end": round(we, 2)})
            
        aligned.append({
            **s,
            "start": round(max(0.0, raw_st - 0.15), 2),
            "end": round(raw_et + 0.30, 2),
            "raw_start": round(raw_st, 2),
            "raw_end": round(raw_et, 2),
            "word_spans": word_spans
        })
        
    with open(aligned_out_path, "w", encoding="utf-8") as f:
        json.dump(aligned, f, ensure_ascii=False, indent=2)
        
    print(f"[{aligned_out_path}] Aligned {len(aligned)} sentences strictly monotonically!")
    return aligned

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        align_sentences_with_audio(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python3 dynamic_aligner.py <acoustic_json_path> <analysis_json_path> <aligned_out_path>")
