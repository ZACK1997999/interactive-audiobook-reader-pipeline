# Fourth Wing unmatched-pattern classification

Run basis: regenerated Chapter 1–39 aligned artifacts from the existing canonical,
linguistic-analysis, and acoustic-word files. Classification is evidence-based;
unresolved records remain release-blocking.

| Class | Count | Evidence | Release treatment |
|---|---:|---|---|
| Leading audiobook attribution / epigraph | 38 resolved | Opening acoustic window contains `A quote from`, `An excerpt from`, or `From`; fuzzy citation binding has real word timestamps | Algorithmically validated |
| Typographic ellipsis / pause marker | 33 | Source token is only `…`/`...`; it has no lexical token that can be truthfully played or highlighted | `non_narrated_text`, with per-record evidence |
| Printed chapter heading / spoken numeric variant | 38 resolved | Acoustic opening contains spoken `Chapter N`, while printed text uses a different number spelling/format | Algorithmically validated |
| Short dialogue or proper name | 55 | Short text is ambiguous or has repeated/weak acoustic candidates; 99 exact occurrences across this class | Must fix or prove with bounded acoustic mapping |
| Body text with no sufficient global match | 57 | No exact occurrence; 10 have fuzzy similarity ≥ 0.70, 22 are below 0.50 | Must fix or prove omission from the source/audio pair |
| Printed attribution candidate | 2 | Dash-prefixed citation remains unmatched after the leading-attribution pass | Must inspect individually |

## Current gate state

- Leading attribution records resolved: 38.
- Spoken numeric chapter headings resolved: 38.
- Confirmed typographic `non_narrated_text` records: 33.
- Remaining algorithmic review records: 129 (59 `no_sufficient_global_match`, 56 `ambiguous_short_sentence`, plus 14 records requiring individual inspection after the structural passes).
- Full report: `reader_validation_report.json` in the Fourth Wing source directory.
- `release_ready`: `false`.

The 33 ellipsis records are the only records automatically classified as
non-narrated in this run. Chapter headings are mapped to their spoken numeric
variants. No body sentence or short dialogue is being batch-approved.
