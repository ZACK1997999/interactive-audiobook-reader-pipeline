import json, os, sys, html
from pathlib import Path
from artifact_io import atomic_write_text

book_dir = Path("/Users/lindy/Vault/MyObsidian/English/Sentence Analysis/Elon Musk - Walter Isaacson")
output_html_path = Path("/Users/lindy/Vault/Audible/books/elon-musk/index.html")

with open(book_dir / "raw_intake_mapping.json", encoding="utf-8") as f:
    mapping = json.load(f)

loaded_chapters = []
for entry in mapping["entries"]:
    ch = entry["chapter"]
    aligned_file = book_dir / f"elon_musk_ch{ch:02d}_aligned_sentences.json"
    if aligned_file.is_file():
        with open(aligned_file, "r", encoding="utf-8") as af:
            sents = json.load(af)
        audio_src = entry["audio_source"]
        loaded_chapters.append({
            "num": ch,
            "title": entry.get("title", f"Chapter {ch}"),
            "audio": f"./audio/{audio_src}",
            "sentences": sents
        })

print(f"Loaded {len(loaded_chapters)} ready chapters for Audible web deployment.")

book_title = "Elon Musk"
book_subtitle = "Bilingual Interactive Reader"
book_author = "Walter Isaacson"
book_id = "elon-musk"
first_ch_audio = loaded_chapters[0]["audio"] if loaded_chapters else "./audio/003 - Elon Musk.mp3"

with open("html_builder.py", "r", encoding="utf-8") as hbf:
    hb_code = hbf.read()

raw_css = hb_code[hb_code.find("<style>"):hb_code.find("</style>") + 8]
clean_css = raw_css.replace("{{", "{").replace("}}", "}")

lib_btn_css = """
.lib-back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  font-family: var(--font-sans);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-sub);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}
.lib-back-btn:hover {
  background: var(--bg-hover);
  color: var(--accent);
  border-color: var(--border);
}
"""
clean_css = clean_css.replace("</style>", lib_btn_css + "\n</style>")

nav_items = ""
for ch in loaded_chapters:
    cnum = ch["num"]
    ctitle = ch["title"]
    label = "Preface" if cnum == 0 else f"Chapter {cnum}"
    active_cls = " active" if cnum == 0 else ""
    nav_items += f"""        <div class="chapter-item{active_cls}" id="menu-ch-{cnum}" onclick="switchChapter({cnum})">
          <span class="chapter-item-tag">{label}</span>
          <span>{html.escape(ctitle)}</span>
        </div>\n"""

chapters_html = ""
for ch in loaded_chapters:
    cnum = ch["num"]
    ctitle = ch["title"]
    caudio = ch["audio"]
    csents = ch["sentences"]
    active_cls = " active" if cnum == 0 else ""
    ch_heading_label = "PREFACE" if cnum == 0 else f"CHAPTER {cnum}"
    
    chapters_html += f"""
  <!-- CHAPTER {cnum} -->
  <section class="chapter-section{active_cls}" id="chapter-{cnum}" data-audio="{caudio}" data-ch="{cnum}">
    <header class="book-header">
      <div class="book-subtitle">{html.escape(book_subtitle)}</div>
      <h1 class="book-title">{ch_heading_label}<br>{html.escape(ctitle)}</h1>
      <div class="book-author">{html.escape(book_author)}</div>
    </header>

    <div class="book-content">
"""
    for s in csents:
        raw_sid = s["id"]
        sid = f"c{cnum}-{raw_sid}"
        is_h = s.get("is_heading", False)
        start = s.get("start", 0.0)
        end = s.get("end", 0.0)
        has_match = 1 if s.get("has_audio_match", True) and (end > start) else 0
        trans = html.escape(s.get("trans", ""))
        vocab = s.get("vocab", [])
        
        word_spans = s.get("word_spans", [])
        word_html_list = []
        if word_spans:
            for w in word_spans:
                rw = html.escape(w["word"])
                ws = w["start"]
                we = w["end"]
                word_html_list.append(f"<span class=\"w\" data-s=\"{ws}\" data-e=\"{we}\">{rw}</span>")
        else:
            for rw in s["text"].split():
                word_html_list.append(f"<span class=\"w\" data-s=\"{start}\" data-e=\"{end}\">{html.escape(rw)}</span>")
        
        sentence_text_html = " ".join(word_html_list)
        
        vocab_html_list = []
        for v in vocab:
            vw = html.escape(v.get("word", ""))
            vp = html.escape(v.get("pos", ""))
            vd = html.escape(v.get("def", ""))
            vocab_html_list.append(f"<div class=\"vocab-row\"><span class=\"v-word\">{vw}</span><span class=\"v-pos\">{vp}</span><span class=\"v-def\">{vd}</span></div>")
            
        joined_vocab = "".join(vocab_html_list)
        vocab_section = f"<div class=\"inspect-vocab-list\">{joined_vocab}</div>" if vocab_html_list else ""
        h_class = " chapter-heading-1" if is_h else ""
        chapters_html += f"""
      <div class="sentence-unit" id="{sid}" data-start="{start}" data-end="{end}" data-matched="{has_match}">
        <div class="sentence-text{h_class}" onclick="handleSentenceClick(event, '{sid}', {start}, {end}, {has_match})">
          <span class="s-content">{sentence_text_html}</span>
        </div>
        <div class="inspect-panel" onclick="handleInspectPanelClick(event, '{sid}')" title="Click to collapse / 点击折叠">
          <div class="inspect-trans">{trans}</div>
          {vocab_section}
        </div>
      </div>
"""
    chapters_html += """    </div>
  </section>
"""

