"""Evidence-preserving repair of sparse long-form ASR windows.

The first transcription pass remains the baseline. Only time windows bounded by
validated neighboring sentences are retranscribed, and a candidate replacement
is accepted only when a fresh alignment reduces the review-required set without
creating new failures elsewhere in the chapter.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from acoustic_whisper import (
    ACOUSTIC_PROFILE_VERSION,
    ACOUSTIC_TRANSCRIPTION_OPTIONS,
)
from artifact_io import atomic_write_json
from dynamic_aligner import align_sentences_with_audio, tokenize_clean


def _validated_audio_record(item):
    return (
        item.get("alignment_status") == "validated"
        and item.get("audio_start") is not None
        and item.get("audio_end") is not None
    )


def review_windows(aligned_records, *, padding=1.0, max_window=180.0):
    """Return merged acoustic windows surrounding contiguous review runs."""
    review_indexes = [
        index for index, item in enumerate(aligned_records)
        if item.get("alignment_status") == "review-required"
    ]
    runs = []
    for index in review_indexes:
        if not runs or index > runs[-1][-1] + 1:
            runs.append([index])
        else:
            runs[-1].append(index)

    windows = []
    for run in runs:
        first, last = run[0], run[-1]
        previous_index = next(
            (index for index in range(first - 1, -1, -1) if _validated_audio_record(aligned_records[index])),
            None,
        )
        following_index = next(
            (index for index in range(last + 1, len(aligned_records)) if _validated_audio_record(aligned_records[index])),
            None,
        )
        if previous_index is None or following_index is None:
            continue

        # A short sentence can be falsely anchored to a later repeated phrase.
        # If it follows a large unexplained audio gap, include it in the repair
        # window and use the preceding long anchor instead.
        previous = aligned_records[previous_index]
        previous_previous_index = next(
            (index for index in range(previous_index - 1, -1, -1) if _validated_audio_record(aligned_records[index])),
            None,
        )
        if (
            len(tokenize_clean(previous.get("source_text", previous.get("text", "")))) <= 2
            and previous_previous_index is not None
            and float(previous["audio_start"]) - float(aligned_records[previous_previous_index]["audio_end"]) >= 4.0
        ):
            first = previous_index
            previous_index = previous_previous_index
            previous = aligned_records[previous_index]

        replace_start = float(previous["audio_end"])
        replace_end = float(aligned_records[following_index]["audio_start"])
        start = max(0.0, replace_start - padding)
        end = replace_end + padding
        if end <= start or end - start > max_window:
            continue
        windows.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "replace_start": round(replace_start, 2),
            "replace_end": round(replace_end, 2),
            "first_sentence_id": aligned_records[first].get("id"),
            "last_sentence_id": aligned_records[last].get("id"),
        })

    merged = []
    for window in sorted(windows, key=lambda item: item["start"]):
        if merged and window["start"] <= merged[-1]["end"] + 0.25:
            merged[-1]["end"] = max(merged[-1]["end"], window["end"])
            merged[-1]["replace_end"] = max(merged[-1]["replace_end"], window["replace_end"])
            merged[-1]["last_sentence_id"] = window["last_sentence_id"]
        else:
            merged.append(dict(window))
    return merged


def _outside_windows(start, end, windows):
    midpoint = (float(start) + float(end)) / 2
    return not any(window["replace_start"] <= midpoint <= window["replace_end"] for window in windows)


def _review_ids(records):
    return {
        item.get("id") for item in records
        if item.get("alignment_status") == "review-required"
    }


def repair_acoustic_gaps(
    audio_path,
    acoustic_path,
    analysis_path,
    aligned_path,
    *,
    transcribe_fn=None,
):
    """Retranscribe bounded failure windows and accept only measurable gains."""
    if transcribe_fn is None:
        import mlx_whisper
        transcribe_fn = mlx_whisper.transcribe

    audio_path = Path(audio_path)
    acoustic_path = Path(acoustic_path)
    analysis_path = Path(analysis_path)
    aligned_path = Path(aligned_path)
    acoustic_data = json.loads(acoustic_path.read_text(encoding="utf-8"))
    aligned_records = json.loads(aligned_path.read_text(encoding="utf-8"))
    current_review_ids = _review_ids(aligned_records)
    prior_repair = acoustic_data.get("bounded_repair") or {}
    if (
        prior_repair.get("profile_version") == ACOUSTIC_PROFILE_VERSION
        and set(prior_repair.get("remaining_review_ids", [])) == current_review_ids
    ):
        return {
            "status": "already-attempted",
            "windows": prior_repair.get("windows", []),
            "review_before": len(current_review_ids),
        }
    windows = review_windows(aligned_records)
    if not windows:
        return {"status": "not-needed", "windows": [], "review_before": len(_review_ids(aligned_records))}

    # mlx-whisper currently processes the span between the first and last pair
    # when many disjoint clips are supplied together. Invoke each bounded clip
    # independently so sparse repairs do not silently become a full-chapter run.
    replacement_segments = []
    for window in windows:
        result = transcribe_fn(
            str(audio_path),
            path_or_hf_repo=acoustic_data.get("model", "mlx-community/whisper-large-v3-turbo"),
            word_timestamps=True,
            verbose=False,
            clip_timestamps=[window["start"], window["end"]],
            **ACOUSTIC_TRANSCRIPTION_OPTIONS,
        )
        replacement_segments.extend(result.get("segments", []))
    replacement_words = [word for segment in replacement_segments for word in segment.get("words", [])]
    if not replacement_words:
        return {"status": "no-acoustic-evidence", "windows": windows, "review_before": len(_review_ids(aligned_records))}

    existing_words = [
        word for word in acoustic_data.get("words", [])
        if _outside_windows(word.get("start", 0), word.get("end", 0), windows)
    ]
    normalized_replacements = [{
        "word": word.get("word", ""),
        "start": round(float(word.get("start", 0)), 2),
        "end": round(float(word.get("end", 0)), 2),
        "probability": round(float(word.get("probability", 0)), 4),
    } for word in replacement_words if (
        word.get("start") is not None
        and word.get("end") is not None
        and not _outside_windows(word["start"], word["end"], windows)
    )]
    candidate_words = sorted(existing_words + normalized_replacements, key=lambda word: (word["start"], word["end"]))

    existing_segments = [
        segment for segment in acoustic_data.get("segments", [])
        if _outside_windows(segment.get("start", 0), segment.get("end", 0), windows)
    ]
    candidate_segments = sorted(existing_segments + [{
        "id": segment.get("id"),
        "start": float(segment.get("start", 0)),
        "end": float(segment.get("end", 0)),
        "text": segment.get("text", ""),
    } for segment in replacement_segments if not _outside_windows(
        segment.get("start", 0), segment.get("end", 0), windows
    )], key=lambda segment: (segment["start"], segment["end"]))

    candidate_data = {
        **acoustic_data,
        "schema_version": 2,
        "acoustic_profile_version": ACOUSTIC_PROFILE_VERSION,
        "transcription_options": ACOUSTIC_TRANSCRIPTION_OPTIONS,
        "segments": candidate_segments,
        "words": candidate_words,
        "bounded_repair": {
            "profile_version": ACOUSTIC_PROFILE_VERSION,
            "base_acoustic_sha256": hashlib.sha256(acoustic_path.read_bytes()).hexdigest(),
            "windows": windows,
        },
    }

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        candidate_acoustic = root / "acoustic.json"
        candidate_aligned = root / "aligned.json"
        atomic_write_json(candidate_acoustic, candidate_data)
        candidate_records = align_sentences_with_audio(candidate_acoustic, analysis_path, candidate_aligned)

    before = _review_ids(aligned_records)
    after = _review_ids(candidate_records)
    new_failures = after - before
    if len(after) >= len(before) or new_failures:
        return {
            "status": "rejected",
            "windows": windows,
            "review_before": len(before),
            "review_after": len(after),
            "new_failures": sorted(new_failures),
        }

    candidate_data["bounded_repair"]["remaining_review_ids"] = sorted(after)
    atomic_write_json(acoustic_path, candidate_data)
    atomic_write_json(aligned_path, candidate_records)
    return {
        "status": "accepted",
        "windows": windows,
        "review_before": len(before),
        "review_after": len(after),
        "resolved": sorted(before - after),
    }
