# Reproduce the workflow

This repository contains reusable code and contracts only. Keep copyrighted EPUBs, audiobooks, generated readers, private notes, and credentials outside Git.

## Roles

- Gemini reads `LINGUISTIC_ANALYSIS_PROMPT.md` and produces one `*_full_analysis.json` per chapter.
- Local scripts extract canonical text, run MLX Whisper, align audio, validate data, and compile HTML.
- Deployment is a separate deliberate action after validation.

## Setup

Use Python 3.9+ on macOS. Core processing uses the standard library. For Apple Silicon acoustic extraction:

```bash
python3 -m pip install -e '.[acoustic]'
```

The default model is `mlx-community/whisper-large-v3-turbo`.

## Per-chapter contract

For slug `example_book` and chapter `01`, provide:

```text
example_book_ch01_canonical_sentences.json
example_book_ch01_full_analysis.json
audio/example_book_ch01_acoustic_words.json
audio/chapter_01.mp3
```

The analysis file must preserve canonical IDs and order. Run the local release gate before building:

```bash
reader-validate /path/to/private/book-output --report /path/to/private/book-output/reader_validation_report.json
```

Any warning or error blocks release. Weak, estimated, missing, or out-of-order alignment is never silently accepted.
