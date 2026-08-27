# Reader optimization and release standard

This is the acceptance standard for deciding whether an optimization is complete.
An optimization is not complete because code was changed; it is complete only when
the relevant invariant is documented, tested, and independently checked.

## Required release invariants

| Area | Pass condition | Evidence |
|---|---|---|
| Audio identity | Every chapter maps to exactly one explicit source and object; ambiguous or changed files block release | `audio_manifest.json`, hashes, validator report |
| Input reproducibility | Canonical, analysis, acoustic, and audio inputs are hashed; changed inputs trigger re-alignment | `reader_run_manifest.json` |
| Acoustic quality | Every chapter reaches at least 95% eligible acoustic-token coverage | validation report |
| Reader contract | Required controls, chapter sections, audio source, and JavaScript handlers exist | `quality_gate.py` smoke report |
| Semantic quality | Human-reviewed samples explicitly pass translation, alignment meaning, and vocabulary checks | `reader_semantic_review.json` |
| Run isolation | Two runs for the same book cannot mutate the same output concurrently | process lock and regression test |
| Publication truth | `compiled` means local HTML exists only; `published` and `externally_verified` require separate evidence | manifest status and publication report |

## Evidence levels

- `VERIFIED`: directly checked by a deterministic test or external probe.
- `REVIEWED`: checked by a named human against the source/audio.
- `SUPPORTED`: supported by multiple checks but not mechanically proven.
- `UNVERIFIED`: not enough evidence; never describe as complete.

## Semantic sampling rule

Semantic quality cannot honestly be inferred from JSON validity. A semantic review
must name the reviewer, date, method, sampled sentence IDs, and explicitly pass:

1. translation accuracy;
2. alignment meaning and chapter identity;
3. vocabulary usefulness and correctness.

For a new book, sample the beginning, middle, end, and at least one random chapter.
The review record is evidence of sampling, not a claim that every sentence is perfect.
