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
from typing import Any

from artifact_io import atomic_write_json


PROMPT_PATH = Path(__file__).with_name("LINGUISTIC_ANALYSIS_PROMPT.md")
CHUNK_SIZE = 50


def _json_from_output(raw: str):
    text = raw.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        extracted = match.group(1).strip()
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            pass
    if text.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", text)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        array_match = re.search(r"(\[\s*\{[\s\S]*\}\s*\])", text)
        if array_match:
            return json.loads(array_match.group(1))
        raise


def chunk_sentences(sentences: list[dict], chunk_size: int = CHUNK_SIZE) -> list[list[dict]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    return [sentences[i:i + chunk_size] for i in range(0, len(sentences), chunk_size)]


def build_batch_prompt(base_prompt: str, batch: list[dict], batch_idx: int, total_batches: int) -> str:
    batch_json = json.dumps(batch, ensure_ascii=False, indent=2)
    return (
        f"{base_prompt.strip()}\n\n"
        f"Input canonical records (batch {batch_idx + 1} of {total_batches}, {len(batch)} items):\n"
        f"```json\n{batch_json}\n```\n\n"
        "Return valid JSON only (a JSON array containing the analyzed objects for this specific batch), "
        "preserving every id, text, and order."
    )


def verify_analysis(data: Any, canonical_data: list[dict]) -> None:
    if not isinstance(data, list):
        raise RuntimeError("analysis output must be a list")
    if len(data) != len(canonical_data):
        raise RuntimeError(
            f"analysis record count mismatch: got {len(data)}, expected {len(canonical_data)}"
        )
    canonical_ids = [item.get("id") for item in canonical_data]
    output_ids = [item.get("id") for item in data]
    if output_ids != canonical_ids:
        raise RuntimeError("analysis output IDs/order differ from canonical input")
    for item, source in zip(data, canonical_data):
        item_id = item.get("id")
        if item.get("text") != source.get("text"):
            raise RuntimeError(f"text mismatch for record {item_id}")
        trans = item.get("trans")
        if not isinstance(trans, str) or not trans.strip():
            raise RuntimeError(f"missing or empty translation for record {item_id}")
        vocab = item.get("vocab")
        if not isinstance(vocab, list):
            raise RuntimeError(f"vocab must be a list for record {item_id}")
        for entry in vocab:
            if not isinstance(entry, dict) or not all(
                isinstance(entry.get(k), str) and entry.get(k).strip()
                for k in ("word", "pos", "def")
            ):
                raise RuntimeError(f"malformed vocabulary item in record {item_id}")


def process_canonical_sentences(
    canonical_data: list[dict],
    base_prompt: str,
    cwd: Path,
    chunk_size: int = CHUNK_SIZE,
    timeout: int = 3700,
) -> list[dict]:
    chunks = chunk_sentences(canonical_data, chunk_size=chunk_size)
    if not chunks:
        return []

    master_list: list[dict] = []
    for batch_idx, batch in enumerate(chunks):
        prompt = build_batch_prompt(base_prompt, batch, batch_idx, len(chunks))
        try:
            completed = subprocess.run(
                ["agy", "--mode", "plan", "--output-format", "text", "--print-timeout", "1h", "--print", prompt],
                cwd=str(cwd),
                text=True,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"agy timed out on batch {batch_idx + 1}/{len(chunks)}") from exc
        if completed.returncode != 0:
            error_msg = (completed.stderr or completed.stdout or "agy failed")[-4000:]
            raise RuntimeError(f"agy failed on batch {batch_idx + 1}/{len(chunks)}: {error_msg}")
        batch_result = _json_from_output(completed.stdout)
        if not isinstance(batch_result, list):
            raise RuntimeError(f"agy output for batch {batch_idx + 1} must be a JSON list")
        if len(batch_result) != len(batch):
            raise RuntimeError(
                f"agy output for batch {batch_idx + 1} returned {len(batch_result)} items, expected {len(batch)}"
            )
        master_list.extend(batch_result)

    verify_analysis(master_list, canonical_data)
    return master_list


def main(environ: dict[str, str] | None = None) -> int:
    env = os.environ if environ is None else environ
    canonical_path = Path(env["READER_CANONICAL_PATH"])
    output_path = Path(env["READER_OUTPUT_PATH"])

    canonical_data = json.loads(canonical_path.read_text(encoding="utf-8"))
    if not isinstance(canonical_data, list):
        raise RuntimeError(f"canonical data at {canonical_path} must be a JSON list")

    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    analyzed_data = process_canonical_sentences(
        canonical_data=canonical_data,
        base_prompt=base_prompt,
        cwd=canonical_path.parent,
    )

    atomic_write_json(output_path, analyzed_data)
    print(f"agy linguistic analysis written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
