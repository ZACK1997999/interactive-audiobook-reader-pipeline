"""Backend boundary for sentence/audio alignment."""

from pathlib import Path
from typing import List, Protocol, Union

from contract_adapters import alignment_records_from_json
from dynamic_aligner import align_sentences_with_audio
from models import AlignmentRecord


PathLike = Union[str, Path]


class AlignmentBackend(Protocol):
    """Minimal contract all future alignment implementations must satisfy."""

    name: str

    def align(
        self,
        acoustic_json_path: PathLike,
        analysis_json_path: PathLike,
        aligned_out_path: PathLike,
    ) -> List[AlignmentRecord]:
        ...


class CurrentGlobalAlignmentBackend:
    """Compatibility wrapper around the proven current global aligner."""

    name = "current-global"

    def align(self, acoustic_json_path, analysis_json_path, aligned_out_path):
        align_sentences_with_audio(
            acoustic_json_path,
            analysis_json_path,
            aligned_out_path,
        )
        import json

        with open(aligned_out_path, "r", encoding="utf-8") as handle:
            return alignment_records_from_json(json.load(handle))
