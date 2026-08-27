# Operational learning-loop upgrade benchmark

Date: 2026-08-27

The benchmark ran the upgraded orchestrator in isolated temporary copies of
the completed book artifacts. Original book directories were not rewritten.

| Book | Chapters | Canonical records | Aligned records | Release result | Errors | Warnings | HTML built |
|---|---:|---:|---:|---|---:|---:|---|
| The Housemaid | 63 | 9,366 | 9,366 | PASS | 0 | 0 | yes |
| Range | 13 | 4,604 | 4,604 | BLOCKED | 460 | 16 | no |
| The Confidence Game | 11 | 7,322 | 7,322 | BLOCKED | 17 | 20 | no |

The Housemaid is a complete end-to-end pass under the upgraded workflow.
Range and The Confidence Game expose legacy-artifact compatibility and
alignment-quality gaps when their existing data is re-aligned by the current
backend. The branch therefore does not claim that all historical workflows are
100% preserved. No release gate was weakened and no HTML was compiled for a
book whose validation failed.

Regression verification on the branch:

```text
python3 -m unittest discover -q
34 tests passed
git diff --check
passed
```
