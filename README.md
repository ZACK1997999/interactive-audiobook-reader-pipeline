# 📖 Interactive Audiobook Reader Pipeline Workspace

This workspace contains the complete, modular industrial toolchain for transforming any **EPUB book** and **studio audiobook MP3 tracks** into an **Apple Books-grade standalone interactive reader** with:
- **Top-left chapter switcher dropdown**
- **Millisecond-accurate word-by-word karaoke synchronization**
- **Unified tap interaction (point-and-play + dynamic-equivalent translation & C1/C2 vocabulary card)**
- **Triple eye-care themes (Sepia / Light / Dark)**
- **Mobile-friendly collapsible menu drawer**
- **Automatic GitHub Pages deployment**

---

## 🛠️ Toolchain Modules

| Script | Function |
| :--- | :--- |
| [`pipeline.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/pipeline.py) | **Master CLI Orchestrator**: Runs any or all stages of the pipeline in one command. |
| [`extract_epub.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/extract_epub.py) | **EPUB Extractor**: Splits raw XHTML into 100% unabridged atomic sentences with abbreviation protection. |
| [`acoustic_whisper.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/acoustic_whisper.py) | **Acoustic Engine**: Runs `mlx-community/whisper-large-v3-turbo` on Apple Silicon GPU/ANE for word-level timestamps. |
| [`dynamic_aligner.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/dynamic_aligner.py) | **Alignment Engine**: Global `SequenceMatcher` anchoring + buffer padding (`-0.15s / +0.30s`). |
| [`html_builder.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/html_builder.py) | **Static HTML Compiler**: Pre-renders the multi-chapter reader with zero-jitter karaoke tracking. |
| [`deploy_pages.py`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/deploy_pages.py) | **Cloud Sync**: Automatically pushes the compiled reader and audio tracks to GitHub Pages. |
| [`SPECIFICATION.md`](file:///Users/lindy/Vault/My%20Python%20Productivity%20Script%202/interactive_reader_pipeline/SPECIFICATION.md) | **Engineering Standard**: Full architecture, typography rules, CSS variables, and design specs. |

---

## 🚀 How to Run for Future Chapters

### 1-Line AI Instruction (Recommended)
Simply say:
```text
Please process Chapter 3 of Range using our interactive_reader_pipeline.
```

### Manual CLI Execution
```bash
python3 pipeline.py \
  --epub "/path/to/book.epub" \
  --internal-path "OEBPS/xhtml/11_CHAPTER_3_When_Less_o.xhtml" \
  --audio-source "/path/to/006 - Range...mp3" \
  --chapter-num 3 \
  --chapter-title "When Less of the Same Is More"
```
