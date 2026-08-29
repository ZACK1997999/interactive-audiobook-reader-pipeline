"""Release gate for reader data; diagnostics stay outside the reader."""

import argparse
import json
import re
from pathlib import Path
from audio_resolver import resolve_chapter_audio
from artifact_io import atomic_write_json
from release_token import issue_release_token

MULTI_BOUNDARY = re.compile(r"(?:[.!?][\"'”’)]*|\*)\s+[A-Z]")
ABBREVIATION_BEFORE_CAPITAL = re.compile(
    r"(?:Mrs|Mr|Ms|Dr|Prof|Sr|Jr|Rev|Hon|Gen|Col|Maj|Capt|Lt|Sgt|Cpl|Pvt|Gov|Sen|Rep|Pres|Sec|Amb|Insp|Det|St|Mt|Ft|Mme|Mlle|Esq|Ph\.D|M\.D|B\.A|M\.A|U\.S|U\.K|U\.S\.A|e\.g|i\.e|vs|etc|al|fig|pp|vol|no|Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec|\b[A-Z])$"
)
MIN_CHAPTER_AUDIO_COVERAGE = 0.95


def _suspicious_sentence_boundaries(text: str) -> list[str]:
    """Return boundary matches after excluding whitelisted prose abbreviations."""
    return [
        match.group(0)
        for match in MULTI_BOUNDARY.finditer(text)
        if not ABBREVIATION_BEFORE_CAPITAL.search(text[:match.start()])
    ]

def _chapter_audio_exists(audio_dir: Path, number: int) -> bool:
    """Return true only when the shared resolver finds exactly one candidate."""
    return resolve_chapter_audio(audio_dir, number).status == "ok"


def _load_review_ledger(book_dir: Path, errors: list[str]) -> dict[tuple[int, str], dict]:
    """Load explicit owner decisions without changing the underlying evidence."""
    path = book_dir / "reader_review_ledger.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        errors.append("reader_review_ledger.json: invalid JSON")
        return {}
    reviews = data.get("reviews") if isinstance(data, dict) else None
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(reviews, list):
        errors.append("reader_review_ledger.json: invalid schema")
        return {}
    decisions = {}
    for entry in reviews:
        if not isinstance(entry, dict):
            errors.append("reader_review_ledger.json: malformed review entry")
            continue
        chapter = entry.get("chapter")
        sentence_ids = entry.get("sentence_ids")
        if sentence_ids is None:
            sentence_ids = [entry.get("sentence_id")]
        required = (entry.get("decision"), entry.get("reviewer"), entry.get("evidence"))
        if not isinstance(chapter, int) or not isinstance(sentence_ids, list) or not sentence_ids or any(not isinstance(item_id, str) or not item_id.strip() for item_id in sentence_ids) or not all(isinstance(value, str) and value.strip() for value in required) or entry.get("decision") != "accepted":
            errors.append(f"reader_review_ledger.json: invalid review entry ({chapter})")
            continue
        for sentence_id in sentence_ids:
            key = (chapter, sentence_id)
            if key in decisions:
                errors.append(f"reader_review_ledger.json: duplicate review entry ({chapter}/{sentence_id})")
            decisions[key] = entry
    return decisions


