# Interactive Audiobook Reader Pipeline

A deterministic, industrial toolchain for transforming EPUB chapters and audiobook audio into an Apple Books-grade standalone interactive reading experience with word-level forced alignment, bilingual vocabulary breakdown, and zero-dependency publication.

---

## Key Capabilities

- **Evidence-Gated Alignment**: Word-by-word timestamp synchronization powered by MLX Whisper and dynamic monotonic alignment.
- **Apple Books Typography**: Responsive serif layouts with dark, sepia, and light reading themes.
- **Intuitive Touch & Keyboard Navigation**: Tap sentence for point-and-play and sentence breakdown; double-tap for a 3x sentence repeat loop; `Space` for card toggle; `R` for repeat loop.
- **O(log N) Binary Synchronization**: Sub-millisecond frame synchronization with automatic requestAnimationFrame throttling when paused or backgrounded.
- **Hardware-Accelerated Audio**: Native pitch-preserving variable speed playback (`preservesPitch`) and seamless Cloudflare R2 CDN streaming.
- **Deterministic Quality Gates**: Release gate enforces 95% acoustic coverage, translation completeness, and SHA-256 cryptographic authorization tokens.

---

## Toolchain Architecture

| Module | Responsibility |
| :--- | :--- |
| [`intake_reconciler.py`](intake_reconciler.py) | **Intake & Reconciler**: Parses EPUB structure, matches acoustic anchors, and enforces hash-bound approval. |
| [`industrial_orchestrator.py`](industrial_orchestrator.py) | **Industrial Orchestrator**: Manages micro-batch processing, GPU memory limits, and atomic resumption state. |
| [`extract_epub.py`](extract_epub.py) | **EPUB Extractor**: Extracts unabridged text and normalizes sentence boundaries without dropping punctuation. |
| [`pipeline.py`](pipeline.py) | **Alignment Engine**: Runs MLX Whisper acoustic forced alignment and generates synchronized time indices. |
| [`quality_gate.py`](quality_gate.py) | **Quality Gate**: Validates monotonic timestamps, acoustic coverage thresholds, and translation integrity. |
| [`html_builder.py`](html_builder.py) | **Reader 2.0 Compiler**: Emits standalone, zero-dependency interactive HTML readers. |
| [`publisher.py`](publisher.py) | **Auto-Publisher**: Orchestrates Cloudflare R2 upload with SHA-256 caching, shelf manifest updates, and verification. |
| [`local_publisher.py`](local_publisher.py) | **Offline Publisher**: Packages standalone offline readers without cloud infrastructure dependencies. |

---

## Installation

### Standard Setup

```bash
python3 -m pip install -e .
```

### Apple Silicon Hardware-Accelerated Acoustic Engine

```bash
python3 -m pip install -e '.[acoustic]'
```

### Deployment & Cloudflare R2 Publisher Support

```bash
python3 -m pip install -e '.[deployment]'
```

---

## Quickstart

### 1. Zero-Touch Intake & Verification

Generate acoustic probes and compute the deterministic intake plan:

```bash
reader-intake --epub /path/to/book.epub --audio-dir /path/to/audio \
  --probes /path/to/probes.json --output /path/to/intake_plan.json
reader-intake --approve /path/to/intake_plan.json
reader-intake --verify /path/to/intake_plan.json
```

### 2. Run Industrial Alignment

Execute unattended chapter processing with automatic checkpoint resumption:

```bash
python3 industrial_orchestrator.py \
  --book-dir /path/to/output_dir \
  --linguistic-command 'python3 agy_linguistic_worker.py' \
  --acoustic-command 'python3 mlx_acoustic_worker.py'
```

### 3. Automated Publishing & Shelf Registration

Run the deployment preflight before any expensive processing or publication:

```bash
python3 deployment_preflight.py --config /path/to/publisher_config.json
```

The preflight is fail-closed. It checks the actual portal repository, deployment
entrypoint, branch, required release inputs, and reports when repository visibility
must be checked in GitHub/Cloudflare. It does not upload, push, or publish anything.

Publish aligned readers through the single release entry point:

```bash
reader-release /path/to/publisher_config.json --dry-run
reader-release /path/to/publisher_config.json
```

See [`publisher_config.example.json`](publisher_config.example.json) for the configuration schema.

The example is not a live configuration. Create a local, ignored
`publisher_config.json` for each deployment target. Keep credentials in the
environment or a secret manager. This project deliberately does not infer the
public portal from the current code repository: in the existing setup, the reader
pipeline repository and `/Users/lindy/Vault/Audible` portal repository are separate
systems. A private portal repository can therefore affect Pages/Cloudflare builds
even when local release validation passes.

For the legacy chunked portal, the safe order is:

```text
quality gate -> semantic gate -> HTML smoke check -> deployment preflight
-> portal build/chunk -> portal repository status/branch check -> explicit push
-> public URL and audio range verification
```

`reader-publish` remains available as a lower-level compatibility command, but it
must not be called directly for a production release. Never run the legacy
all-books script as an implicit post-processing step. Select one book, one source
HTML, one portal branch, and record the resulting commit and public URL in the
release journal.

---

## Verification & Testing

The test suite validates data invariants, CSS zero-jitter rules, failure recovery, and acoustic alignment:

```bash
python3 -m unittest discover
```

Continuous integration runs across Python 3.9, 3.11, and 3.13.

---

## Standards & Specifications

- [`SPECIFICATION.md`](SPECIFICATION.md): Typography, CSS variable contract, DOM tree schema, and client runtime architecture.
- [`QUALITY_STANDARD.md`](QUALITY_STANDARD.md): Quality gate rules, acoustic coverage thresholds, and anomaly detection.
- [`REPRODUCE.md`](REPRODUCE.md): End-to-end environment reproduction guide.
