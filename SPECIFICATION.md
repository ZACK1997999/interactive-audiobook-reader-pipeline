# Industrial Interactive Audiobook Reader Specification & Architecture (v3.0)

## 1. System Overview
The **Interactive Audiobook Reader Pipeline** is a fully automated, Apple Books-grade bilingual reading and listening system. It transforms raw book text (EPUB/Markdown) and complete audiobooks (MP3) into synchronized standalone web applications with sub-second karaoke word tracking, collapsible sentence-by-sentence Machiavellian/philosophical translations, and B2+/C1/C2 vocabulary breakdowns. Abridged and course audio require a declared, hash-bound audio-content profile and a separately supplied spoken source; they are never inferred from duration.

---

## 2. Core Architectural Pillars & Lessons Learned

### Pillar I: Full-Chapter Non-Monotonic Global Alignment (`dynamic_aligner.py`)
- **The Audiobook Production Structure**: In printed layouts, marginal sidebars, fables, and authority quotes appear in side columns. However, audiobook narrators read the **entire main body text first**, and narrate all sidebars **at the end of each section/chapter**.
- **The Fix**: Linear/monotonic sliding windows are strictly forbidden. The aligner executes full-chapter sequence clustering against the complete acoustic timeline, finding spoken sentences regardless of visual layout positioning.
- **True Coverage Standard**: Every chapter must hit **$\ge 95\%$ true acoustic audio matching**.

### Pillar II: Zero-Jitter DOM Playback Engine (`html_builder.py`)
- **Sentinel Bookmarking for Unspoken Headings**: Any structural header or unrecorded element receives `data-matched="0"` and a zero-duration sentinel timestamp (`start == end == last_known_end`).
- **Spoken-Only Audio Tracking**: The JavaScript `syncPlayback()` loop strictly queries `.sentence-unit[data-matched="1"]`. Unspoken elements never intercept playback focus, completely eliminating cursor hopping and visual jitter.
- **Dynamic Viewport Centering**: Smooth auto-scroll only triggers when the active sentence leaves the central viewing area (`top < 90px` or `bottom > innerHeight - 90px`).

### Pillar III: Universal End-to-End Automation (`pipeline.py`)
- **Auto-Discovery**: Given any book directory in Obsidian (e.g. `/Range - David Epstein`, `/The 48 Laws of Power - Robert Greene`), the pipeline auto-infers titles, authors, chapter counts, and track files.

---

## 3. Directory File Standards
Each book directory maintains the following standard schema:
```
[Book Directory]/
├── audio_content_profile.json                         # Mode: "complete" | "text_only"
├── chapter_metadata.json                              # Schema v1 track catalog
├── [book_prefix]_ch{00..N}_canonical_sentences.json   # 100% EPUB ground truth
├── [book_prefix]_ch{00..N}_full_analysis.json          # Translation + C1/C2 vocab
├── [book_prefix]_ch{00..N}_aligned_sentences.json      # Word timestamps (or text-only cards)
├── audio/                                             # (Omitted in text_only mode)
│   ├── chapter_{00..N}.mp3                            # Chapter audio track
│   └── [book_prefix]_ch{00..N}_acoustic_words.json   # MLX Whisper word timestamps
└── [Book_Title]_Interactive_Reader.html               # Standalone multi-chapter reader
```

## 4. Release and Reproducibility Contract

The reader is compiled only after a separate release gate passes:
- **Complete Mode (`audio_content_mode: "complete"`)**: Each chapter must achieve $\ge 95\%$ acoustic token coverage across eligible narrated content. Audio tracks and acoustic word stamps are strictly required; missing or estimated timestamps block release.
- **Text-Only Mode (`audio_content_mode: "text_only"`)**: Audio file discovery, acoustic coverage, and monotonic audio timestamps are exempted, but 100% bilingual translation completeness and vocabulary schema validity are strictly enforced. Playback audio controls in the compiled HTML reader are hidden while keeping full typography, card expansion, and keyboard navigation.

Every aligned record must include matched-token count, source-token count, match ratio, alignment method, fallback status, alignment status, and reason. Generated artifacts and manifests are written atomically, and a manifest hash mismatch blocks release.

Gemini owns linguistic analysis and must emit the branch-local JSON contract in `LINGUISTIC_ANALYSIS_PROMPT.md`. Local scripts own extraction, acoustic transcription, alignment, validation, and compilation. Deployment is explicit and validation-gated.

No reusable script may contain a book-specific absolute path. Book-specific exceptions belong in configuration or an isolated adapter. Private books, audiobook files, credentials, and generated copyrighted readers stay outside the public repository.
