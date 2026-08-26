# Stable internal contracts

Phase 1 defines the domain vocabulary shared by future preparation and alignment
backends. The implementation is in [`models.py`](models.py).

These models are an internal boundary, not a replacement for the current JSON
files. Existing `*_canonical_sentences.json`, `*_full_analysis.json`, and
`*_aligned_sentences.json` files remain unchanged until a later compatibility
adapter phase.

## Objects

- `CanonicalSentence`: immutable-in-practice EPUB ground truth and reading order.
- `AudioTrack`: one physical audiobook track and its identity/provenance.
- `AcousticWord`: one timestamped word emitted by an acoustic backend.
- `WordSpan`: one source word's playback interval and optional mapping evidence.
- `AlignmentRecord`: one sentence's sentence-level and word-level alignment result.
- `VocabularyItem`: one contextual learning item from linguistic analysis.
- `LinguisticAnalysis`: translation and selected learning items for one canonical sentence.
- `ValidationReport`: release-gate result and diagnostics outside the reader.

All future backends must produce these concepts without exposing backend-specific
objects to the HTML reader. `SCHEMA_VERSION` is currently `1.0`.

## Phase 0 fixtures

The synthetic fixtures in `fixtures/phase0/` describe one tiny book and are used
only to freeze contracts and regression behavior. They contain no copyrighted
book content and no real audio.
