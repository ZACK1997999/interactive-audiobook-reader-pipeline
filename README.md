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
| [`intake_reconciler.py`](intake_reconciler.py) | **P2 Intake Contract**: Parses EPUB structure, reconciles acoustic anchors, and enforces hash-bound human approval. |
| [`publisher.py`](publisher.py) | **P2 Publication Protocol**: Resumes journaled archive/R2/Git/HTTP verification without duplicate work. |
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
Every generated JSON, manifest, validation report, and HTML file is written atomically. The
pipeline records hashes for every available canonical, analysis, acoustic, and audio input in
`reader_run_manifest.json`; if a recorded input changes, the affected chapter is realigned
instead of silently reusing its previous alignment. It refuses to compile when any required
analysis, alignment, review, or 95% chapter-level acoustic coverage gate fails.

The pipeline records `compiled` after local HTML generation. It does not claim that the reader
was uploaded or externally verified; publication and external audio checks remain separate,
explicit operations.

Each book run also takes an exclusive lock so two pipeline processes cannot mutate the same
artifacts concurrently. The written acceptance criteria are in
[`QUALITY_STANDARD.md`](QUALITY_STANDARD.md). An explicit `audio_manifest.json` is created on
the first successful discovery and becomes authoritative thereafter; changed or missing audio
sources block the run.

### Durable Coordinator for Unattended Runs

Use [`industrial_orchestrator.py`](industrial_orchestrator.py) as the durable coordinator for
overnight processing. It persists stage state, chapter attempts, input/output hashes, and failure
reasons. Language and acoustic models are injected as workers through the `READER_*` environment
contract; the coordinator never invents analysis or acoustic artifacts.

Start with a safe dry-run:

```bash
python3 industrial_orchestrator.py \
  --book-dir /path/to/private/book-output \
  --state /path/to/private/book-output/industrial_run_state.json \
  --dry-run
```

Then provide separately reviewed linguistic and acoustic worker commands. A worker reads
`READER_CANONICAL_PATH`/`READER_AUDIO_PATH` and writes the contract file at `READER_OUTPUT_PATH`.
Failed workers are retried up to `--max-attempts`; publication is not a coordinator stage.

Before any configured worker may run, P2 requires an approved `intake_plan.json`. Generate the
cheap head/tail acoustic probes with the selected acoustic backend, then build and review the
plan:

```bash
reader-intake --epub /path/book.epub --audio-dir /path/audio \
  --probes /path/acoustic_probes.json --output /path/book/intake_plan.json
reader-intake --approve /path/book/intake_plan.json
reader-intake --verify /path/book/intake_plan.json
```

Approval is bound to the complete plan plus the SHA-256 of the EPUB and every audio source.
Changing any input closes the gate. Plans below the configured confidence threshold cannot be
approved. The repository includes the default worker adapters:

```bash
python3 industrial_orchestrator.py \
  --book-dir /path/to/private/book-output \
  --linguistic-command 'python3 agy_linguistic_worker.py' \
  --acoustic-command 'python3 mlx_acoustic_worker.py'
```

These adapters fail closed when `agy` or MLX cannot start, so a missing model, authentication
failure, or hardware problem becomes a resumable blocker instead of a fabricated artifact.

### P2 Reader and Publication

`html_builder.py` now emits one dual-mode reader: `file://` uses the local audio path while HTTP
uses the chapter's public CDN path. Sentence synchronization uses a per-chapter binary-search
index and suspends animation frames while paused or hidden. Native pitch-preserving speed,
sentence shadowing (`R`), and UTF-8 Anki TSV export are built into that same compiler.

Install publication support and run the reviewed JSON configuration:

```bash
python3 -m pip install -e '.[deployment]'
reader-publish /path/publisher_config.json
```

Start from [`publisher_config.example.json`](publisher_config.example.json). The publisher derives
`chaptersCount`, `totalDuration`, the cover path, and the reader path from the compiled reader and
approved intake/audio evidence, so shelf registration does not duplicate those computed fields.

The publisher records `preflight -> archive -> r2_upload -> remote_verify -> git_stage ->
git_push -> smoke_test` in `publisher_journal.json`. R2 objects are skipped only when their
stored SHA-256 metadata matches. Every public audio object must return exact HTTP 206 ranges at
its beginning, middle, and end before the publisher creates a whitelisted Git commit. The portal
must load `manifest.json` as its single data source; a remaining `INLINE_MANIFEST` blocks
preflight.

### 1-Line AI Instruction (Recommended)
Simply say:
```text
Please process this book using the current branch workflow. Read README.md, SPECIFICATION.md, and LINGUISTIC_ANALYSIS_PROMPT.md first. Agy handles linguistic analysis; local scripts handle extraction, acoustic alignment, validation, and HTML compilation.
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
