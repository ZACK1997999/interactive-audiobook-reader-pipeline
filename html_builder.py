"""
Module: html_builder.py
Description: Compiles Multi-Chapter Apple Books-grade Interactive Readers with top-left dropdown switcher, zero-jitter word-by-word karaoke tracking, and unified tap inspection.
"""

import json
import html
import os
import re
import sys
from artifact_io import atomic_write_text
from release_token import ReleaseToken, verify_release_token

def build_master_reader(book_title, book_subtitle, book_author, chapters_config, output_html_path,
                        *, release_token: ReleaseToken, release_report_path, book_id=None):
    """
    chapters_config: list of dicts with:
      - 'num': unique internal track number (e.g. 0, 1, 2)
      - 'title': str (e.g. 'The Cult of the Head Start')
      - 'role': optional 'preface', 'introduction', or 'chapter'
      - 'display_number': optional printed chapter number for role='chapter'
      - 'label': optional complete navigation/heading label override
      - 'audio': str (e.g. './audio/chapter_01.mp3')
      - 'aligned_json': str (path to aligned sentences JSON)
    """
    if book_id is None or not str(book_id).strip():
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(book_title).strip().lower()).strip("_")
        book_id = slug or "default"
    else:
        book_id = str(book_id).strip()

    output_html_path = os.path.abspath(output_html_path)
    book_dir = os.path.dirname(output_html_path)
    verify_release_token(release_token, book_dir, release_report_path)
    with open(release_report_path, encoding="utf-8") as report_file:
        report = json.load(report_file)
    authorized = {
        os.path.abspath(os.path.join(book_dir, chapter["aligned"]))
        for chapter in report.get("chapters", []) if chapter.get("aligned")
    }
    requested = {os.path.abspath(c["aligned_json"]) for c in chapters_config}
    if requested != authorized:
        raise RuntimeError("HTML compilation chapter set does not match the validated release report")

    loaded_chapters = []
    for c in chapters_config:
        with open(c['aligned_json'], 'r', encoding='utf-8') as f:
            sents = json.load(f)
        role = c.get('role', 'preface' if c['num'] == 0 else 'chapter')
        display_number = c.get('display_number', c['num'] if role == 'chapter' else None)
        label = c.get('label')
        if not label:
            if role == 'preface':
                label = 'Preface'
            elif role == 'introduction':
                label = 'Introduction'
            elif role == 'chapter' and display_number is not None:
                label = f'Chapter {display_number}'
            else:
                label = c['title']
        loaded_chapters.append({
            'num': c['num'],
            'title': c['title'],
            'role': role,
            'display_number': display_number,
            'label': str(label),
            'audio': c['audio'],
            'public_audio': c.get('public_audio'),
            'sentences': sents
        })
        
    first_ch_audio = loaded_chapters[0]['audio'] if loaded_chapters else "./audio/chapter_00.mp3"
    first_ch_public_audio = loaded_chapters[0].get('public_audio') if loaded_chapters else None
    first_ch_num = loaded_chapters[0]['num'] if loaded_chapters else 0
    
    html_head = f"""<!DOCTYPE html>
<html lang="en" data-theme="sepia">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="reader-release-report-sha256" content="{html.escape(release_token.report_sha256)}">
<title>{html.escape(book_title)}: {html.escape(book_subtitle)}</title>
<style>
:root {{
  --font-serif: "Charter", "Iowan Old Style", "Palatino Linotype", "Georgia", "Source Han Serif SC", "PingFang SC", serif;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-size-base: 1.20rem;
  --line-height-base: 1.88;
  --max-content-width: 740px;
}}

[data-theme="sepia"] {{
  --bg-page: #fbf7ee;
  --bg-panel: #f2ece0;
  --bg-hover: #e8e0d0;
  --text-main: #2d261e;
  --text-sub: #6c5d4b;
  --accent: #8b4513;
  --accent-light: #d4a373;
  --word-highlight-bg: #fde047;
  --word-highlight-text: #78350f;
  --border: #e2d7c5;
  --card-shadow: 0 4px 16px rgba(45, 38, 30, 0.07);
}}

[data-theme="light"] {{
  --bg-page: #ffffff;
  --bg-panel: #f8f9fa;
  --bg-hover: #eaedf0;
  --text-main: #1a1a1a;
  --text-sub: #555555;
  --accent: #1e3a8a;
  --accent-light: #3b82f6;
  --word-highlight-bg: #bfdbfe;
  --word-highlight-text: #1e3a8a;
  --border: #e5e7eb;
  --card-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}}

[data-theme="dark"] {{
  --bg-page: #12151c;
  --bg-panel: #1b202c;
  --bg-hover: #262e3f;
  --text-main: #e2e8f0;
  --text-sub: #94a3b8;
  --accent: #60a5fa;
  --accent-light: #93c5fd;
  --word-highlight-bg: #2563eb;
  --word-highlight-text: #ffffff;
  --border: #2d3748;
  --card-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: var(--font-serif);
  background-color: var(--bg-page);
  color: var(--text-main);
  font-size: var(--font-size-base);
  line-height: var(--line-height-base);
  padding-bottom: 140px;
  transition: background-color 0.25s ease, color 0.25s ease;
  -webkit-font-smoothing: antialiased;
}}

/* Top Sticky Navigation Bar */
.top-nav {{
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-page);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  backdrop-filter: blur(8px);
}}

.nav-bar {{
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}}

.chapter-nav-wrapper {{
  position: relative;
  flex: 1;
  min-width: 0;
}}

.chapter-btn {{
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  color: var(--text-main);
  padding: 6px 12px;
  border-radius: 8px;
  font-family: var(--font-sans);
  font-size: 0.90rem;
  font-weight: 600;
  cursor: pointer;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: all 0.2s ease;
}}

.chapter-btn:hover {{
  background: var(--bg-hover);
  border-color: var(--accent-light);
}}

.dropdown-arrow {{
  font-size: 0.75rem;
  color: var(--text-sub);
}}

.chapter-dropdown {{
  display: none;
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  width: 280px;
  max-height: 400px;
  overflow-y: auto;
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  padding: 6px 0;
  z-index: 2000;
}}

.chapter-dropdown.open {{
  display: block;
}}

.chapter-item {{
  padding: 8px 14px;
  font-family: var(--font-sans);
  font-size: 0.88rem;
  color: var(--text-main);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-bottom: 1px solid var(--border);
  transition: background 0.15s ease;
}}

.chapter-item:last-child {{
  border-bottom: none;
}}

.chapter-item:hover {{
  background: var(--bg-hover);
}}

.chapter-item.active {{
  background: var(--bg-panel);
  color: var(--accent);
  font-weight: 600;
  border-left: 3px solid var(--accent);
}}

.chapter-item-tag {{
  font-size: 0.72rem;
  color: var(--text-sub);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}

.nav-actions {{
  display: flex;
  align-items: center;
  gap: 8px;
}}

.icon-btn {{
  background: var(--bg-panel);
  border: 1px solid var(--border);
  color: var(--text-main);
  padding: 6px 12px;
  border-radius: 8px;
  font-family: var(--font-sans);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
}}

.icon-btn:hover {{
  background: var(--bg-hover);
  border-color: var(--accent-light);
}}

.icon-btn.primary {{
  background: var(--accent);
  color: #ffffff;
  border-color: var(--accent);
}}

.icon-btn.primary:hover {{
  filter: brightness(1.1);
}}

/* Collapsible Control Drawer */
.control-drawer {{
  display: none;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  padding: 12px 16px;
}}

.control-drawer.open {{
  display: block;
}}

.drawer-inner {{
  max-width: var(--max-content-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}}

.control-drawer audio {{
  width: 100%;
  height: 38px;
  border-radius: 6px;
}}

.drawer-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}}

.drawer-group {{
  display: flex;
  align-items: center;
  gap: 6px;
}}

.search-input {{
  background: var(--bg-page);
  border: 1px solid var(--border);
  color: var(--text-main);
  padding: 6px 12px;
  border-radius: 6px;
  font-family: var(--font-sans);
  font-size: 0.85rem;
  outline: none;
  width: 100%;
}}

.drawer-tips {{
  display: none;
  font-family: var(--font-sans);
  font-size: 0.82rem;
  background: var(--bg-page);
  padding: 14px 18px;
  border-radius: 10px;
  border: 1px solid var(--border);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.02);
}}

.drawer-tips.open {{
  display: block;
}}

.tips-columns {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}}

@media (max-width: 600px) {{
  .tips-columns {{
    grid-template-columns: 1fr;
    gap: 14px;
  }}
}}

.tips-section {{
  display: flex;
  flex-direction: column;
  gap: 6px;
}}

.tips-section-title {{
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 2px;
  padding-bottom: 4px;
  border-bottom: 1px dashed var(--border);
}}

.tips-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--text-main);
  line-height: 1.4;
}}

.tips-key {{
  display: inline-block;
  font-family: var(--font-sans);
  font-weight: 600;
  font-size: 0.74rem;
  color: var(--text-main);
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 2px 7px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  white-space: nowrap;
}}

/* Main Layout */
.container {{
  max-width: var(--max-content-width);
  margin: 28px auto;
  padding: 0 20px;
}}

.chapter-section {{
  display: none;
}}

.chapter-section.active {{
  display: block;
}}

.book-header {{
  text-align: center;
  margin-bottom: 36px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}}

.book-subtitle {{
  font-family: var(--font-sans);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--accent);
  margin-bottom: 8px;
}}

.book-title {{
  font-size: 2.1rem;
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 10px;
}}

.book-author {{
  font-family: var(--font-sans);
  font-size: 0.95rem;
  color: var(--text-sub);
}}

/* Sentence Units & Tap Inspection */
.sentence-unit {{
  margin-bottom: 12px;
  border-radius: 8px;
  transition: background 0.15s ease;
}}

.sentence-text {{
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: background 0.15s ease;
}}

.sentence-text:hover {{
  background: var(--bg-hover);
}}

.sentence-unit.active .sentence-text {{
  background: var(--bg-panel);
}}

.sentence-unit[data-matched="0"] .sentence-text {{
  opacity: 0.92;
}}

.w {{
  display: inline;
  border-radius: 3px;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}}

.w.active-word {{
  background-color: var(--word-highlight-bg) !important;
  color: var(--word-highlight-text) !important;
  border-radius: 3px;
}}

/* Collapsible Inspection Card */
.inspect-panel {{
  display: none;
  background: var(--bg-panel);
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  padding: 10px 14px;
  margin: 6px 0 14px 6px;
  box-shadow: var(--card-shadow);
  cursor: pointer;
}}

.sentence-unit.active .inspect-panel {{
  display: block;
}}

.inspect-trans {{
  font-family: var(--font-serif);
  font-size: 1.02rem;
  line-height: 1.72;
  color: var(--text-main);
  margin-bottom: 8px;
}}

.inspect-vocab-list {{
  border-top: 1px solid var(--border);
  padding-top: 6px;
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}}

.vocab-row {{
  font-family: var(--font-sans);
  font-size: 0.82rem;
  line-height: 1.45;
  display: flex;
  align-items: baseline;
  gap: 6px;
}}

.v-word {{
  font-weight: 700;
  color: var(--accent);
}}

.v-pos {{
  font-size: 0.72rem;
  color: var(--text-sub);
  font-style: italic;
}}

.v-def {{
  color: var(--text-main);
}}

.chapter-heading-1 {{
  font-size: 1.35rem;
  font-weight: 700;
  margin-top: 32px;
  margin-bottom: 12px;
  color: var(--accent);
  border-bottom: 1px solid var(--border);
  padding-bottom: 6px;
}}

/* Mobile Specific Refinements */
@media (max-width: 640px) {{
  :root {{
    --font-size-base: 1.15rem;
    --line-height-base: 1.82;
  }}
  .container {{
    padding: 0 14px;
    margin: 16px auto;
  }}
  .book-title {{
    font-size: 1.65rem;
  }}
  .nav-bar {{
    padding: 6px 12px;
  }}
  .icon-btn {{
    padding: 4px 10px;
    font-size: 0.78rem;
  }}
  .chapter-btn {{
    font-size: 0.85rem;
  }}
  .chapter-dropdown {{
    width: 240px;
  }}
}}
</style>
</head>
<body onclick="closeDropdowns(event)">

<header class="top-nav">
  <div class="nav-bar">
    <div class="chapter-nav-wrapper">
      <button class="chapter-btn" id="chapterSelectBtn" onclick="toggleChapterDropdown(event)">
        <span>{html.escape(book_title)} · <span id="currentChapterLabel">Ch. 0</span></span>
        <span class="dropdown-arrow">▾</span>
      </button>
      <div class="chapter-dropdown" id="chapterDropdown">
"""

    for ch in loaded_chapters:
        cnum = ch["num"]
        ctitle = ch["title"]
        label = ch["label"]
        active_cls = " active" if cnum == first_ch_num else ""
        html_head += f"""        <div class="chapter-item{active_cls}" id="menu-ch-{cnum}" onclick="switchChapter({cnum})">
          <span class="chapter-item-tag">{label}</span>
          <span>{html.escape(ctitle)}</span>
        </div>\n"""

    html_head += f"""      </div>
    </div>
    
    <div class="nav-actions">
      <button class="icon-btn primary" id="globalPlayBtn" onclick="toggleGlobalPlay()">▶ Play</button>
      <button class="icon-btn" id="drawerToggleBtn" onclick="toggleDrawer()">⚙️ Menu</button>
    </div>
  </div>
  
  <div class="control-drawer" id="controlDrawer">
    <div class="drawer-inner">
      <audio id="audioTrack" controls preload="metadata" src="{html.escape(first_ch_public_audio or first_ch_audio)}"></audio>
      <div class="drawer-row">
        <div class="drawer-group">
          <button class="icon-btn" onclick="adjustFontSize(-1)">A-</button>
          <button class="icon-btn" onclick="adjustFontSize(1)">A+</button>
          <button class="icon-btn" onclick="toggleTheme()">Theme</button>
          <button class="icon-btn" id="tipsToggleBtn" onclick="toggleTips()">Tips</button>
        </div>
        <div class="drawer-group">
          <label style="font-family: var(--font-sans); font-size: 0.82rem; color: var(--text-sub);">
            Repeat
            <select id="shadowRepeatSelect" onchange="setShadowRepetitions(this.value)">
              <option value="1">1x</option><option value="3" selected>3x</option><option value="5">5x</option>
            </select>
          </label>
          <button class="icon-btn" id="shadowBtn" onclick="toggleShadowing()">Repeat</button>
        </div>
        <div class="drawer-group">
          <label style="font-family: var(--font-sans); font-size: 0.82rem; display: flex; align-items: center; gap: 4px; color: var(--text-sub);">
            <input type="checkbox" id="autoScrollCheck" checked onchange="toggleAutoScroll(this.checked)"> Auto-scroll
          </label>
        </div>
      </div>
      <input type="text" id="searchInput" class="search-input" placeholder="Search in active chapter..." oninput="handleSearch()">
      <div class="drawer-tips" id="drawerTips">
        <div class="tips-columns">
          <div class="tips-section">
            <div class="tips-section-title">Touch & Mouse</div>
            <div class="tips-row"><span class="tips-key">Tap Sentence</span><span>Play audio & show breakdown</span></div>
            <div class="tips-row"><span class="tips-key">Double Tap</span><span>Repeat sentence loop</span></div>
            <div class="tips-row"><span class="tips-key">Tap Card</span><span>Collapse card</span></div>
          </div>
          <div class="tips-section">
            <div class="tips-section-title">Keyboard Shortcuts</div>
            <div class="tips-row"><span class="tips-key">Space</span><span>Toggle breakdown card</span></div>
            <div class="tips-row"><span class="tips-key">R</span><span>Repeat current sentence</span></div>
            <div class="tips-row"><span class="tips-key">← / →</span><span>Previous / Next sentence</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</header>

<main class="container">
"""

    for ch in loaded_chapters:
        cnum = ch["num"]
        ctitle = ch["title"]
        caudio = ch["audio"]
        cpublic_audio = ch.get("public_audio") or ""
        csents = ch["sentences"]
        active_cls = " active" if cnum == first_ch_num else ""
        ch_heading_label = ch["label"].upper()
        
        html_head += f"""
  <!-- CHAPTER {cnum} -->
  <section class="chapter-section{active_cls}" id="chapter-{cnum}" data-audio="{html.escape(caudio)}" data-public-audio="{html.escape(cpublic_audio)}" data-ch="{cnum}">
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
            raw_text = s.get("text", "")
            
            word_spans = s.get("word_spans", [])
            word_html_list = []
            if word_spans:
                for w in word_spans:
                    rw = html.escape(w["word"])
                    ws = w["start"]
                    we = w["end"]
                    word_html_list.append(f'<span class="w" data-s="{ws}" data-e="{we}">{rw}</span>')
            else:
                for rw in s["text"].split():
                    word_html_list.append(f'<span class="w" data-s="{start}" data-e="{end}">{html.escape(rw)}</span>')
            
            sentence_text_html = " ".join(word_html_list)
            
            vocab_html_list = []
            for v in vocab:
                vw = html.escape(v.get("word", ""))
                vp = html.escape(v.get("pos", ""))
                vd = html.escape(v.get("def", ""))
                vocab_html_list.append(f'<div class="vocab-row"><span class="v-word">{vw}</span><span class="v-pos">{vp}</span><span class="v-def">{vd}</span></div>')
                
            vocab_section = ""
            if vocab_html_list:
                vocab_section = f'<div class="inspect-vocab-list">{"".join(vocab_html_list)}</div>'
                
            h_class = " chapter-heading-1" if is_h else ""
            html_head += f"""
      <div class="sentence-unit" id="{sid}" data-start="{start}" data-end="{end}" data-matched="{has_match}" data-text="{html.escape(raw_text)}" data-trans="{trans}" data-vocab="{html.escape(json.dumps(vocab, ensure_ascii=False))}">
        <div class="sentence-text{h_class}" onclick="handleSentenceClick(event, '{sid}', {start}, {end}, {has_match})">
          <span class="s-content">{sentence_text_html}</span>
        </div>
        <div class="inspect-panel" onclick="handleInspectPanelClick(event, '{sid}')" title="Click to collapse / 点击折叠">
          <div class="inspect-trans">{trans}</div>
          {vocab_section}
        </div>
      </div>
