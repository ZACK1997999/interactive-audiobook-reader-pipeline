# Reproduce the workflow

This repository contains reusable code and contracts only. Keep copyrighted EPUBs, audiobooks, generated readers, private notes, and credentials outside Git.

The backend-neutral domain models and synthetic Phase 0 fixtures are documented in
[`CONTRACTS.md`](CONTRACTS.md). They freeze the internal vocabulary without changing the current
JSON files or reader output.

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
Translations must be non-empty, vocabulary entries must contain `word`, `pos`, and `def`, and
analysis must preserve canonical text and record order. Generated artifacts use atomic replacement;
partial files are not treated as completed stages. `reader_run_manifest.json` records chapter state
and input/output hashes for resumability and tamper detection.

Out-of-order matches are valid only when the alignment evidence is strong and the record has
been explicitly changed from `review-required` to `reviewed` with reason
`global_match_out_of_order`. This separates canonical reading order from physical audio order
without allowing automatic global matching to bypass review.

## Publication verification

Public audio is verified with a ranged `GET`, matching how HTML5 audio streams media. A `HEAD`
request alone is not a sufficient release check because some public object endpoints reject `HEAD`
while correctly serving byte ranges.

```bash
python3 publication_verify.py \
  https://cdn.example/book/chapter_01.mp3 \
  https://cdn.example/book/chapter_63.mp3
```

Keep R2/S3 credentials in the environment, OS keychain, or a secret manager. Never commit them to
an uploader script, chat export, or repository. The public URL is safe to publish; write-access
credentials are not.
