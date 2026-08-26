"""Release gate for reader data; diagnostics stay outside the reader."""

import argparse
import json
import re
from pathlib import Path

MULTI_BOUNDARY = re.compile(r"(?:[.!?][\"'”’)]*|\*)\s+[A-Z]")

def _chapter_audio_exists(audio_dir: Path, number: int) -> bool:
    """Accept only the canonical name or filenames that explicitly encode the chapter."""
    canonical = audio_dir / f"chapter_{number:02d}.mp3"
    if canonical.exists():
        return True
    pattern = re.compile(rf"(?<!\d)(?:chapter|ch)[ _-]*0*{number}(?!\d)", re.IGNORECASE)
    candidates = [path for path in audio_dir.glob("*.mp3") if pattern.search(path.name)]
    return bool(candidates)


def validate(book_dir: Path, report_path=None):
    errors, warnings, chapters = [], [], []
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
        suspicious = [item.get("id") for item in data if not item.get("is_heading") and MULTI_BOUNDARY.search(item.get("text", ""))]
        if suspicious:
            warnings.append(f"{label}: {len(suspicious)} suspicious sentence boundaries ({', '.join(suspicious[:8])})")
        record = {"chapter": number, "canonical_records": len(data), "suspicious_records": len(suspicious)}

        analysis = book_dir / canonical.name.replace("_canonical_sentences.json", "_full_analysis.json")
        if not analysis.exists():
            errors.append(f"{label}: linguistic analysis file missing")
        else:
            try:
                analysis_data = json.loads(analysis.read_text(encoding="utf-8"))
                if [item.get("id") for item in analysis_data] != ids:
                    errors.append(f"{label}: analysis IDs/order differ from canonical source")
                record["analysis_records"] = len(analysis_data)
            except Exception as exc:
                errors.append(f"{analysis.name}: invalid JSON ({exc})")
        if number is not None and not _chapter_audio_exists(book_dir / "audio", number):
            errors.append(f"{label}: chapter audio file missing")

        aligned = book_dir / canonical.name.replace("_canonical_sentences.json", "_aligned_sentences.json")
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
        if len(aligned_data) != len(data):
            errors.append(f"{label}: canonical/aligned count mismatch")
        if [item.get("id") for item in aligned_data] != ids:
            errors.append(f"{label}: aligned IDs/order differ from canonical source")

        previous_start = -1.0
        review_ids = []
        for item in aligned_data:
            item_id = item.get("id", "<unknown>")
            is_heading = item.get("is_heading", False)
            approved_non_monotonic = (
                item.get("alignment_status") == "reviewed"
                and item.get("alignment_reason") == "global_match_out_of_order"
                and item.get("has_audio_match") is True
                and not item.get("fallback_used")
                and float(item.get("match_ratio", 0.0)) >= 0.5
            )
            if not is_heading and (not item.get("word_spans") or not item.get("has_audio_match", True)):
                errors.append(f"{label} {item_id}: missing audio word spans")
            start = float(item.get("raw_start", item.get("start", -1)))
            end = float(item.get("raw_end", item.get("end", -1)))
            if start < previous_start and not approved_non_monotonic:
                errors.append(f"{label} {item_id}: non-monotonic raw start")
            if end < start:
                errors.append(f"{label} {item_id}: end precedes start")
            for span in item.get("word_spans", []):
                span_start = float(span.get("start", -1))
                span_end = float(span.get("end", -1))
                if span_start < 0 or span_end < span_start:
                    errors.append(f"{label} {item_id}: invalid word span")
            previous_start = start
            ratio = float(item.get("match_ratio", 0.0))
            matched = int(item.get("matched_token_count", 0))
            if not is_heading and (not item.get("has_audio_match", True) or item.get("fallback_used") or item.get("alignment_status") not in {"validated", "reviewed"} or matched < 1 or ratio < 0.5):
                review_ids.append(item_id)
        record["review_required_records"] = len(review_ids)
        if review_ids:
            warnings.append(f"{label}: {len(review_ids)} alignment records require review ({', '.join(review_ids[:8])})")
            record["status"] = "review-required"
        else:
            record["status"] = "validated"
        chapters.append(record)

    result = {"book_dir": str(book_dir.resolve()), "chapters": chapters, "errors": errors, "warnings": warnings, "release_ready": not errors and not warnings}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output + "\n", encoding="utf-8")
    return 0 if result["release_ready"] else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    return validate(args.book_dir.expanduser().resolve(), args.report)


if __name__ == "__main__":
    raise SystemExit(main())