"""

        html_head += """    </div>
  </section>
"""

    book_id_json = json.dumps(book_id)
    html_tail = f"""
</main>

<script>
window.__BOOK_ID__ = {book_id_json};
window.__INITIAL_CHAPTER__ = {first_ch_num};
window.__INITIAL_PUBLIC_AUDIO__ = {json.dumps(first_ch_public_audio)};
const STORAGE_PREFIX = 'reader_' + (window.__BOOK_ID__ || 'default') + '_';
""" + """
const audio = document.getElementById('audioTrack');
const globalPlayBtn = document.getElementById('globalPlayBtn');
const controlDrawer = document.getElementById('controlDrawer');
const drawerToggleBtn = document.getElementById('drawerToggleBtn');
const chapterDropdown = document.getElementById('chapterDropdown');
const currentChapterLabel = document.getElementById('currentChapterLabel');

let activeChapterNum = parseInt(localStorage.getItem(STORAGE_PREFIX + 'active_ch') || String(window.__INITIAL_CHAPTER__), 10);
let autoScrollEnabled = localStorage.getItem(STORAGE_PREFIX + 'autoscroll') !== 'false';
let currentPlayingId = null;
let currentActiveWordEl = null;
let sentenceTimeIndex = [];
let syncFrameId = null;
const shadowState = { phase: 'idle', repetitions: 3, completed: 0, sentence: null, timer: null };

