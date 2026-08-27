"""Canonical, machine-readable contracts for reproducible book publication."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from artifact_io import atomic_write_json


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_audio_manifest(
    audio_dir: Path,
    book_id: str,
    public_base_url: Optional[str] = None,
    chapter_count: Optional[int] = None,
    source_files: Optional[Iterable[Path]] = None,
) -> Dict:
    """Map each logical chapter to one immutable source file and public object.

    Callers should pass ``source_files`` when a book has non-chapter extras or a
    nonstandard naming scheme. The fallback is deterministic filename sorting,
    never loose chapter-number globbing.
    """
    audio_dir = Path(audio_dir).expanduser().resolve()
    candidates = [Path(path).expanduser().resolve() for path in source_files] if source_files is not None else sorted(audio_dir.glob("*.mp3"))
    if chapter_count is None:
        chapter_count = len(candidates)
    if len(candidates) != chapter_count:
        raise ValueError("source_files count must equal chapter_count")
    entries: List[Dict] = []
    for chapter, source in enumerate(candidates, 1):
        if not source.is_file():
            raise FileNotFoundError(source)
        object_name = f"chapter_{chapter:02d}.mp3"
        entry = {
            "chapter": chapter,
            "source_path": str(source),
            "source_sha256": sha256(source),
            "object_key": f"{book_id}/{object_name}",
            "bytes": source.stat().st_size,
        }
        if public_base_url:
            entry["public_url"] = f"{public_base_url.rstrip('/')}/{entry['object_key']}"
        entries.append(entry)
    return {
        "schema_version": 1,
        "book_id": book_id,
        "chapter_count": chapter_count,
        "entries": entries,
        "audio_urls": [entry["public_url"] for entry in entries if "public_url" in entry],
    }


def write_audio_manifest(path: Path, manifest: Dict) -> Path:
    atomic_write_json(path, manifest)
    return Path(path)
