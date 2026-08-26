"""Stable domain models shared by preparation, alignment, validation, and readers.

These models are intentionally independent of any alignment backend or UI.  The
current JSON files remain the external compatibility format until adapters are
introduced in a later phase.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = "1.0"


@dataclass
class CanonicalSentence:
    sentence_id: str
    text: str
    is_heading: bool = False
    source_index: Optional[int] = None


@dataclass
class AudioTrack:
    track_id: str
    path: str
    chapter_number: Optional[int] = None
    duration_seconds: Optional[float] = None
    format: Optional[str] = None
    sha256: Optional[str] = None


@dataclass
class AcousticWord:
    word: str
    start: float
    end: float
    probability: Optional[float] = None
    token_index: Optional[int] = None


@dataclass
class WordSpan:
    word: str
    start: float
    end: float
    source_word_index: Optional[int] = None
    acoustic_word_start: Optional[int] = None
    acoustic_word_end: Optional[int] = None


@dataclass
class AlignmentRecord:
    sentence_id: str
    source_text: str
    start: float
    end: float
    word_spans: List[WordSpan] = field(default_factory=list)
    raw_start: Optional[float] = None
    raw_end: Optional[float] = None
    has_audio_match: bool = False
    matched_token_count: int = 0
    source_token_count: int = 0
    match_ratio: float = 0.0
    alignment_method: str = "unknown"
    fallback_used: bool = False
    alignment_status: str = "review-required"
    alignment_reason: Optional[str] = None


@dataclass
class VocabularyItem:
    word: str
    pos: str
    definition: str


@dataclass
class LinguisticAnalysis:
    sentence_id: str
    text: str
    translation: str
    vocabulary: List[VocabularyItem] = field(default_factory=list)


@dataclass
class ValidationReport:
    book_dir: str
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    release_ready: bool = False