document.getElementById('autoScrollCheck').checked = autoScrollEnabled;

function toggleAutoScroll(enabled) {
  autoScrollEnabled = enabled;
  localStorage.setItem(STORAGE_PREFIX + 'autoscroll', enabled);
}

// Chapter Switching
function toggleChapterDropdown(event) {
  if (event) event.stopPropagation();
  chapterDropdown.classList.toggle('open');
}

function closeDropdowns(event) {
  if (chapterDropdown.classList.contains('open')) {
    chapterDropdown.classList.remove('open');
  }
}

function resolveAudioSource(section) {
  const localSource = section.dataset.audio;
  const publicSource = section.dataset.publicAudio;
  return window.location.protocol === 'file:' || !publicSource ? localSource : publicSource;
}

function rebuildSentenceTimeIndex() {
  const section = document.querySelector('.chapter-section.active');
  sentenceTimeIndex = section ? Array.from(section.querySelectorAll('.sentence-unit')).map(el => ({
    start: parseFloat(el.dataset.start || '0'),
    end: parseFloat(el.dataset.end || '0'),
    el: el
  })).filter(item => item.end > item.start && item.el.dataset.matched !== '0').sort((a, b) => a.start - b.start) : [];
}

function findSentenceAt(time) {
  let low = 0;
  let high = sentenceTimeIndex.length - 1;
  let candidate = null;
  while (low <= high) {
    const middle = (low + high) >> 1;
    const item = sentenceTimeIndex[middle];
    if (item.start <= time) {
      candidate = item;
      low = middle + 1;
    } else {
      high = middle - 1;
    }
  }
  return candidate && time < candidate.end ? candidate.el : null;
}

