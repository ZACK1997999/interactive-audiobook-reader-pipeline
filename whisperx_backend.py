"""Optional WhisperX acoustic backend.

WhisperX is imported only when this backend is used. This keeps the default MLX
installation lightweight and preserves the Apple Silicon path.
"""

from pathlib import Path
import json
from typing import List

from models import AcousticWord


class WhisperXBackend:
    name = "whisperx"

    def __init__(self, model_name="large-v2", language="en", device="cpu", batch_size=4,
                 compute_type=None, align_model=None, whisperx_module=None):
        self.model_name = model_name
        self.language = language
        self.device = device
        self.batch_size = batch_size
        self.compute_type = compute_type or ("int8" if device == "cpu" else "float16")
        self.align_model = align_model
        self._whisperx = whisperx_module

    def _module(self):
        if self._whisperx is None:
            import importlib
            self._whisperx = importlib.import_module("whisperx")
        return self._whisperx

    def transcribe(self, audio_path, output_json_path=None) -> List[AcousticWord]:
        whisperx = self._module()
        model = whisperx.load_model(
            self.model_name, self.device, compute_type=self.compute_type, language=self.language
        )
        result = model.transcribe(str(audio_path), batch_size=self.batch_size)
        language_code = result.get("language", self.language)
        align_kwargs = {"language_code": language_code, "device": self.device}
        if self.align_model:
            align_kwargs["model_name"] = self.align_model
        model_a, metadata = whisperx.load_align_model(**align_kwargs)
        aligned = whisperx.align(
            result.get("segments", []),
            model_a,
            metadata,
            whisperx.load_audio(str(audio_path)),
            self.device,
            return_char_alignments=False,
        )
        words = []
        for segment in aligned.get("segments", []):
            for item in segment.get("words", []):
                if item.get("start") is None or item.get("end") is None:
                    continue
                words.append(AcousticWord(
                    word=item.get("word", "").strip(),
                    start=float(item["start"]),
                    end=float(item["end"]),
                    probability=item.get("score", item.get("probability")),
                    token_index=len(words),
                ))
        if output_json_path is not None:
            Path(output_json_path).write_text(
                json.dumps({
                    "model": self.model_name,
                    "backend": self.name,
                    "word_timestamps": True,
                    "words": [
                        {"word": word.word, "start": word.start, "end": word.end, "probability": word.probability}
                        for word in words
                    ],
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return words