js_orig = hb_code[hb_code.find("const audio = document.getElementById('audioTrack');"):hb_code.find("</script>\n</body>\n</html>")]

cdn_helper_js = """
window.AUDIBLE_BOOK_ID = "elon-musk";
window.AUDIO_CDN_DEFAULT = "https://pub-97d9c951fe28402ba8ba05ac4e05afb9.r2.dev";

function resolveAudioUrl(relPath) {
  if (!relPath) return "";
  const isLocal = window.location.protocol === "file:" || window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  if (!isLocal || new URLSearchParams(window.location.search).has("force_cdn")) {
    const cdnBase = window.AUDIO_CDN_BASE || new URLSearchParams(window.location.search).get("cdn") || localStorage.getItem("audible_cdn_base") || window.AUDIO_CDN_DEFAULT;
    if (cdnBase) {
      const filename = relPath.split("/").pop();
      return cdnBase.replace(/\/$/, "") + "/" + window.AUDIBLE_BOOK_ID + "/" + filename;
    }
  }
  return relPath;
}

function reportLibraryProgress(chNum, pct) {
  try {
    const progressKey = "audible_progress_" + window.AUDIBLE_BOOK_ID;
    localStorage.setItem(progressKey, JSON.stringify({
      chapter: chNum,
      percent: Math.round(pct || 0),
      updatedAt: new Date().toISOString()
    }));
    localStorage.setItem("audible_last_active_book", window.AUDIBLE_BOOK_ID);
  } catch(e) {}
}
"""

js_patched = js_orig.replace("audio.src = audioSrc;", "audio.src = resolveAudioUrl(audioSrc); reportLibraryProgress(chNum, 0);")

final_html = f"""<!DOCTYPE html>
<html lang="en" data-theme="sepia">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{html.escape(book_title)}: {html.escape(book_subtitle)}</title>
{clean_css}
</head>
<body onclick="closeDropdowns(event)">

<header class="top-nav">
  <div class="nav-bar">
    <div class="chapter-nav-wrapper" style="display: flex; align-items: center; gap: 8px;">
      <a href="../../index.html" class="lib-back-btn" title="Back to Bookshelf">🏛️ Library</a>
      <button class="chapter-btn" id="chapterSelectBtn" onclick="toggleChapterDropdown(event)">
        <span>📖 {html.escape(book_title)} · <span id="currentChapterLabel">Ch. 0</span></span>
        <span class="dropdown-arrow">▾</span>
      </button>
      <div class="chapter-dropdown" id="chapterDropdown">
{nav_items}      </div>
    </div>
    
    <div class="nav-actions">
      <button class="icon-btn primary" id="globalPlayBtn" onclick="toggleGlobalPlay()">▶ Play</button>
      <button class="icon-btn" id="drawerToggleBtn" onclick="toggleDrawer()">⚙️ Menu</button>
    </div>
  </div>
  
  <div class="control-drawer" id="controlDrawer">
    <div class="drawer-inner">
      <audio id="audioTrack" controls preload="metadata" src="{first_ch_audio}"></audio>
      <div class="drawer-row">
        <div class="drawer-group">
          <button class="icon-btn" onclick="adjustFontSize(-1)">A-</button>
          <button class="icon-btn" onclick="adjustFontSize(1)">A+</button>
          <button class="icon-btn" onclick="toggleTheme()">Theme</button>
          <button class="icon-btn" id="tipsToggleBtn" onclick="toggleTips()">Tips</button>
        </div>
        <div class="drawer-group">
          <label style="font-family: var(--font-sans); font-size: 0.82rem; display: flex; align-items: center; gap: 4px; color: var(--text-sub);">
            <input type="checkbox" id="autoScrollCheck" checked onchange="toggleAutoScroll(this.checked)"> Auto-scroll
          </label>
        </div>
      </div>
      <input type="text" id="searchInput" class="search-input" placeholder="Search in active chapter..." oninput="handleSearch()">
      <div class="drawer-tips" id="drawerTips">
        <div class="tips-grid">
          <div class="tips-item"><span class="tips-key">Tap English</span> Replay sentence & show breakdown</div>
          <div class="tips-item"><span class="tips-key">Tap Chinese</span> Collapse card</div>
          <div class="tips-item"><span class="tips-key">Spacebar</span> Toggle translation & vocabulary</div>
          <div class="tips-item"><span class="tips-key">← / ↑</span> Jump to previous sentence</div>
          <div class="tips-item"><span class="tips-key">→ / ↓</span> Jump to next sentence</div>
        </div>
      </div>
    </div>
  </div>
</header>

<main class="container">
{chapters_html}
</main>

<script>
window.__BOOK_ID__ = {json.dumps(book_id)};
const STORAGE_PREFIX = "reader_" + (window.__BOOK_ID__ || "default") + "_";
{cdn_helper_js}
{js_patched}
</script>
</body>
</html>
"""

atomic_write_text(output_html_path, final_html)
print(f"Successfully generated Audible web reader -> {output_html_path} ({output_html_path.stat().st_size / 1024 / 1024:.2f} MB)")
