"""MLX Whisper adapter for one chapter of acoustic word timestamps."""

from __future__ import annotations

import os
import json
from pathlib import Path

from acoustic_whisper import run_mlx_acoustic_extraction


def main() -> int:
    sources = json.loads(os.environ.get("READER_AUDIO_PATHS_JSON", "[]"))
    if len(sources) > 1:
        raise RuntimeError(
            "the approved intake maps this chapter to multiple audio tracks; "
            "use a playlist-aware acoustic worker or consolidate the tracks before extraction"
        )
    audio = Path(sources[0] if sources else os.environ["READER_AUDIO_PATH"])
    output = Path(os.environ["READER_OUTPUT_PATH"])
    if not audio.is_file():
        raise FileNotFoundError(f"audio input does not exist: {audio}")
    run_mlx_acoustic_extraction(
        str(audio), str(output), os.environ.get("READER_WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
