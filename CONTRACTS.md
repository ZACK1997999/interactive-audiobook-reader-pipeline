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

Phase 2 adds [`contract_adapters.py`](contract_adapters.py) for the current JSON
format and [`alignment_backend.py`](alignment_backend.py) for the backend boundary.
`CurrentGlobalAlignmentBackend` is only a compatibility wrapper around the
existing aligner; it does not change production orchestration yet.

Phase 3 adds [`chapter_resolver.py`](chapter_resolver.py) and makes the pipeline
use the shared chapter artifact discovery path. Audio resolution remains explicit:
zero candidates are missing, one is selectable, and multiple candidates are
ambiguous.

Phase 4 adds [`chapter_locator.py`](chapter_locator.py), a backend-neutral,
Storyteller-inspired fuzzy locator. It returns `resolved`, `ambiguous`, or
`no-match` plus candidate evidence; it is not yet wired into automatic release
selection.

Phase 5 adds [`acoustic_backend.py`](acoustic_backend.py) and the optional
[`whisperx_backend.py`](whisperx_backend.py). Both acoustic backends expose
`AcousticWord`; WhisperX is lazy-loaded and remains opt-in through the
`whisperx` package extra.

Phase 5 adds [`acoustic_backend.py`](acoustic_backend.py) and the optional
[`whisperx_backend.py`](whisperx_backend.py). Both acoustic backends expose
`AcousticWord`; WhisperX is lazy-loaded and remains opt-in through the
`whisperx` package extra.

## Phase 0 fixtures

The synthetic fixtures in `fixtures/phase0/` describe one tiny book and are used
only to freeze contracts and regression behavior. They contain no copyrighted
book content and no real audio.
