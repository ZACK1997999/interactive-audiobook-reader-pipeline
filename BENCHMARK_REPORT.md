# Alignment backend benchmark

## Scope

This is an isolated synthetic sample-chapter benchmark. It uses four invented
sentences and sixteen synthetic acoustic words. The audio begins with a
two-word publisher introduction, then contains the main text, followed by a
sidebar/quote that is narrated out of canonical reading order. No real book,
copyrighted text, model, or audiobook file was used.

Important: Phase 4 currently provides a Storyteller-inspired **chapter-start
locator**, not a replacement sentence aligner. Therefore the comparison is:

1. Legacy path: current global sentence alignment over the full audio stream.
2. Locator-assisted path: chapter-start localization, audio slicing, absolute
   timestamp restoration, then the same current global sentence aligner.

## Results

| Metric | Legacy full-audio path | Locator-assisted path |
|---|---:|---:|
| Source sentences | 4 | 4 |
| Audio words | 16 | localized from token 2 |
| Audio matches | 4 | 4 |
| Validated records | 3 | 3 |
| Review-required records | 1 | 1 |
| Sentence-start timestamps | 1.0, 3.0, 6.0, 5.0 | 1.0, 3.0, 6.0, 5.0 |

The locator returned `resolved`, selected token `2`, and scored the chapter
opening at similarity `1.0`. It removed the two-word introduction for the
alignment pass and restored the original absolute timestamps exactly.

## Interpretation

- The new locator introduces no regression on this sample.
- It solves the chapter-start discovery problem independently of sentence
  alignment.
- It preserves the release policy: the out-of-order sidebar is still marked
  `review-required` rather than being silently accepted.
- The benchmark does **not** prove that the new path is more accurate for
  every book. It proves that the new prepass can be added safely without
  changing the current sentence-alignment result on this representative case.

## Decision

Keep the locator isolated until a larger benchmark corpus exists. Do not merge
it into automatic production selection solely because this one sample passes.
The next meaningful benchmark should include skipped forewords, repeated
chapter openings, transcription substitutions, and multiple candidate tracks.
