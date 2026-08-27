"""MLX Whisper adapter for one chapter of acoustic word timestamps."""

from __future__ import annotations

import os
from pathlib import Path

from acoustic_whisper import run_mlx_acoustic_extraction


def main() -> int:
    audio = Path(os.environ["READER_AUDIO_PATH"])
    output = Path(os.environ["READER_OUTPUT_PATH"])
    if not audio.is_file():
        raise FileNotFoundError(f"audio input does not exist: {audio}")
    run_mlx_acoustic_extraction(
        str(audio), str(output), os.environ.get("READER_WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
