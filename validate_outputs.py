"""Validate generated reader data without modifying it."""
import argparse, json, re
from pathlib import Path

MULTI_BOUNDARY = re.compile(r"(?:[.!?][\"'”’)]*|\*)\s+[A-Z]")

def validate(book_dir: Path):
    errors, warnings, chapters = [], [], []
    for canonical in sorted(book_dir.glob("range_ch*_canonical_sentences.json")):
        n = canonical.name.split("ch")[1].split("_")[0]
        aligned = book_dir / f"range_ch{n}_aligned_sentences.json"
        try: data = json.loads(canonical.read_text(encoding="utf-8"))
        except Exception as e: errors.append(f"{canonical.name}: invalid JSON ({e})"); continue
        ids = [x.get("id") for x in data]
        if len(ids) != len(set(ids)): errors.append(f"Ch {n}: duplicate IDs")
        suspicious = [x.get("id") for x in data if not x.get("is_heading") and MULTI_BOUNDARY.search(x.get("text", ""))]
        if suspicious: warnings.append(f"Ch {n}: {len(suspicious)} suspicious multi-boundary records ({', '.join(suspicious[:8])})")
        record = {"chapter": int(n), "canonical_records": len(data), "suspicious_records": len(suspicious)}
        if aligned.exists():
            adata = json.loads(aligned.read_text(encoding="utf-8")); record["aligned_records"] = len(adata)
            if len(adata) != len(data): errors.append(f"Ch {n}: canonical/aligned count mismatch")
            prev = -1.0
            for item in adata:
                if not item.get("word_spans"): errors.append(f"Ch {n} {item.get('id')}: missing word spans")
                start = float(item.get("raw_start", item.get("start", -1)))
                if start < prev: errors.append(f"Ch {n} {item.get('id')}: non-monotonic raw start")
                prev = start
            record["status"] = "review-required" if suspicious else "auto-aligned"
        else:
            record["status"] = "not-aligned"; warnings.append(f"Ch {n}: aligned file missing")
        chapters.append(record)
    result = {"book_dir": str(book_dir), "chapters": chapters, "errors": errors, "warnings": warnings, "release_ready": not errors and not warnings}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("book_dir", type=Path)
    raise SystemExit(validate(p.parse_args().book_dir.expanduser().resolve()))
