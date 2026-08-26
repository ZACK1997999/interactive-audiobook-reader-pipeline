"""Single source of truth for chapter-audio discovery."""

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class AudioResolution:
    candidates: tuple[Path, ...]

    @property
    def status(self):
        if not self.candidates:
            return "missing"
        if len(self.candidates) > 1:
            return "ambiguous"
        return "ok"

    @property
    def path(self):
        return self.candidates[0] if self.status == "ok" else None


def resolve_chapter_audio(audio_dir, chapter_number):
    """Resolve zero, one, or multiple explicit chapter-number filenames."""
    audio_dir = Path(audio_dir)
    pattern = re.compile(
        rf"(?<!\d)(?:chapter|ch)[ _-]*0*{chapter_number}(?!\d)",
        re.IGNORECASE,
    )
    candidates = {
        path.resolve()
        for path in audio_dir.glob("*.mp3")
        if pattern.search(path.name)
    }
    return AudioResolution(tuple(sorted(candidates)))
