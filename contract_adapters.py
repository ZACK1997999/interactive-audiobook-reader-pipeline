"""Adapters between the existing JSON artifacts and stable domain models."""

from typing import Any, Dict, Iterable, List

from models import (
    AcousticWord,
    AlignmentRecord,
    CanonicalSentence,
    LinguisticAnalysis,
    VocabularyItem,
    WordSpan,
)


def canonical_sentences_from_json(items: Iterable[Dict[str, Any]]) -> List[CanonicalSentence]:
    return [
        CanonicalSentence(
            sentence_id=item["id"],
            text=item["text"],
            is_heading=bool(item.get("is_heading", False)),
            source_index=index,
        )
        for index, item in enumerate(items)
    ]


def acoustic_words_from_json(data: Dict[str, Any]) -> List[AcousticWord]:
    return [
        AcousticWord(
            word=item["word"],
            start=float(item["start"]),
            end=float(item["end"]),
            probability=item.get("probability"),
            token_index=index,
        )
        for index, item in enumerate(data.get("words", []))
    ]


def linguistic_analysis_from_json(items: Iterable[Dict[str, Any]]) -> List[LinguisticAnalysis]:
    return [
        LinguisticAnalysis(
            sentence_id=item["id"],
            text=item["text"],
            translation=item.get("trans", ""),
            vocabulary=[
                VocabularyItem(
                    word=vocab["word"],
                    pos=vocab.get("pos", ""),
                    definition=vocab.get("def", ""),
                )
                for vocab in item.get("vocab", [])
            ],
        )
        for item in items
    ]


def alignment_records_from_json(items: Iterable[Dict[str, Any]]) -> List[AlignmentRecord]:
    records = []
    for item in items:
        records.append(
            AlignmentRecord(
                sentence_id=item["id"],
                source_text=item.get("source_text", item.get("text", "")),
                start=float(item["start"]) if isinstance(item.get("start"), (int, float)) else None,
                end=float(item["end"]) if isinstance(item.get("end"), (int, float)) else None,
                raw_start=item.get("raw_start"),
                raw_end=item.get("raw_end"),
                word_spans=[
                    WordSpan(
                        word=span["word"],
                        start=float(span["start"]) if isinstance(span.get("start"), (int, float)) else None,
                        end=float(span["end"]) if isinstance(span.get("end"), (int, float)) else None,
                        timing_source=span.get("timing_source", "observed"),
                    )
                    for span in item.get("word_spans", [])
                ],
                has_audio_match=bool(item.get("has_audio_match", False)),
                matched_token_count=int(item.get("matched_token_count", 0)),
                source_token_count=int(item.get("source_token_count", 0)),
                match_ratio=float(item.get("match_ratio", 0.0)),
                alignment_method=item.get("alignment_method", "legacy"),
                fallback_used=bool(item.get("fallback_used", False)),
                alignment_status=item.get("alignment_status", "review-required"),
                alignment_reason=item.get("alignment_reason"),
            )
        )
    return records


def alignment_record_to_json(record: AlignmentRecord, *, text: str = None) -> Dict[str, Any]:
    """Serialize the stable alignment model using the current artifact field names."""
    result = {
        "id": record.sentence_id,
        "text": text if text is not None else record.source_text,
        "source_text": record.source_text,
        "start": record.start,
        "end": record.end,
        "raw_start": record.raw_start,
        "raw_end": record.raw_end,
        "has_audio_match": record.has_audio_match,
        "word_spans": [
            {"word": span.word, "start": span.start, "end": span.end, "timing_source": span.timing_source}
            for span in record.word_spans
        ],
        "matched_token_count": record.matched_token_count,
        "source_token_count": record.source_token_count,
        "match_ratio": record.match_ratio,
        "alignment_method": record.alignment_method,
        "fallback_used": record.fallback_used,
        "alignment_status": record.alignment_status,
        "alignment_reason": record.alignment_reason,
    }
    return result
