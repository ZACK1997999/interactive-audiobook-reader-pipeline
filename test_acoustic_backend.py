import unittest
import tempfile
from pathlib import Path

from models import AcousticWord
from whisperx_backend import WhisperXBackend


class FakeWhisperModel:
    def transcribe(self, audio_path, batch_size):
        return {"language": "en", "segments": [{"words": []}]}


class FakeWhisperX:
    def load_model(self, model_name, device, compute_type, language):
        return FakeWhisperModel()

    def load_align_model(self, language_code, device):
        return "align-model", {"language": language_code}

    def load_audio(self, audio_path):
        return audio_path

    def align(self, segments, model, metadata, audio, device, return_char_alignments):
        return {"segments": [{"words": [
            {"word": " Alpha ", "start": 0.1, "end": 0.4, "score": 0.98},
            {"word": "begins", "start": 0.4, "end": 0.8},
        ]}]}


class AcousticBackendTests(unittest.TestCase):
    def test_whisperx_backend_is_lazy_and_returns_acoustic_words(self):
        backend = WhisperXBackend(whisperx_module=FakeWhisperX())
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "acoustic.json"
            words = backend.transcribe("fixture.mp3", output)
            self.assertTrue(output.exists())
        self.assertEqual(backend.name, "whisperx")
        self.assertEqual(words, [
            AcousticWord("Alpha", 0.1, 0.4, 0.98, 0),
            AcousticWord("begins", 0.4, 0.8, None, 1),
        ])


if __name__ == "__main__":
    unittest.main()
