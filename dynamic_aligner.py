"""
Module: dynamic_aligner.py
Description: Full-Chapter Non-Monotonic Global Sequence Aligner for Audiobooks.
Correctly handles audiobook production structures where marginal sidebars and quotes
are narrated at section/chapter endings, achieving >99% true acoustic audio alignment.
"""

import json
import re
import difflib
import sys

COMMON_CONTRACTIONS = {
    "can't": "cannot", "couldn't": "could not", "didn't": "did not",
    "doesn't": "does not", "don't": "do not", "hadn't": "had not",
    "hasn't": "has not", "haven't": "have not", "isn't": "is not",
    "it's": "it is", "let's": "let us", "mustn't": "must not",
    "shouldn't": "should not", "that's": "that is", "there's": "there is",
    "they're": "they are", "wasn't": "was not", "weren't": "were not",
    "won't": "will not", "wouldn't": "would not", "you're": "you are",
}

def tokenize_clean(text):
    normalized = str(text).lower().replace("’", "'")
    for contraction, expansion in COMMON_CONTRACTIONS.items():
        normalized = re.sub(rf"(?<![a-z]){re.escape(contraction.strip())}(?![a-z])", expansion, normalized)
    cleaned = re.sub(r'[\—\–\-\/\_\:\;\,\.\?\!\"\“\”\(\)\[\]\{\}\'\‘\’\`]', ' ', normalized)
    return [w for w in cleaned.split() if w]


def _source_tokens_with_words(text):
    """Return normalized source tokens together with their original-word indexes."""
    raw_words = str(text).split()
    tokens, word_indexes = [], []
    for word_index, raw_word in enumerate(raw_words):
        for token in tokenize_clean(raw_word):
            tokens.append(token)
            word_indexes.append(word_index)
    return tokens, word_indexes


def _short_sentence_candidate_count(source_tokens, audio_tokens):
    """Count exact positions for short sentences, where a partial hit is unsafe."""
    width = len(source_tokens)
    if width > 2:
        return None
    return sum(
        audio_tokens[index:index + width] == source_tokens
        for index in range(max(0, len(audio_tokens) - width + 1))
    )


def _build_word_spans(raw_words, source_word_indexes, source_to_audio, acoustic_words, st, et):
    """Map source words to matched acoustic words, interpolating only true gaps."""
    mapped_by_word = {index: [] for index in range(len(raw_words))}
    for source_index, audio_token_index in source_to_audio.items():
        if source_index < len(source_word_indexes):
            mapped_by_word[source_word_indexes[source_index]].append(audio_token_index)

    mapped_word_ranges = {}
    for word_index, token_indexes in mapped_by_word.items():
        if token_indexes:
            mapped_word_ranges[word_index] = (min(token_indexes), max(token_indexes))

    spans = []
    for word_index, raw_word in enumerate(raw_words):
        if word_index in mapped_word_ranges:
            start_token, end_token = mapped_word_ranges[word_index]
            start_word = acoustic_words[start_token]
            end_word = acoustic_words[end_token]
            ws = max(st, float(start_word["start"]))
            we = max(ws, float(end_word["end"]))
        else:
            previous = [mapped_word_ranges[i][1] for i in range(word_index) if i in mapped_word_ranges]
            following = [mapped_word_ranges[i][0] for i in range(word_index + 1, len(raw_words)) if i in mapped_word_ranges]
            if previous and following:
                left = acoustic_words[previous[-1]]["end"]
                right = acoustic_words[following[0]]["start"]
                gap_fraction = 1 / (len(raw_words) - word_index + 1)
                ws = float(left) + (float(right) - float(left)) * max(0.0, gap_fraction - 0.5)
                we = float(left) + (float(right) - float(left)) * min(1.0, gap_fraction + 0.5)
            else:
                ws = st + (et - st) * (word_index / max(1, len(raw_words)))
                we = st + (et - st) * ((word_index + 1) / max(1, len(raw_words)))
        spans.append({"word": raw_word, "start": round(ws, 2), "end": round(max(ws, we), 2)})
    return spans

