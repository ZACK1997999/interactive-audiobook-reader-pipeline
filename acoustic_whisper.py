"""
Module: acoustic_whisper.py
Description: Apple Silicon GPU-Accelerated MLX Whisper Word Timestamp Extractor.
"""

import json
import time
import sys
from artifact_io import atomic_write_json

ACOUSTIC_PROFILE_VERSION = 2
ACOUSTIC_TRANSCRIPTION_OPTIONS = {
    "condition_on_previous_text": False,
    "hallucination_silence_threshold": 2.0,
    "language": "en",
}


def run_mlx_acoustic_extraction(
    audio_path,
    output_json_path,
    model_name="mlx-community/whisper-large-v3-turbo",
    *,
    transcribe_fn=None,
):
    if transcribe_fn is None:
        import mlx_whisper
        transcribe_fn = mlx_whisper.transcribe
    
    print(f"Starting MLX Whisper acoustic extraction on {audio_path} using {model_name}...")
    start_t = time.time()
    
    result = transcribe_fn(
        audio_path,
        path_or_hf_repo=model_name,
        word_timestamps=True,
        verbose=False,
        **ACOUSTIC_TRANSCRIPTION_OPTIONS,
    )
    
    words_list = []
    segments_list = []
    
    for seg in result.get("segments", []):
        segments_list.append({
            "id": seg.get("id"),
            "start": seg.get("start"),
            "end": seg.get("end"),
            "text": seg.get("text")
        })
        for w in seg.get("words", []):
            words_list.append({
                "word": w.get("word"),
                "start": round(w.get("start", 0.0), 2),
                "end": round(w.get("end", 0.0), 2),
                "probability": round(w.get("probability", 0.0), 4)
            })
            
    output_data = {
        "schema_version": 2,
        "acoustic_profile_version": ACOUSTIC_PROFILE_VERSION,
        "model": model_name,
        "transcription_options": ACOUSTIC_TRANSCRIPTION_OPTIONS,
        "word_timestamps": True,
        "segments": segments_list,
        "words": words_list
    }
    
    atomic_write_json(output_json_path, output_data)
        
    elapsed = round(time.time() - start_t, 2)
    print(f"Acoustic extraction complete in {elapsed}s! Total words extracted: {len(words_list)} -> {output_json_path}")
    return output_data

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        model = sys.argv[3] if len(sys.argv) >= 4 else "mlx-community/whisper-large-v3-turbo"
        run_mlx_acoustic_extraction(sys.argv[1], sys.argv[2], model)
    else:
        print("Usage: python3 acoustic_whisper.py <audio_path> <output_json_path> [model_name]")
