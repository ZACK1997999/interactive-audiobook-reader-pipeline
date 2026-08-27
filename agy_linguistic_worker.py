"""Agy adapter for one chapter of linguistic analysis.

Inputs are passed by the coordinator through READER_* environment variables.
The worker returns only the contract JSON and never edits the source book.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from artifact_io import atomic_write_json


PROMPT_PATH = Path(__file__).with_name("LINGUISTIC_ANALYSIS_PROMPT.md")


def _json_from_output(raw: str):
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def main() -> int:
    canonical = Path(os.environ["READER_CANONICAL_PATH"])
    output = Path(os.environ["READER_OUTPUT_PATH"])
    prompt = (
        PROMPT_PATH.read_text(encoding="utf-8")
        + "\n\nRead the canonical JSON file at: " + str(canonical)
        + "\nReturn valid JSON only, preserving every id, text, and order."
    )
    completed = subprocess.run(
        ["agy", "--mode", "plan", "--output-format", "text", "--print-timeout", "1h", "--print", prompt],
        cwd=str(canonical.parent), text=True, capture_output=True, timeout=3700,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "agy failed")[-4000:])
    data = _json_from_output(completed.stdout)
    canonical_data = json.loads(canonical.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != len(canonical_data):
        raise RuntimeError("agy output must be a list with the same record count as canonical input")
    canonical_ids = [item.get("id") for item in canonical_data]
    output_ids = [item.get("id") for item in data]
    if output_ids != canonical_ids:
        raise RuntimeError("agy output IDs/order differ from canonical input")
    for item, source in zip(data, canonical_data):
        if item.get("text") != source.get("text") or not str(item.get("trans", "")).strip():
            raise RuntimeError(f"invalid agy record for {item.get('id')}")
    atomic_write_json(output, data)
    print(f"agy linguistic analysis written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
