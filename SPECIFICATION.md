# Industrial Interactive Audiobook Reader Specification & Architecture (v3.0)

## 1. System Overview
The **Interactive Audiobook Reader Pipeline** is a fully automated, Apple Books-grade bilingual reading and listening system. It transforms raw book text (EPUB/Markdown) and unabridged audiobooks (MP3) into synchronized standalone web applications with sub-second karaoke word tracking, collapsible sentence-by-sentence Machiavellian/philosophical translations, and B2+/C1/C2 vocabulary breakdowns.

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
- **Continuous Daemon Watcher (`auto_sync_watcher.py`)**: Continuously monitors local MLX Whisper output on Apple Silicon and automatically recompiles the Master Reader as each chapter completes.

---

## 3. Directory File Standards
Each book directory strictly maintains the following standard schema:
```
[Book Directory]/
├── [book_prefix]_ch{00..N}_canonical_sentences.json   # 100% EPUB ground truth
├── [book_prefix]_ch{00..N}_full_analysis.json          # Machiavellian translation + C1/C2 vocab
├── [book_prefix]_ch{00..N}_aligned_sentences.json      # Word timestamps + audio metadata
├── audio/
│   ├── chapter_{00..N}.mp3                            # Chapter audio track
│   └── [book_prefix]_ch{00..N}_acoustic_words.json   # MLX Whisper word timestamps
└── [Book_Title]_Interactive_Reader.html               # Standalone multi-chapter reader
```
