# Fourth Wing unmatched-pattern classification

Run basis: regenerated Chapter 1–39 aligned artifacts from the existing canonical,
linguistic-analysis, and acoustic-word files. Classification is evidence-based;
unresolved records remain release-blocking.

| Class | Count | Evidence | Release treatment |
|---|---:|---|---|
| Leading audiobook attribution / epigraph | 38 resolved | Opening acoustic window contains `A quote from`, `An excerpt from`, or `From`; fuzzy citation binding has real word timestamps | Algorithmically validated |
| Typographic ellipsis / pause marker | 33 | Source token is only `…`/`...`; it has no lexical token that can be truthfully played or highlighted | `non_narrated_text`, with per-record evidence |
| Printed chapter heading / spoken numeric variant | 38 resolved | Acoustic opening contains spoken `Chapter N`, while printed text uses a different number spelling/format | Algorithmically validated |
| Bounded acoustic recovery | 43 resolved across accepted windows | Fresh short-window ASR with cross-window prompting disabled reduced long-form sparse-ASR failures; Chapter 9 reduced 10→0 and Chapter 12 13→1 | Accepted only when review set strictly decreased |
| Short dialogue or proper name | 16 direct unresolved records; more low-quality records remain gate-visible | Repeated names, interjections, and very short phrases still have ambiguous candidates | Must fix or prove with bounded acoustic mapping |
| Body text / ASR variant | 11 direct unresolved records; several now recovered by local retranscription | Remaining records need a unique local match or explicit evidence | Must fix or prove; never use a timestamp fallback |
| Structural or order conflict | 1 direct out-of-order record plus gate-visible structural records | Chapter-opening metadata and ambiguous boundaries require separate handling | Must inspect individually |

## Current gate state

- Leading attribution records resolved: 38.
- Spoken numeric chapter headings resolved: 38.
- Confirmed typographic `non_narrated_text` records: 33.
- Remaining gate-visible review records: 39; 27 records still lack usable word spans, one has a structural order conflict, and one legacy review ledger still blocks release.
- Accepted bounded acoustic recovery is recorded in `acoustic_repair_report.json` in the Fourth Wing source directory.
- Full report: `reader_validation_report.json` in the Fourth Wing source directory.
- `release_ready`: `false`.

The 33 ellipsis records are the only records automatically classified as
non-narrated in this run. Chapter headings are mapped to their spoken numeric
variants. No body sentence or short dialogue is being batch-approved without a
fresh acoustic match and a measurable gate improvement.
