"""Replaceable acoustic transcription backend boundary."""

from pathlib import Path
import tempfile
from typing import List, Protocol, Union

from acoustic_whisper import run_mlx_acoustic_extraction
from contract_adapters import acoustic_words_from_json
from models import AcousticWord


PathLike = Union[str, Path]


class AcousticBackend(Protocol):
    name: str

    def transcribe(self, audio_path: PathLike, output_json_path: PathLike = None) -> List[AcousticWord]:
        ...


class MLXWhisperBackend:
    """Compatibility wrapper for the existing Apple Silicon MLX backend."""

    name = "mlx-whisper"

    def transcribe(self, audio_path, output_json_path=None, model_name="mlx-community/whisper-large-v3-turbo"):
        temporary_path = None
        if output_json_path is None:
            temporary_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
            temporary_path = Path(temporary_file.name)
            temporary_file.close()
            output_json_path = temporary_path
        data = run_mlx_acoustic_extraction(audio_path, output_json_path, model_name)
        if temporary_path:
            temporary_path.unlink(missing_ok=True)
        return acoustic_words_from_json(data)
