# Phase 0 baseline

This refactor branch starts from `main` commit `2022c99`:

```text
merge: unify audio resolution contract
```

The baseline is protected by Git history. Phase 0 uses only synthetic fixtures
under [`fixtures/phase0/`](fixtures/phase0/); no EPUB, audiobook, generated
reader, or private book output is included.

The baseline test suite passed before Phase 1 changes. Phase 1 adds contract
tests without changing the reader, validator semantics, Gemini prompt, or
existing JSON output format.
