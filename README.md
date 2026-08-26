# 📖 Interactive Audiobook Reader Pipeline Workspace

This workspace contains the complete, modular industrial toolchain for transforming any **EPUB book** and **studio audiobook MP3 tracks** into an **Apple Books-grade standalone interactive reader** with:
- **Top-left chapter switcher dropdown**
- **Evidence-gated word-by-word karaoke synchronization**
- **Unified tap interaction (point-and-play + dynamic-equivalent translation & C1/C2 vocabulary card)**
- **Triple eye-care themes (Sepia / Light / Dark)**
- **Mobile-friendly collapsible menu drawer**
- **Explicit, validation-gated GitHub Pages deployment**

---

## 🛠️ Toolchain Modules

| Script | Function |
| :--- | :--- |
| [`pipeline.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/pipeline.py) | **Master CLI Orchestrator**: Runs any or all stages of the pipeline in one command. |
| [`extract_epub.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/extract_epub.py) | **EPUB Extractor**: Splits raw XHTML into 100% unabridged atomic sentences with abbreviation protection. |
| [`acoustic_whisper.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/acoustic_whisper.py) | **Acoustic Engine**: Runs `mlx-community/whisper-large-v3-turbo` on Apple Silicon GPU/ANE for word-level timestamps. |
| [`dynamic_aligner.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/dynamic_aligner.py) | **Alignment Engine**: Global `SequenceMatcher` anchoring + buffer padding (`-0.15s / +0.30s`). |
| [`html_builder.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/html_builder.py) | **Static HTML Compiler**: Pre-renders the multi-chapter reader with zero-jitter karaoke tracking. |
| [`validate_outputs.py`](validate_outputs.py) | **Release Gate**: Blocks release for missing, weak, or inconsistent data. |
| [`LINGUISTIC_ANALYSIS_PROMPT.md`](LINGUISTIC_ANALYSIS_PROMPT.md) | **Gemini contract**: Context-first language analysis using the existing JSON schema. |
| [`REPRODUCE.md`](REPRODUCE.md) | **Reproduction guide**: Setup, contracts, privacy boundary, and handoff. |
| [`config.example.json`](config.example.json) | **Configuration template**: Book metadata and private input locations. |
| [`LEGACY_EXPERIMENTS.md`](LEGACY_EXPERIMENTS.md) | **Boundary**: Identifies historical book-specific scripts that are not the supported release path. |
| [`archive/legacy-experiments/`](archive/legacy-experiments/) | **Archive**: Historical book-specific and hardcoded helpers retained for reference only. |
| [`SPECIFICATION.md`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/SPECIFICATION.md) | **Engineering Standard**: Full architecture, typography rules, CSS variables, and design specs. |
| [`pyproject.toml`](pyproject.toml) | **Installable package metadata**: Installs the reusable CLI entry points. |

---

## 🚀 How to Run for Future Chapters

### Install the reusable workflow

```bash
python3 -m pip install -e .
```

For Apple Silicon acoustic extraction:

```bash
python3 -m pip install -e '.[acoustic]'
```

This installs `reader-pipeline` and `reader-validate`. Deployment is never part of the normal processing command.

### 1-Line AI Instruction (Recommended)
Simply say:
```text
Please process this book using the current branch workflow. Read README.md, SPECIFICATION.md, and LINGUISTIC_ANALYSIS_PROMPT.md first. Gemini handles linguistic analysis; local scripts handle extraction, acoustic alignment, validation, and HTML compilation.
```

### Manual CLI Execution

The supported release command expects a prepared book directory. Its layout is documented in
[`REPRODUCE.md`](REPRODUCE.md); in particular, the directory contains canonical sentence JSON,
Gemini analysis JSON, and an `audio/` directory with chapter tracks.

```bash
reader-pipeline --book-dir "/path/to/book-directory" --title "Book Title" --author "Author"
```

The command aligns only ready chapter pairs, runs the release validator, and compiles the reader
only when validation passes. A blocked validation exits non-zero. Use `reader-validate` to inspect
the same gate without compiling HTML. Deployment remains a separate, explicit operation.