def validate(book_dir: Path, report_path=None):
    errors, warnings, chapters = [], [], []
    review_ledger = _load_review_ledger(book_dir, errors)
    if review_ledger:
        errors.append(
            "reader_review_ledger.json contains alignment exceptions; release is blocked "
            "because manual exceptions cannot waive algorithmic alignment failures"
        )
        review_ledger = {}
    accepted_exceptions = []
    manifest_entries = {}
    manifest_path = book_dir / "reader_run_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_entries = {item.get("chapter"): item for item in manifest.get("chapters", [])}
        except (OSError, ValueError, TypeError):
            errors.append("reader_run_manifest.json: invalid JSON")
    canonical_files = sorted(book_dir.glob("*_ch*_canonical_sentences.json"))
    if not canonical_files:
        errors.append("No canonical sentence files found")

    for canonical in canonical_files:
        match = re.search(r"ch(\d+)", canonical.name)
        number = int(match.group(1)) if match else None
        label = f"Ch {number:02d}" if number is not None else canonical.name
        try:
            data = json.loads(canonical.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{canonical.name}: invalid JSON ({exc})")
            continue
        ids = [item.get("id") for item in data]
        if any(not item_id for item_id in ids):
            errors.append(f"{label}: missing sentence ID")
        if len(ids) != len(set(ids)):
            errors.append(f"{label}: duplicate sentence IDs")
        suspicious = [item.get("id") for item in data if not item.get("is_heading") and _suspicious_sentence_boundaries(item.get("text", "")) and (number, item.get("id")) not in review_ledger]
        if suspicious:
            warnings.append(f"{label}: {len(suspicious)} suspicious sentence boundaries ({', '.join(suspicious[:8])})")
        record = {"chapter": number, "canonical_records": len(data), "suspicious_records": len(suspicious)}

        analysis = book_dir / canonical.name.replace("_canonical_sentences.json", "_full_analysis.json")
        if not analysis.exists():
            errors.append(f"{label}: linguistic analysis file missing")
        else:
            try:
                analysis_data = json.loads(analysis.read_text(encoding="utf-8"))
                canonical_by_id = {item.get("id"): item for item in data}
                if not isinstance(analysis_data, list):
                    errors.append(f"{label}: analysis must be a JSON list")
                    analysis_data = []
                if len(analysis_data) != len(data):
                    errors.append(f"{label}: analysis record count mismatch")
                if [item.get("id") for item in analysis_data] != ids:
                    errors.append(f"{label}: analysis IDs/order differ from canonical source")
                allowed_keys = {"id", "text", "trans", "vocab", "is_heading", "elem_idx", "tag"}
                for item in analysis_data:
                    item_id = item.get("id", "<unknown>")
                    if not isinstance(item.get("trans"), str) or not item.get("trans", "").strip():
                        errors.append(f"{label} {item_id}: missing or empty translation")
                    if item.get("text") != canonical_by_id.get(item_id, {}).get("text"):
                        errors.append(f"{label} {item_id}: analysis text differs from canonical source")
                    vocab = item.get("vocab")
                    if not isinstance(vocab, list) or len(vocab) > 3:
                        errors.append(f"{label} {item_id}: malformed vocabulary list")
                    else:
                        for entry in vocab:
                            if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry.get(k).strip() for k in ("word", "pos", "def")):
                                errors.append(f"{label} {item_id}: malformed vocabulary item")
                    unexpected = set(item) - allowed_keys
                    if unexpected:
                        errors.append(f"{label} {item_id}: unexpected analysis fields ({', '.join(sorted(unexpected))})")
                record["analysis_records"] = len(analysis_data)
            except Exception as exc:
                errors.append(f"{analysis.name}: invalid JSON ({exc})")
        if number is not None:
            audio_resolution = resolve_chapter_audio(book_dir / "audio", number)
            if audio_resolution.status == "missing":
                errors.append(f"{label}: chapter audio file missing")
            elif audio_resolution.status == "ambiguous":
                names = ", ".join(path.name for path in audio_resolution.candidates)
                errors.append(f"{label}: ambiguous chapter audio candidates ({names})")

        aligned = book_dir / canonical.name.replace("_canonical_sentences.json", "_aligned_sentences.json")
        manifest_entry = manifest_entries.get(number, {})
        expected_hash = manifest_entry.get("aligned_sha256")
        if expected_hash and aligned.exists():
            import hashlib
            digest = hashlib.sha256(aligned.read_bytes()).hexdigest()
            if digest != expected_hash:
                errors.append(f"{label}: aligned artifact changed after manifest creation")
        if not aligned.exists():
            errors.append(f"{label}: aligned file missing")
            record["status"] = "not-aligned"
            chapters.append(record)
            continue
        try:
            aligned_data = json.loads(aligned.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{aligned.name}: invalid JSON ({exc})")
            record["status"] = "failed"
            chapters.append(record)
            continue

        record["aligned_records"] = len(aligned_data)
        record["aligned"] = str(aligned.relative_to(book_dir))
        import hashlib
        record["aligned_sha256"] = hashlib.sha256(aligned.read_bytes()).hexdigest()
        if len(aligned_data) != len(data):
            errors.append(f"{label}: canonical/aligned count mismatch")
        if [item.get("id") for item in aligned_data] != ids:
            errors.append(f"{label}: aligned IDs/order differ from canonical source")

        previous_start = -1.0
        review_ids = []
        covered_tokens = 0
        expected_tokens = 0
        for item in aligned_data:
            item_id = item.get("id", "<unknown>")
            is_heading = item.get("is_heading", False)
            owner_accepted = (number, item_id) in review_ledger
            if owner_accepted:
                accepted_exceptions.append({"chapter": number, "sentence_id": item_id, **review_ledger[(number, item_id)]})
            approved_non_monotonic = (
                item.get("alignment_status") == "reviewed"
                and item.get("alignment_reason") == "global_match_out_of_order"
                and isinstance(item.get("review_evidence"), str)
                and bool(item.get("review_evidence", "").strip())
                and item.get("has_audio_match") is True
                and not item.get("fallback_used")
                and float(item.get("match_ratio", 0.0)) >= 0.5
            )
            non_narrated = item.get("alignment_status") == "not-applicable" and item.get("alignment_reason") == "non_narrated_content"
            if not is_heading and not non_narrated and not owner_accepted and (not item.get("word_spans") or not item.get("has_audio_match", True)):
                errors.append(f"{label} {item_id}: missing audio word spans")
            raw_start = item.get("raw_start", item.get("start"))
            raw_end = item.get("raw_end", item.get("end"))
            start = float(raw_start) if isinstance(raw_start, (int, float)) else None
            end = float(raw_end) if isinstance(raw_end, (int, float)) else None
            participates_in_timeline = not owner_accepted and not non_narrated
            if participates_in_timeline and start is not None and start < previous_start and not approved_non_monotonic:
                errors.append(f"{label} {item_id}: non-monotonic raw start")
            if start is not None and end is not None and end < start:
                errors.append(f"{label} {item_id}: end precedes start")
            # Missing-match records are reported once above. Their null spans
            # are intentional and must not create one duplicate error per word.
            spans_to_validate = item.get("word_spans", []) if item.get("has_audio_match") else []
            for span in spans_to_validate:
                span_start_raw = span.get("start")
                span_end_raw = span.get("end")
                span_start = float(span_start_raw) if isinstance(span_start_raw, (int, float)) else None
                span_end = float(span_end_raw) if isinstance(span_end_raw, (int, float)) else None
                if span_start is None or span_end is None or span_start < 0 or span_end < span_start:
                    errors.append(f"{label} {item_id}: invalid word span")
            if participates_in_timeline:
                if start is not None:
                    previous_start = start
            ratio = float(item.get("match_ratio", 0.0))
            matched = int(item.get("matched_token_count", 0))
            source_tokens = int(item.get("source_token_count", 0))
            if not is_heading and not non_narrated and not owner_accepted:
                expected_tokens += max(source_tokens, 0)
                covered_tokens += min(max(matched, 0), max(source_tokens, 0))
            if not is_heading and not non_narrated and not owner_accepted and (not item.get("has_audio_match", True) or item.get("fallback_used") or item.get("alignment_status") not in {"validated", "reviewed"} or matched < 1 or ratio < 0.5):
                review_ids.append(item_id)
        record["review_required_records"] = len(review_ids)
        coverage = covered_tokens / expected_tokens if expected_tokens else 1.0
        record["acoustic_coverage"] = coverage
        record["covered_audio_tokens"] = covered_tokens
        record["expected_audio_tokens"] = expected_tokens
        if coverage < MIN_CHAPTER_AUDIO_COVERAGE:
            errors.append(
                f"{label}: acoustic coverage {coverage:.1%} is below the "
                f"{MIN_CHAPTER_AUDIO_COVERAGE:.0%} release threshold"
            )
        if review_ids:
            warnings.append(f"{label}: {len(review_ids)} alignment records require review ({', '.join(review_ids[:8])})")
            record["status"] = "review-required"
        else:
            record["status"] = "validated"
        chapters.append(record)

    result = {"book_dir": str(book_dir.resolve()), "chapters": chapters, "accepted_review_exceptions": accepted_exceptions, "errors": errors, "warnings": warnings, "release_ready": not errors and not warnings}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if report_path:
        atomic_write_json(report_path, result)
    return 0 if result["release_ready"] else 1


def validate_for_release(book_dir: Path, report_path: Path):
    """Validate and return (report, token); a failed gate returns no token."""
    code = validate(book_dir, report_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if code != 0:
        return report, None
    return report, issue_release_token(book_dir, report_path, report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    return validate(args.book_dir.expanduser().resolve(), args.report)


if __name__ == "__main__":
    raise SystemExit(main())
