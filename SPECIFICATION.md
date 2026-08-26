# Interactive Audiobook Reader Pipeline Specification

## 1. Overview & Vision
This pipeline turns any standard **EPUB electronic book** and **studio audiobook MP3 track** into a **single-file Apple Books-grade interactive web application**:
- **Editorial Typography**: Classic serif font stack (`Charter`, `Iowan Old Style`, `Palatino`, `Georgia`), 740px reading width, 1.88 line-height.
- **Pure Text Immersion (Zero-Icon)**: 100% printed book aesthetics with no trailing buttons or widow lines.
- **Top-Left Chapter Switcher Dropdown (`📖 Book Title · Ch. 1 ▾`)**: Smooth instant chapter swapping with automatic audio track binding and zero page reloads.
- **Unified Replay & Collapse Interaction**:
  - **Tap English Sentence**: Jumps studio audio to that exact moment, plays/re-plays the sentence from the beginning, and opens/keeps open the translation & C1/C2 vocabulary card.
  - **Tap Chinese Card**: Clicking anywhere on the Chinese inspection card smoothly collapses/folds it without interrupting audio playback. Selecting/copying text inside the card is preserved without accidental collapsing.
- **Word-by-Word Active Karaoke Sync**: Spoken words illuminate with constant `font-weight` (zero layout shift/jitter).
- **Collapsible Control Drawer (`⚙️ Menu`)**: Houses font scaling (`A-` / `A+`), theme switcher (Sepia / Light / Dark), auto-scroll toggle, and real-time full-text search.
- **Zero Markdown Bloat**: Keeps the Obsidian vault clean by generating only standalone HTML readers and structured JSON data.
- **Automatic GitHub Pages Deployment**: Direct sync to mobile web readers (`Vault/Audible`).

---

## 2. 6-Stage Industrial Pipeline Architecture

```
[Source EPUB Book + Studio MP3 Audio Track]
                   │
                   ▼
 1. Canonical EPUB Extraction ────────► extract_epub.py
    • 100% unabridged atomic sentences (1-sentence-1-card)
    • Protected abbreviations (Dr., U.S., a.m., etc.) & parentheticals
                   │
                   ▼
 2. Apple Silicon MLX Whisper ────────► acoustic_whisper.py
    • `mlx-community/whisper-large-v3-turbo` on Mac GPU/ANE
    • Global word-level timestamps (e.g. 5,000+ words in ~3 min)
                   │
                   ▼
 3. Global Dynamic Alignment ─────────► dynamic_aligner.py
    • `difflib.SequenceMatcher` anchoring across entire chapters
    • Anti-clipping acoustic padding (-0.15s start / +0.30s end)
                   │
                   ▼
 4. B2+/C1/C2 Linguistic Analysis ────► LLM Micro-Chunking (2,000-3,000 words/batch)
    • Filter elementary A1-B1 words; extract context C1/C2 collocations
    • Dynamic-equivalent, literary Chinese translations (Zero-label format)
                   │
                   ▼
 5. Master Multi-Chapter Compilation ─► html_builder.py
    • Static single-file HTML pre-rendering
    • Top-left dropdown switcher + zero-jitter word karaoke tracking
                   │
                   ▼
 6. Clean Storage & Cloud Deployment ─► deploy_pages.py
    • Git checkpoint in Obsidian Vault
    • Synchronize & push to `Vault/Audible` for instant iPhone/Mac mobile access
```

---

## 3. Directory Layout Standard

```text
/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/<Book_Title>/
├── audio/
│   ├── chapter_01.mp3
│   ├── chapter_02.mp3
│   ├── range_ch01_acoustic_words.json
│   └── range_ch02_acoustic_words.json
├── range_ch01_canonical_sentences.json
├── range_ch01_full_analysis.json
├── range_ch01_aligned_sentences.json
├── range_ch02_canonical_sentences.json
├── range_ch02_full_analysis.json
├── range_ch02_aligned_sentences.json
└── <Book_Title>_Interactive_Reader.html   <-- Unified Master Multi-Chapter Reader
```

---

## 4. UI/UX & Typography Standards

### Theme Palettes
- **📜 Sepia (`[data-theme="sepia"]`)**:
  - Background: `#fbf7ee` | Panel: `#f2ece0` | Accent: `#8b4513`
  - Spoken Word Highlight: Background `#fde047`, Text `#78350f`
- **☀️ Light (`[data-theme="light"]`)**:
  - Background: `#ffffff` | Panel: `#f8f9fa` | Accent: `#1e3a8a`
  - Spoken Word Highlight: Background `#bfdbfe`, Text `#1e3a8a`
- **🌙 Dark (`[data-theme="dark"]`)**:
  - Background: `#12151c` | Panel: `#1b202c` | Accent: `#60a5fa`
  - Spoken Word Highlight: Background `#2563eb`, Text `#ffffff`

### Zero-Jitter Typography Rule
- **Rule**: When highlighting the active spoken word, only change `background-color` and `color`.
- **Prohibition**: **NEVER dynamically modify `font-weight: 700` or letter dimensions** during playback. Changing font weight expands character pixel widths and triggers line-wrap reflows / visual jitter.
