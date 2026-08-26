# 📖 Interactive Audiobook Reader Pipeline Workspace

This workspace contains a reusable toolchain for turning prepared chapter artifacts from an **EPUB**, linguistic analysis, and audiobook timestamps into an **Apple Books-grade standalone interactive reader** with:
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
| [`pipeline.py`](pipeline.py) | **Release Orchestrator**: Aligns, validates, and compiles prepared chapter artifacts. |
| [`extract_epub.py`](extract_epub.py) | **EPUB Extractor**: Splits raw XHTML into unabridged atomic sentences. |
| [`acoustic_whisper.py`](acoustic_whisper.py) | **Acoustic Engine**: Runs MLX Whisper for word-level timestamps. |
| [`dynamic_aligner.py`](dynamic_aligner.py) | **Alignment Engine**: Global matching with evidence-bearing word spans. |
| [`html_builder.py`](html_builder.py) | **Static HTML Compiler**: Builds the multi-chapter interactive reader. |
| [`audio_resolver.py`](audio_resolver.py) | **Audio Contract**: Resolves exactly one explicit chapter audio candidate. |
| [`models.py`](models.py) | **Stable Internal Contracts**: Backend-neutral domain models introduced in Phase 1. |
| [`contract_adapters.py`](contract_adapters.py) | **Compatibility Adapters**: Converts current JSON artifacts to and from internal models. |
| [`alignment_backend.py`](alignment_backend.py) | **Alignment Boundary**: Exposes the current aligner behind a replaceable backend interface. |
| [`chapter_locator.py`](chapter_locator.py) | **Chapter Locator**: Fuzzy, evidence-bearing chapter-start discovery. |
| [`acoustic_backend.py`](acoustic_backend.py) | **Acoustic Boundary**: Replaceable MLX/WhisperX-compatible interface. |
| [`whisperx_backend.py`](whisperx_backend.py) | **Optional WhisperX Backend**: Forced-alignment timestamps without affecting the default MLX install. |
| [`CONTRACTS.md`](CONTRACTS.md) | **Contract Reference**: Object responsibilities and compatibility boundary. |
| [`PHASE_0_BASELINE.md`](PHASE_0_BASELINE.md) | **Refactor Baseline**: Starting commit and scope of the synthetic contract fixtures. |
| [`validate_outputs.py`](validate_outputs.py) | **Release Gate**: Blocks release for missing, weak, or inconsistent data. |
| [`LINGUISTIC_ANALYSIS_PROMPT.md`](LINGUISTIC_ANALYSIS_PROMPT.md) | **Gemini contract**: Context-first language analysis using the existing JSON schema. |
| [`REPRODUCE.md`](REPRODUCE.md) | **Reproduction guide**: Setup, contracts, privacy boundary, and handoff. |
| [`config.example.json`](config.example.json) | **Configuration template**: Book metadata and private input locations. |
| [`LEGACY_EXPERIMENTS.md`](LEGACY_EXPERIMENTS.md) | **Boundary**: Identifies historical book-specific scripts that are not the supported release path. |
| [`archive/legacy-experiments/`](archive/legacy-experiments/) | **Archive**: Historical book-specific and hardcoded helpers retained for reference only. |
| [`SPECIFICATION.md`](SPECIFICATION.md) | **Engineering Standard**: Full architecture, typography rules, CSS variables, and design specs. |
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

WhisperX is an optional alternative backend:

```bash
python3 -m pip install -e '.[whisperx]'
```

The default workflow remains MLX Whisper. WhisperX is exposed through the same
`AcousticBackend` contract and is tested without downloading a model.

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

The current release command consumes prepared artifacts. The extraction, acoustic, and alignment
backends will be placed behind the stable interfaces in later refactor phases.
