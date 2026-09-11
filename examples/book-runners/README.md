# Historical Book-Specific Pipeline Runners

This directory contains standalone runners used during initial development and calibration for specific book releases:

- `fourth_wing_industrial_runner.py`: End-to-end alignment and reader generation for Fourth Wing.
- `denationalization_runner.py`: End-to-end dual-mode runner for Hayek Denationalisation of Money.

## Universal Standard Alternative

For all new books (both pure-text readers and full audiobooks), use the unified command-line tool `reader-build` (powered by `universal_runner.py`):

```bash
# Pure-text interactive reader:
reader-build /path/to/book.epub --text-only

# Immersive audiobook reader:
reader-build --epub /path/to/book.epub --audio-dir /path/to/audio --book-dir /path/to/output
```
