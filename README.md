# Interactive Audiobook Reader Pipeline

**The Apple Books-grade Interactive Bilingual Reader & Audiobook Engine, built specifically for macOS & Apple Silicon.**

[![macOS](https://img.shields.io/badge/platform-macOS%2013%2B-black.svg?style=flat-square&logo=apple)](https://apple.com)
[![Apple Silicon](https://img.shields.io/badge/hardware-Apple%20Silicon%20(M1/M2/M3/M4)-orange.svg?style=flat-square)](https://apple.com)
[![Acoustics](https://img.shields.io/badge/acoustics-Apple%20MLX%20Whisper-blue.svg?style=flat-square)](https://github.com/ml-explore/mlx)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

---

A deterministic, industrial-strength pipeline for converting any EPUB book into a standalone, zero-dependency bilingual reading experience with Apple Books typography, word-level acoustic synchronization, bilingual contextual breakdown, and cryptographic release verification.

---

## Why macOS & Apple Silicon?

- **Zero-Dependency Core**: Pure text interactive readers require **zero external dependencies** — running entirely on the native Python 3.9+ standard library.
- **Apple Silicon Unified Memory Acceleration**: Speech-to-text forced alignment uses Apple's official `mlx-whisper`, executing on the Mac's Neural Engine and GPU without bloated CUDA drivers or cloud API fees.
- **Apple Books-Grade Aesthetics**: Features responsive New York/San Francisco serif typography, instant word-by-word highlight, 44px Apple HIG touch targets, and fluid Sepia/Light/Dark themes.
- **Native macOS Workflow**: Automatic Safari browser launch (`open`) upon compilation completion, with instant delivery copy via `pbcopy`.

---

## Quickstart (30 Seconds on Mac)

Clone the repository and build the included public-domain demo (*Sun Tzu's The Art of War*) in 5 seconds:

```bash
# 1. Clone the repository
git clone https://github.com/ZACK1997999/interactive-audiobook-reader-pipeline.git
cd interactive-audiobook-reader-pipeline

# 2. Build the interactive bilingual reader (Zero external dependencies needed)
python3 universal_runner.py demo/sample.epub --text-only
```

Your default browser (Safari) will automatically open displaying the completed standalone interactive reader.

---

## Dual-Mode Operation

### 1. Pure Text Interactive Reader (`text_only`)
Ideal for books without audiobooks. Generates complete chapter-by-chapter bilingual readers with sentence click-to-translate, interactive vocabulary popups, and keyboard navigation.

```bash
# Basic run with auto-detected output directory:
python3 universal_runner.py /path/to/book.epub --text-only

# High-throughput parallel translation (e.g. 8 workers):
python3 universal_runner.py /path/to/book.epub --text-only --concurrency 8 --book-dir ./my_book
```

### 2. Immersive Studio Audiobook (`complete`)
Combines EPUB text with professional narrator audio tracks (`.mp3`), performing word-by-word forced alignment via Apple Silicon MLX Whisper.

```bash
# Install Apple Silicon MLX acoustic support:
pip install -e '.[acoustic]'

# Build complete audiobook reader:
python3 universal_runner.py --epub /path/to/book.epub --audio-dir /path/to/mp3s --book-dir ./my_book
```

---

## CLI Installation

Install into your local Python environment to use the `reader-build` command anywhere on your Mac:

```bash
# Standard setup (Text-only readers)
pip install -e .

# Full setup (Apple Silicon MLX acoustic engine + publication tools)
pip install -e '.[acoustic,deployment]'
```

Once installed, simply run:

```bash
reader-build /path/to/book.epub --text-only
```

---

## Project Structure

```text
├── universal_runner.py           # Primary CLI entrypoint (reader-build)
├── extract_epub.py               # Clean EPUB sentence boundary extractor
├── dynamic_aligner.py            # High-precision word-level acoustic aligner
├── html_builder.py               # Apple Books-grade standalone HTML compiler
├── content_profile.py            # Mode router (text_only vs complete audio)
├── quality_gate.py               # Cryptographic release gate & smoke tester
├── validate_outputs.py           # Invariant validator for publication
├── acoustic_whisper.py           # Apple Silicon MLX Whisper extractor
├── demo/
│   └── sample.epub               # Minimal 5KB public-domain demo EPUB
├── examples/
│   └── book-runners/             # Historical book-specific pipeline runners
├── docs/
│   └── history/                  # Archive of milestone specs and benchmarks
├── requirements.txt              # Standard macOS pip requirements
├── setup.py                      # Package configuration & console scripts
└── LICENSE                       # MIT License
```

---

## Quality Verification

Run the comprehensive unit and integration test matrix:

```bash
python3 -m unittest discover
```

---

## License

This project is licensed under the [MIT License](LICENSE).
