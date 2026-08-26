"""Storyteller-inspired fuzzy discovery of a chapter inside an audio track."""

from dataclasses import dataclass
import difflib
import re
from typing import List


def _tokens(text):
    return [token for token in re.sub(r"[^a-z0-9']+", " ", str(text).lower()).split() if token]


@dataclass(frozen=True)
class ChapterMatchCandidate:
    start_token: int
    end_token: int
    matched_token_count: int
    source_token_count: int
    similarity: float


@dataclass(frozen=True)
class ChapterLocation:
    status: str
    candidates: List[ChapterMatchCandidate]

    @property
    def selected(self):
        return self.candidates[0] if self.status == "resolved" else None


def locate_chapter_start(source_text, acoustic_words, *, lookahead=24, threshold=0.60, margin=0.08):
    """Find a likely chapter start while exposing ambiguity instead of guessing."""
    source_tokens = _tokens(source_text)
    audio_tokens = _tokens(" ".join(item.get("word", "") for item in acoustic_words))
    if not source_tokens or not audio_tokens:
        return ChapterLocation("no-match", [])

    source_tokens = source_tokens[:lookahead]
    window_width = len(source_tokens)
    candidates = []
    for start in range(max(1, len(audio_tokens) - window_width + 2)):
        window = audio_tokens[start:start + window_width]
        if not window:
            continue
        matcher = difflib.SequenceMatcher(None, source_tokens, window, autojunk=False)
        matched = sum(block.size for block in matcher.get_matching_blocks())
        similarity = matched / max(len(source_tokens), len(window))
        if similarity >= threshold:
            candidates.append(ChapterMatchCandidate(start, start + len(window), matched, len(source_tokens), round(similarity, 3)))

    candidates.sort(key=lambda item: (-item.similarity, -item.matched_token_count, item.start_token))
    if not candidates:
        return ChapterLocation("no-match", [])
    if len(candidates) > 1 and candidates[1].similarity >= candidates[0].similarity - margin:
        return ChapterLocation("ambiguous", candidates[:5])
    return ChapterLocation("resolved", candidates[:5])