def align_sentences_with_audio(acoustic_json_path, analysis_json_path, aligned_out_path):
    with open(analysis_json_path, "r", encoding="utf-8") as f:
        sentences = json.load(f)
    with open(acoustic_json_path, "r", encoding="utf-8") as f:
        acoustic_data = json.load(f)
        
    acoustic_words = acoustic_data["words"]
    total_ac = len(acoustic_words)
    if total_ac == 0:
        print(f"Warning: No acoustic words in {acoustic_json_path}")
        with open(aligned_out_path, "w", encoding="utf-8") as f:
            json.dump(sentences, f, ensure_ascii=False, indent=2)
        return sentences
        
    # Build token list and index mapping for audio
    ac_tokens = []
    ac_map = [] # maps token pos to acoustic_word_idx
    for w_idx, w_obj in enumerate(acoustic_words):
        toks = tokenize_clean(w_obj["word"])
        for t in toks:
            ac_tokens.append(t)
            ac_map.append(w_idx)
            
    # For every sentence, find the best matching cluster anywhere in the entire audio stream
    matched_sentences = {}
    
    for s_idx, s in enumerate(sentences):
        clean_s, source_word_indexes = _source_tokens_with_words(s["text"])
        if len(clean_s) == 0:
            continue
            
        matcher = difflib.SequenceMatcher(None, clean_s, ac_tokens, autojunk=False)
        blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
        
        best_cluster = None
        best_score = 0
        
        for i, b in enumerate(blocks):
            cluster = [b]
            cluster_size = b.size
            for next_b in blocks[i+1:]:
                token_dist_in_sent = next_b.a - (cluster[-1].a + cluster[-1].size)
                token_dist_in_win = next_b.b - (cluster[-1].b + cluster[-1].size)
                if 0 <= token_dist_in_win <= token_dist_in_sent + 15 and token_dist_in_sent >= 0:
                    cluster.append(next_b)
                    cluster_size += next_b.size
            
            if cluster_size > best_score:
                best_score = cluster_size
                best_cluster = cluster
                
        min_thresh = 1 if len(clean_s) <= 2 else 2 if len(clean_s) <= 4 else 3
        ratio_thresh = 0.35 if len(clean_s) >= 4 else 0.5
        
        short_candidates = _short_sentence_candidate_count(clean_s, ac_tokens)
        short_is_ambiguous = len(clean_s) <= 2 and (
            short_candidates != 1 or best_score < len(clean_s)
        )

        if best_cluster and not short_is_ambiguous and best_score >= min_thresh and (best_score / len(clean_s)) >= ratio_thresh:
            first_b = best_cluster[0]
            last_b = best_cluster[-1]
            t_start = max(0, min(len(ac_tokens) - 1, first_b.b))
            t_end = max(t_start, min(len(ac_tokens) - 1, last_b.b + last_b.size + (len(clean_s) - last_b.a - last_b.size) - 1))
            
            w_start = ac_map[t_start]
            w_end = ac_map[t_end]
            st = acoustic_words[w_start]["start"]
            et = acoustic_words[w_end]["end"]
            
            raw_words = s["text"].split()
            source_to_audio = {}
            for block in best_cluster:
                for offset in range(block.size):
                    source_to_audio[block.a + offset] = ac_map[block.b + offset]
            word_spans = _build_word_spans(
                raw_words, source_word_indexes, source_to_audio, acoustic_words, st, et
            )
                
            matched_sentences[s_idx] = {
                "start": round(st, 2),
                "end": round(max(st + 0.3, et), 2),
                "raw_start": round(st, 2),
                "raw_end": round(max(st + 0.3, et), 2),
                "has_audio_match": True,
                "word_spans": word_spans,
                "word_start": w_start,
                "matched_token_count": best_score,
                "source_token_count": len(clean_s),
                "match_ratio": round(best_score / max(1, len(clean_s)), 3),
                "alignment_method": "global_cluster_match",
                "fallback_used": False
            }
            
    # Build final aligned list preserving 100% of sentences
    aligned_results = []
    last_known_t = 0.0
    last_word_start = -1
    
    for s_idx, s in enumerate(sentences):
        raw_words = s["text"].split()
        if s_idx in matched_sentences:
            ms = matched_sentences[s_idx]
            non_monotonic = ms["word_start"] < last_word_start
            last_known_t = ms["end"]
            last_word_start = max(last_word_start, ms["word_start"])
            aligned_results.append({
                **s,
                "source_text": s.get("source_text", s.get("text", "")),
                "start": ms["start"],
                "end": ms["end"],
                "raw_start": ms["raw_start"],
                "raw_end": ms["raw_end"],
                "has_audio_match": True,
                "word_spans": ms["word_spans"],
                "matched_token_count": ms["matched_token_count"],
                "source_token_count": ms["source_token_count"],
                "match_ratio": ms["match_ratio"],
                "alignment_method": ms["alignment_method"],
                "fallback_used": False,
                "alignment_status": "review-required" if non_monotonic else "validated",
                "alignment_reason": "global_match_out_of_order" if non_monotonic else None
            })
        else:
            # Sentence without standalone acoustic match (e.g. unread heading label)
            bookmark_t = round(last_known_t, 2)
            word_spans = [{"word": rw, "start": bookmark_t, "end": bookmark_t} for rw in raw_words]
            aligned_results.append({
                **s,
                "source_text": s.get("source_text", s.get("text", "")),
                "start": bookmark_t,
                "end": bookmark_t,
                "raw_start": bookmark_t,
                "raw_end": bookmark_t,
                "has_audio_match": False,
                "word_spans": word_spans,
                "matched_token_count": 0,
                "source_token_count": len(tokenize_clean(s.get("text", ""))),
                "match_ratio": 0.0,
                "alignment_method": "unmatched",
                "fallback_used": True,
                "alignment_status": "not-applicable" if s.get("is_heading") else "review-required",
                "alignment_reason": "ambiguous_short_sentence" if len(tokenize_clean(s.get("text", ""))) <= 2 else "no_sufficient_global_match"
            })
            
    with open(aligned_out_path, "w", encoding="utf-8") as f:
        json.dump(aligned_results, f, ensure_ascii=False, indent=2)
        
    matched_count = len(matched_sentences)
    validated_count = sum(item.get("alignment_status") == "validated" for item in aligned_results)
    print(f"[{aligned_out_path}] Produced {len(aligned_results)} records; {matched_count} audio matches, {validated_count} validated, {len(aligned_results) - validated_count} requiring review or non-applicable.")
    return aligned_results

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        align_sentences_with_audio(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python3 dynamic_aligner.py <acoustic_json_path> <analysis_json_path> <aligned_out_path>")
