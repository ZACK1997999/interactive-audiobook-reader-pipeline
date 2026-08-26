import json
import re
import difflib

def norm_word(w):
    return re.sub(r'[^a-zA-Z0-9]', '', w).lower()

def robust_monotonic_align(acoustic_words, sentences):
    total_ac = len(acoustic_words)
    total_s = len(sentences)
    
    ac_tokens = [norm_word(w["word"]) for w in acoustic_words]
    
    # 1. First pass: find unambiguous monotonic anchor matches
    anchors = {} # s_idx -> (ac_start, ac_end, score)
    
    last_ac = 0
    for s_idx, s in enumerate(sentences):
        text = s["text"]
        raw_words = text.split()
        clean = [norm_word(w) for w in raw_words if norm_word(w)]
        if len(clean) < 4:
            continue
            
        # Search in a forward monotonic window of reasonable size
        search_start = last_ac
        search_end = min(total_ac, last_ac + 1200)
        window = ac_tokens[search_start:search_end]
        
        matcher = difflib.SequenceMatcher(None, clean, window)
        match = matcher.find_longest_match(0, len(clean), 0, len(window))
        
        if match.size >= max(3, int(len(clean) * 0.5)):
            ac_start = search_start + match.b - match.a
            ac_end = search_start + match.b + match.size + (len(clean) - match.a - match.size)
            ac_start = max(0, min(total_ac - 1, ac_start))
            ac_end = max(ac_start, min(total_ac - 1, ac_end))
            
            # Ensure monotonicity
            if ac_start >= last_ac:
                anchors[s_idx] = (ac_start, ac_end)
                last_ac = ac_start
                
    print(f"Found {len(anchors)} strong monotonic anchors out of {total_s} sentences.")
    
    # 2. Second pass: interpolate and fine-match all sentences between anchors
    aligned = []
    
    # Add boundary anchors
    anchor_indices = sorted(anchors.keys())
    if 0 not in anchors:
        anchors[0] = (0, min(5, total_ac - 1))
        anchor_indices = [0] + anchor_indices
    if (total_s - 1) not in anchors:
        anchors[total_s - 1] = (max(0, total_ac - 10), total_ac - 1)
        anchor_indices.append(total_s - 1)
        
    for i in range(len(anchor_indices) - 1):
        s_start_idx = anchor_indices[i]
        s_end_idx = anchor_indices[i + 1]
        
        ac_start_bound = anchors[s_start_idx][0]
        ac_end_bound = anchors[s_end_idx][1]
        
        num_s = s_end_idx - s_start_idx + 1
        
        # Align each sentence in this segment
        seg_last_ac = ac_start_bound
        for seg_k in range(s_start_idx, s_end_idx):
            s = sentences[seg_k]
            raw_words = s["text"].split()
            clean = [norm_word(w) for w in raw_words if norm_word(w)]
            
            # Search within bounded range [seg_last_ac, ac_end_bound]
            search_window = ac_tokens[seg_last_ac:ac_end_bound + 1]
            if len(clean) >= 2 and len(search_window) >= len(clean):
                matcher = difflib.SequenceMatcher(None, clean, search_window)
                m = matcher.find_longest_match(0, len(clean), 0, len(search_window))
                if m.size >= 2:
                    matched_start = seg_last_ac + m.b - m.a
                    matched_end = seg_last_ac + m.b + m.size + (len(clean) - m.a - m.size)
                    c_start = max(seg_last_ac, min(total_ac - 1, matched_start))
                    c_end = max(c_start, min(total_ac - 1, matched_end))
                else:
                    # Linear interpolation fallback within anchor bounds
                    frac = (seg_k - s_start_idx) / max(1, (s_end_idx - s_start_idx))
                    frac_next = (seg_k - s_start_idx + 1) / max(1, (s_end_idx - s_start_idx))
                    c_start = int(ac_start_bound + frac * (ac_end_bound - ac_start_bound))
                    c_end = int(ac_start_bound + frac_next * (ac_end_bound - ac_start_bound))
            else:
                frac = (seg_k - s_start_idx) / max(1, (s_end_idx - s_start_idx))
                frac_next = (seg_k - s_start_idx + 1) / max(1, (s_end_idx - s_start_idx))
                c_start = int(ac_start_bound + frac * (ac_end_bound - ac_start_bound))
                c_end = int(ac_start_bound + frac_next * (ac_end_bound - ac_start_bound))
                
            c_start = max(0, min(total_ac - 1, c_start))
            c_end = max(c_start, min(total_ac - 1, c_end))
            seg_last_ac = c_start
            
            raw_st = acoustic_words[c_start]["start"]
            raw_et = max(raw_st + 0.8, acoustic_words[c_end]["end"])
            
            # Word spans
            word_spans = []
            span_count = len(raw_words)
            for w_i, rw in enumerate(raw_words):
                target_ac = min(total_ac - 1, c_start + w_i)
                if target_ac <= c_end:
                    ws = acoustic_words[target_ac]["start"]
                    we = acoustic_words[target_ac]["end"]
                else:
                    w_frac = w_i / max(1, span_count)
                    w_frac_next = (w_i + 1) / max(1, span_count)
                    ws = round(raw_st + w_frac * (raw_et - raw_st), 2)
                    we = round(raw_st + w_frac_next * (raw_et - raw_st), 2)
                word_spans.append({"word": rw, "start": ws, "end": we})
                
            aligned.append({
                **s,
                "start": round(max(0.0, raw_st - 0.15), 2),
                "end": round(raw_et + 0.30, 2),
                "raw_start": round(raw_st, 2),
                "raw_end": round(raw_et, 2),
                "word_spans": word_spans
            })
            
    # Add last sentence
    last_s = sentences[-1]
    last_ac_start, last_ac_end = anchors[total_s - 1]
    raw_st = acoustic_words[last_ac_start]["start"]
    raw_et = max(raw_st + 1.0, acoustic_words[last_ac_end]["end"])
    last_words = last_s["text"].split()
    last_word_spans = []
    for w_i, rw in enumerate(last_words):
        target_ac = min(total_ac - 1, last_ac_start + w_i)
        ws = acoustic_words[target_ac]["start"]
        we = acoustic_words[target_ac]["end"]
        last_word_spans.append({"word": rw, "start": ws, "end": we})
    aligned.append({
        **last_s,
        "start": round(max(0.0, raw_st - 0.15), 2),
        "end": round(raw_et + 0.30, 2),
        "raw_start": round(raw_st, 2),
        "raw_end": round(raw_et, 2),
        "word_spans": last_word_spans
    })
    
    return aligned

# Test on Chapter 3
with open("/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Range - David Epstein/audio/range_ch03_acoustic_words.json") as f:
    ac = json.load(f)["words"]
with open("/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Range - David Epstein/range_ch03_full_analysis.json") as f:
    sents = json.load(f)

res = robust_monotonic_align(ac, sents)
print(f"Total aligned sentences in Ch 3: {len(res)}")
print(f"First sentence: {res[0]['start']}s - {res[0]['end']}s")
print(f"Middle sentence (s-200): {res[200]['start']}s - {res[200]['end']}s ({res[200]['text'][:40]}...)")
print(f"Sentence (s-300): {res[300]['start']}s - {res[300]['end']}s ({res[300]['text'][:40]}...)")
print(f"Last sentence: {res[-1]['start']}s - {res[-1]['end']}s ({res[-1]['text'][:40]}...)")

# Audit monotonicity
issues = 0
prev = -1
for s in res:
    if s['start'] < prev:
        print(f"Non-monotonic in {s['id']}: prev={prev}, cur={s['start']}")
        issues += 1
    prev = s['start']
print(f"Audit completed: {issues} non-monotonic issues!")