function switchChapter(chNum) {
  activeChapterNum = chNum;
  localStorage.setItem(STORAGE_PREFIX + 'active_ch', chNum);
  currentChapterLabel.textContent = chNum === 0 ? 'Preface' : 'Ch. ' + chNum;
  
  document.querySelectorAll('.chapter-item').forEach(el => el.classList.remove('active'));
  const menuEl = document.getElementById('menu-ch-' + chNum);
  if (menuEl) menuEl.classList.add('active');
  chapterDropdown.classList.remove('open');
  
  document.querySelectorAll('.chapter-section').forEach(sec => {
    sec.classList.remove('active');
    if (parseInt(sec.dataset.ch, 10) === chNum) {
      sec.classList.add('active');
      const audioSrc = resolveAudioSource(sec);
      if (audio.getAttribute('src') !== audioSrc) {
        const wasPlaying = !audio.paused;
        audio.src = audioSrc;
        currentPlayingId = null;
        if (currentActiveWordEl) {
          currentActiveWordEl.classList.remove('active-word');
          currentActiveWordEl = null;
        }
        if (wasPlaying) audio.play();
      }
    }
  });
  rebuildSentenceTimeIndex();
  
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

switchChapter(activeChapterNum);

function toggleDrawer() {
  const isOpen = controlDrawer.classList.contains('open');
  if (isOpen) {
    controlDrawer.classList.remove('open');
    drawerToggleBtn.innerHTML = '⚙️ Menu';
    localStorage.setItem(STORAGE_PREFIX + 'drawer_open', 'false');
  } else {
    controlDrawer.classList.add('open');
    drawerToggleBtn.innerHTML = '✕ Close';
    localStorage.setItem(STORAGE_PREFIX + 'drawer_open', 'true');
  }
}

const savedDrawerState = localStorage.getItem(STORAGE_PREFIX + 'drawer_open');
if (savedDrawerState === 'true') {
  controlDrawer.classList.add('open');
  drawerToggleBtn.innerHTML = '✕ Close';
}

const themes = ['sepia', 'light', 'dark'];
let currentThemeIndex = 0;
function toggleTheme() {
  currentThemeIndex = (currentThemeIndex + 1) % themes.length;
  document.documentElement.setAttribute('data-theme', themes[currentThemeIndex]);
  localStorage.setItem(STORAGE_PREFIX + 'theme', themes[currentThemeIndex]);
}

const savedTheme = localStorage.getItem(STORAGE_PREFIX + 'theme');
if (savedTheme) {
  document.documentElement.setAttribute('data-theme', savedTheme);
  currentThemeIndex = themes.indexOf(savedTheme);
}

let currentFontSizeRem = 1.20;
function adjustFontSize(delta) {
  currentFontSizeRem = Math.max(0.95, Math.min(1.8, currentFontSizeRem + delta * 0.08));
  document.documentElement.style.setProperty('--font-size-base', currentFontSizeRem + 'rem');
  localStorage.setItem(STORAGE_PREFIX + 'font_size', currentFontSizeRem);
}

const savedFontSize = localStorage.getItem(STORAGE_PREFIX + 'font_size');
if (savedFontSize) {
  currentFontSizeRem = parseFloat(savedFontSize);
  document.documentElement.style.setProperty('--font-size-base', currentFontSizeRem + 'rem');
}

function toggleTips() {
  const tipsEl = document.getElementById('drawerTips');
  const btn = document.getElementById('tipsToggleBtn');
  if (tipsEl) {
    tipsEl.classList.toggle('open');
    if (btn) btn.classList.toggle('active');
  }
}

let lastSentenceClickTime = 0;
let lastSentenceClickId = null;

function startSentenceShadowing(sentenceEl) {
  if (!sentenceEl || sentenceEl.dataset.matched !== '1') return;
  if (shadowState.timer) clearTimeout(shadowState.timer);
  shadowState.phase = 'playing';
  shadowState.completed = 0;
  shadowState.sentence = sentenceEl;
  const btn = document.getElementById('shadowBtn');
  if (btn) btn.textContent = 'Stop Repeat';
  
  const activeSection = document.querySelector('.chapter-section.active') || document.querySelector('.chapter-section');
  if (activeSection && activeSection.dataset.audio) {
    attachAudioSource(activeSection.dataset.audio);
  }
  const start = parseFloat(sentenceEl.dataset.start);
  audio.currentTime = start;
  audio.play();
  globalPlayBtn.textContent = '⏸ Pause';
  sentenceEl.classList.add('active');
}

function handleSentenceClick(event, id, start, end, hasMatch) {
  if (event) event.stopPropagation();
  const el = document.getElementById(id);
  if (!el) return;
  
  const now = Date.now();
  const isDoubleTap = (lastSentenceClickId === id && (now - lastSentenceClickTime) < 350);
  lastSentenceClickTime = now;
  lastSentenceClickId = id;
  
  if (isDoubleTap) {
    startSentenceShadowing(el);
    return;
  }
  
  localStorage.setItem(STORAGE_PREFIX + 'last_sentence_c' + activeChapterNum, id);
  if (start > 0 || hasMatch) {
    audio.currentTime = start;
    audio.play();
    globalPlayBtn.textContent = '⏸ Pause';
  }
  el.classList.add('active');
}

function handleInspectPanelClick(event, id) {
  if (event) event.stopPropagation();
  const selection = window.getSelection();
  if (selection && selection.toString().trim().length > 0) return;
  
  const el = document.getElementById(id);
  if (el) {
    el.classList.remove('active');
  }
}

function toggleGlobalPlay() {
  if (audio.paused) {
    audio.play();
    globalPlayBtn.textContent = '⏸ Pause';
  } else {
    audio.pause();
    globalPlayBtn.textContent = '▶ Play';
  }
}

audio.preservesPitch = true;
audio.mozPreservesPitch = true;
audio.webkitPreservesPitch = true;

function setShadowRepetitions(value) {
  shadowState.repetitions = Math.max(1, parseInt(value, 10) || 3);
}

function stopShadowing() {
  if (shadowState.timer) clearTimeout(shadowState.timer);
  shadowState.phase = 'idle';
  shadowState.completed = 0;
  shadowState.sentence = null;
  shadowState.timer = null;
  const btn = document.getElementById('shadowBtn');
  if (btn) btn.textContent = 'Repeat';
}

function toggleShadowing() {
  if (shadowState.phase !== 'idle') {
    stopShadowing();
    return;
  }
  const sentence = findSentenceAt(audio.currentTime) || document.getElementById(currentPlayingId);
  if (sentence) {
    startSentenceShadowing(sentence);
  }
}

function advanceShadowing() {
  if (shadowState.phase === 'idle' || !shadowState.sentence) return;
  const end = parseFloat(shadowState.sentence.dataset.end);
  if (audio.currentTime < end) return;
  audio.pause();
  shadowState.completed += 1;
  if (shadowState.completed >= shadowState.repetitions) {
    stopShadowing();
    return;
  }
  shadowState.phase = 'pause_buffer';
  shadowState.timer = setTimeout(() => {
    if (!shadowState.sentence) return;
    shadowState.phase = 'replaying';
    audio.currentTime = parseFloat(shadowState.sentence.dataset.start);
    audio.play();
  }, 650);
}

function startSyncLoop() {
  if (syncFrameId === null && !audio.paused && !document.hidden) syncFrameId = requestAnimationFrame(syncPlayback);
}

function stopSyncLoop() {
  if (syncFrameId !== null) cancelAnimationFrame(syncFrameId);
  syncFrameId = null;
}

audio.addEventListener('play', () => { globalPlayBtn.textContent = '⏸ Pause'; startSyncLoop(); });
audio.addEventListener('pause', () => { globalPlayBtn.textContent = '▶ Play'; stopSyncLoop(); });
audio.addEventListener('timeupdate', syncPlayback);
document.addEventListener('visibilitychange', () => { if (document.hidden) stopSyncLoop(); else startSyncLoop(); });

function syncPlayback() {
  syncFrameId = null;
  if (!audio.paused) {
    const curTime = audio.currentTime;
    const activeSection = document.querySelector('.chapter-section.active');
    
    if (activeSection) {
      const activeUnit = findSentenceAt(curTime);
      
      if (activeUnit) {
        if (activeUnit.id !== currentPlayingId) {
          currentPlayingId = activeUnit.id;
          localStorage.setItem(STORAGE_PREFIX + 'last_sentence_c' + activeChapterNum, activeUnit.id);
          
          if (autoScrollEnabled) {
            const rect = activeUnit.getBoundingClientRect();
            const inView = rect.top >= 90 && rect.bottom <= (window.innerHeight - 90);
            if (!inView) {
              activeUnit.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }
        }
        
        const wordEls = activeUnit.querySelectorAll('.w');
        let foundWord = null;
        for (let w of wordEls) {
          const ws = parseFloat(w.dataset.s);
          const we = parseFloat(w.dataset.e);
          if (ws < we && curTime >= ws && curTime < we) {
            foundWord = w;
            break;
          }
        }
        
        if (foundWord !== currentActiveWordEl) {
          if (currentActiveWordEl) currentActiveWordEl.classList.remove('active-word');
          if (foundWord) foundWord.classList.add('active-word');
          currentActiveWordEl = foundWord;
        }
      } else {
        if (currentActiveWordEl) {
          currentActiveWordEl.classList.remove('active-word');
          currentActiveWordEl = null;
        }
      }
    }
    advanceShadowing();
  }
  startSyncLoop();
}

rebuildSentenceTimeIndex();

function handleSearch() {
  const query = document.getElementById('searchInput').value.toLowerCase().trim();
  const activeSection = document.querySelector('.chapter-section.active');
  if (!activeSection) return;
  const units = activeSection.querySelectorAll('.sentence-unit');
  
  for (let u of units) {
    if (!query) {
      u.style.display = '';
      continue;
    }
    const text = u.textContent.toLowerCase();
    if (text.includes(query)) {
      u.style.display = '';
    } else {
      u.style.display = 'none';
    }
  }
}

// Desktop Keyboard Navigation (Arrow Keys + Spacebar)
window.addEventListener('keydown', (e) => {
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
    return;
  }
  
  const activeSection = document.querySelector('.chapter-section.active');
  if (!activeSection) return;
  
  const units = Array.from(activeSection.querySelectorAll('.sentence-unit'));
  if (units.length === 0) return;
  
  const curTime = audio.currentTime;

  if (e.key === 'r' || e.key === 'R') {
    e.preventDefault();
    toggleShadowing();
    return;
  }
  
  let currentIndex = units.findIndex(u => {
    const s = parseFloat(u.dataset.start);
    const e = parseFloat(u.dataset.end);
    return curTime >= s && curTime <= e;
  });
  
  if (currentIndex === -1) {
    for (let i = units.length - 1; i >= 0; i--) {
      if (parseFloat(units[i].dataset.start) <= curTime) {
        currentIndex = i;
        break;
      }
    }
    if (currentIndex === -1) currentIndex = 0;
  }
  
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault();
    const targetIdx = Math.max(0, currentIndex - 1);
    const targetUnit = units[targetIdx];
    if (targetUnit) {
      const st = parseFloat(targetUnit.dataset.start);
      audio.currentTime = st;
      audio.play();
      globalPlayBtn.textContent = '⏸ Pause';
      targetUnit.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
    e.preventDefault();
    const targetIdx = Math.min(units.length - 1, currentIndex + 1);
    const targetUnit = units[targetIdx];
    if (targetUnit) {
      const st = parseFloat(targetUnit.dataset.start);
      audio.currentTime = st;
      audio.play();
      globalPlayBtn.textContent = '⏸ Pause';
      targetUnit.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  } else if (e.code === 'Space') {
    e.preventDefault();
    const currentUnit = units[currentIndex];
    if (currentUnit) {
      currentUnit.classList.toggle('active');
    }
  }
});
</script>
</body>
</html>
"""
    atomic_write_text(output_html_path, html_head + html_tail)
        
    print(f"Master multi-chapter interactive reader successfully compiled -> {output_html_path}")
