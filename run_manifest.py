"""Create reproducibility metadata without processing or copying book content."""

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from artifact_io import atomic_write_json


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_manifest(book_dir, source_files, audio_files, model="mlx-community/whisper-large-v3-turbo"):
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        revision = None
    manifest = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_revision": revision,
        "acoustic_model": model,
        "source_files": [{"path": str(path.resolve()), "sha256": sha256(path)} for path in source_files],
        "audio_files": [{"path": str(path.resolve()), "sha256": sha256(path)} for path in audio_files],
    }
    output = book_dir / "reader_run_manifest.json"
    atomic_write_json(output, manifest)
    return output


def update_manifest(book_dir, chapters, status="in_progress", model="mlx-community/whisper-large-v3-turbo"):
    """Write a resumable chapter-stage manifest without copying book content."""
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        revision = None
    manifest = {
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_revision": revision,
        "acoustic_model": model,
        "status": status,
        "chapters": chapters,
    }
    output = Path(book_dir) / "reader_run_manifest.json"
    atomic_write_json(output, manifest)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir", type=Path)
    parser.add_argument("--source", type=Path, action="append", default=[])
    parser.add_argument("--audio", type=Path, action="append", default=[])
    parser.add_argument("--model", default="mlx-community/whisper-large-v3-turbo")
    args = parser.parse_args()
    print(create_manifest(args.book_dir.expanduser().resolve(), args.source, args.audio, args.model))


if __name__ == "__main__":
    main()
