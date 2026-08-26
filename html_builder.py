"""
Module: html_builder.py
Description: Compiles Multi-Chapter Apple Books-grade Interactive Readers with top-left dropdown switcher, zero-jitter word-by-word karaoke tracking, and unified tap inspection.
"""

import json
import html
import os
import sys

def build_master_reader(book_title, book_subtitle, book_author, chapters_config, output_html_path):
    """
    chapters_config: list of dicts with:
      - 'num': int (e.g. 1, 2)
      - 'title': str (e.g. 'The Cult of the Head Start')
      - 'audio': str (e.g. './audio/chapter_01.mp3')
      - 'aligned_json': str (path to aligned sentences JSON)
    """
    loaded_chapters = []
    for c in chapters_config:
        with open(c['aligned_json'], 'r', encoding='utf-8') as f:
            sents = json.load(f)
        loaded_chapters.append({
            'num': c['num'],
            'title': c['title'],
            'audio': c['audio'],
            'sentences': sents
        })
        
    first_ch_audio = loaded_chapters[0]['audio'] if loaded_chapters else "./audio/chapter_01.mp3"
    
    html_head = f"""<!DOCTYPE html>
<html lang="en" data-theme="sepia">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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

/* Sticky Ultra-Clean Top Bar */
.top-nav {{
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-page);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: var(--card-shadow);
}}

.nav-bar {{
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

/* Chapter Switcher Menu in Top-Left */
.chapter-nav-wrapper {{
  position: relative;
  display: inline-block;
}}

.chapter-btn {{
  background: transparent;
  border: 1px solid transparent;
  color: var(--accent);
  font-family: var(--font-sans);
  font-size: 0.92rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}}

.chapter-btn:hover {{
  background: var(--bg-panel);
  border-color: var(--border);
}}

.dropdown-arrow {{
  font-size: 0.75rem;
  opacity: 0.7;
}}

.chapter-dropdown {{
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 6px;
  width: 320px;
  max-height: 70vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  display: none;
  flex-direction: column;
  z-index: 200;
  animation: fadeIn 0.15s ease;
}}

.chapter-dropdown::-webkit-scrollbar {{
  width: 5px;
}}
.chapter-dropdown::-webkit-scrollbar-thumb {{
  background: var(--border);
  border-radius: 4px;
}}

.chapter-dropdown.open {{
  display: flex;
}}

.chapter-item {{
  padding: 10px 14px;
  font-family: var(--font-sans);
  font-size: 0.88rem;
  color: var(--text-main);
  text-decoration: none;
  cursor: pointer;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 2px;
  transition: background 0.15s ease;
}}

.chapter-item:last-child {{
  border-bottom: none;
}}

.chapter-item:hover {{
  background: var(--bg-hover);
}}

.chapter-item.active {{
  background: var(--bg-hover);
  border-left: 3.5px solid var(--accent);
  font-weight: 700;
}}

.chapter-item-tag {{
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
  letter-spacing: 0.5px;
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
  font-family: var(--font-sans);
  font-size: 0.84rem;
  font-weight: 600;
  border-radius: 6px;
  padding: 5px 12px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}}

.icon-btn:hover {{
  background: var(--bg-hover);
  border-color: var(--accent);
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
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1), padding 0.3s ease;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
}}

.control-drawer.open {{
  max-height: 240px;
  padding: 12px 16px 14px;
}}

.drawer-inner {{
  max-width: var(--max-content-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}}

.drawer-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}}

.drawer-group {{
  display: flex;
  align-items: center;
  gap: 6px;
}}

audio {{
  width: 100%;
  height: 36px;
  border-radius: 8px;
  outline: none;
}}

.search-input {{
  width: 100%;
  font-family: var(--font-sans);
  font-size: 0.88rem;
  padding: 7px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-page);
  color: var(--text-main);
  outline: none;
}}
.search-input:focus {{
  border-color: var(--accent);
}}

/* Main Container */
.container {{
  max-width: var(--max-content-width);
  margin: 20px auto;
  padding: 0 18px;
}}

.chapter-section {{
  display: none;
}}

.chapter-section.active {{
  display: block;
  animation: fadeIn 0.2s ease;
}}

.book-header {{
  margin-bottom: 28px;
  text-align: center;
  border-bottom: 2px solid var(--border);
  padding-bottom: 20px;
}}

.book-subtitle {{
  font-family: var(--font-sans);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--text-sub);
  margin-bottom: 6px;
}}

.book-title {{
  font-size: 1.95rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--accent);
}}

.book-author {{
  font-family: var(--font-sans);
  font-size: 0.95rem;
  color: var(--text-sub);
  margin-top: 6px;
}}

/* Pure Sentence Units (100% Clean Book Flow, Zero Box Background) */
.sentence-unit {{
  margin-bottom: 6px;
  padding: 2px 0;
  position: relative;
}}

/* Focused Word-by-Word Luminous Highlighting (Zero Jitter, Zero Box Background) */
.w {{
  display: inline;
  border-radius: 3px;
  padding: 1px 2px;
  transition: background-color 0.08s ease, color 0.08s ease;
}}

.w.active-word {{
  background-color: var(--word-highlight-bg);
  color: var(--word-highlight-text);
  border-radius: 3px;
}}

.sentence-unit:hover .s-content {{
  text-decoration: underline;
  text-decoration-color: var(--accent-light);
  text-decoration-thickness: 1.5px;
}}

.sentence-text {{
  cursor: pointer;
  display: inline;
  -webkit-tap-highlight-color: transparent;
}}

.s-content {{
  transition: all 0.15s;
}}

/* Inspection Panel (Clean, Rounded Card, Click to Collapse) */
.inspect-panel {{
  display: none;
  margin: 8px 0 14px 0;
  padding: 12px 16px;
  background: var(--bg-panel);
  border-radius: 8px;
  border: 1px solid var(--border);
  font-family: var(--font-sans);
  font-size: 0.94rem;
  line-height: 1.62;
  box-shadow: var(--card-shadow);
  cursor: pointer;
  position: relative;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
  animation: fadeIn 0.16s ease;
}}

.inspect-panel:hover {{
  border-color: var(--accent-light);
}}

@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(-4px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

.sentence-unit.active .inspect-panel {{
  display: block;
}}

.inspect-trans {{
  font-weight: 500;
  color: var(--text-main);
}}

.inspect-vocab-list {{
  margin-top: 8px;
  border-top: 1px dashed var(--border);
  padding-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}}

.vocab-row {{
  font-size: 0.90rem;
}}
.v-word {{ font-weight: 700; color: var(--accent); margin-right: 6px; }}
.v-pos {{ font-style: italic; color: var(--text-sub); margin-right: 6px; font-size: 0.82rem; }}
.v-def {{ color: var(--text-sub); }}

/* Heading styles */
.chapter-heading-1 {{
  font-size: 1.45rem;
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
        <span>📖 {html.escape(book_title)} · <span id="currentChapterLabel">Ch. 1</span></span>
        <span class="dropdown-arrow">▾</span>
      </button>
      <div class="chapter-dropdown" id="chapterDropdown">
"""

    for ch in loaded_chapters:
        cnum = ch["num"]
        ctitle = ch["title"]
        active_cls = " active" if cnum == 1 else ""
        html_head += f"""        <div class="chapter-item{active_cls}" id="menu-ch-{cnum}" onclick="switchChapter({cnum})">
          <span class="chapter-item-tag">Chapter {cnum}</span>
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
      <audio id="audioTrack" controls preload="metadata" src="{first_ch_audio}"></audio>
      <div class="drawer-row">
        <div class="drawer-group">
          <button class="icon-btn" onclick="adjustFontSize(-1)">A-</button>
          <button class="icon-btn" onclick="adjustFontSize(1)">A+</button>
          <button class="icon-btn" onclick="toggleTheme()">📜 Theme</button>
        </div>
        <div class="drawer-group">
          <label style="font-family: var(--font-sans); font-size: 0.82rem; display: flex; align-items: center; gap: 4px; color: var(--text-sub);">
            <input type="checkbox" id="autoScrollCheck" checked onchange="toggleAutoScroll(this.checked)"> Auto-scroll
          </label>
        </div>
      </div>
      <input type="text" id="searchInput" class="search-input" placeholder="Search in active chapter..." oninput="handleSearch()">
    </div>
  </div>
</header>

<main class="container">
"""

    for ch in loaded_chapters:
        cnum = ch["num"]
        ctitle = ch["title"]
        caudio = ch["audio"]
        csents = ch["sentences"]
        active_cls = " active" if cnum == 1 else ""
        
        html_head += f"""
  <!-- CHAPTER {cnum} -->
  <section class="chapter-section{active_cls}" id="chapter-{cnum}" data-audio="{caudio}" data-ch="{cnum}">
    <header class="book-header">
      <div class="book-subtitle">{html.escape(book_subtitle)}</div>
      <h1 class="book-title">CHAPTER {cnum}<br>{html.escape(ctitle)}</h1>
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
            trans = html.escape(s.get("trans", ""))
            vocab = s.get("vocab", [])
            
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
                
            if is_h:
                html_head += f"""
      <div class="sentence-unit" id="{sid}" data-start="{start}" data-end="{end}">
        <div class="sentence-text chapter-heading-1" onclick="handleSentenceClick(event, '{sid}', {start}, {end})">
          <span class="s-content">{sentence_text_html}</span>
        </div>
        <div class="inspect-panel" onclick="handleInspectPanelClick(event, '{sid}')" title="Click to collapse / 点击折叠">
          <div class="inspect-trans">{trans}</div>
          {vocab_section}
        </div>
      </div>
"""
            else:
                html_head += f"""
      <div class="sentence-unit" id="{sid}" data-start="{start}" data-end="{end}">
        <div class="sentence-text" onclick="handleSentenceClick(event, '{sid}', {start}, {end})">
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

    html_tail = """
</main>

<script>
const audio = document.getElementById('audioTrack');
const globalPlayBtn = document.getElementById('globalPlayBtn');
const controlDrawer = document.getElementById('controlDrawer');
const drawerToggleBtn = document.getElementById('drawerToggleBtn');
const chapterDropdown = document.getElementById('chapterDropdown');
const currentChapterLabel = document.getElementById('currentChapterLabel');

let activeChapterNum = parseInt(localStorage.getItem('book_active_ch') || '1', 10);
let autoScrollEnabled = localStorage.getItem('book_autoscroll') !== 'false';
let currentPlayingId = null;
let currentActiveWordEl = null;

document.getElementById('autoScrollCheck').checked = autoScrollEnabled;

function toggleAutoScroll(enabled) {
  autoScrollEnabled = enabled;
  localStorage.setItem('book_autoscroll', enabled);
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

function switchChapter(chNum) {
  activeChapterNum = chNum;
  localStorage.setItem('book_active_ch', chNum);
  currentChapterLabel.textContent = 'Ch. ' + chNum;
  
  document.querySelectorAll('.chapter-item').forEach(el => el.classList.remove('active'));
  const menuEl = document.getElementById('menu-ch-' + chNum);
  if (menuEl) menuEl.classList.add('active');
  chapterDropdown.classList.remove('open');
  
  document.querySelectorAll('.chapter-section').forEach(sec => {
    sec.classList.remove('active');
    if (parseInt(sec.dataset.ch, 10) === chNum) {
      sec.classList.add('active');
      const audioSrc = sec.dataset.audio;
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
  
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

if (activeChapterNum !== 1) {
  switchChapter(activeChapterNum);
}

function toggleDrawer() {
  const isOpen = controlDrawer.classList.contains('open');
  if (isOpen) {
    controlDrawer.classList.remove('open');
    drawerToggleBtn.innerHTML = '⚙️ Menu';
    localStorage.setItem('book_drawer_open', 'false');
  } else {
    controlDrawer.classList.add('open');
    drawerToggleBtn.innerHTML = '✕ Close';
    localStorage.setItem('book_drawer_open', 'true');
  }
}

const savedDrawerState = localStorage.getItem('book_drawer_open');
if (savedDrawerState === 'true') {
  controlDrawer.classList.add('open');
  drawerToggleBtn.innerHTML = '✕ Close';
}

const themes = ['sepia', 'light', 'dark'];
let currentThemeIndex = 0;
function toggleTheme() {
  currentThemeIndex = (currentThemeIndex + 1) % themes.length;
  document.documentElement.setAttribute('data-theme', themes[currentThemeIndex]);
  localStorage.setItem('book_theme', themes[currentThemeIndex]);
}

const savedTheme = localStorage.getItem('book_theme');
if (savedTheme) {
  document.documentElement.setAttribute('data-theme', savedTheme);
  currentThemeIndex = themes.indexOf(savedTheme);
}

let currentFontSizeRem = 1.20;
function adjustFontSize(delta) {
  currentFontSizeRem = Math.max(0.95, Math.min(1.8, currentFontSizeRem + delta * 0.08));
  document.documentElement.style.setProperty('--font-size-base', currentFontSizeRem + 'rem');
  localStorage.setItem('book_font_size', currentFontSizeRem);
}

const savedFontSize = localStorage.getItem('book_font_size');
if (savedFontSize) {
  currentFontSizeRem = parseFloat(savedFontSize);
  document.documentElement.style.setProperty('--font-size-base', currentFontSizeRem + 'rem');
}

function handleSentenceClick(event, id, start, end) {
  if (event) event.stopPropagation();
  const el = document.getElementById(id);
  if (!el) return;
  
  localStorage.setItem('book_last_sentence_c' + activeChapterNum, id);
  audio.currentTime = start;
  audio.play();
  globalPlayBtn.textContent = '⏸ Pause';
  
  // Clicking English sentence always opens the card and replays audio
  el.classList.add('active');
}

function handleInspectPanelClick(event, id) {
  if (event) event.stopPropagation();
  // Don't collapse if user is selecting/copying text
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

audio.addEventListener('play', () => { globalPlayBtn.textContent = '⏸ Pause'; });
audio.addEventListener('pause', () => { globalPlayBtn.textContent = '▶ Play'; });

function syncPlayback() {
  if (!audio.paused) {
    const curTime = audio.currentTime;
    const activeSection = document.querySelector('.chapter-section.active');
    
    if (activeSection) {
      const sentenceUnits = activeSection.querySelectorAll('.sentence-unit');
      let activeUnit = null;
      
      for (let u of sentenceUnits) {
        const s = parseFloat(u.dataset.start);
        const e = parseFloat(u.dataset.end);
        if (curTime >= s && curTime <= e) {
          activeUnit = u;
          break;
        }
      }
      
      if (activeUnit) {
        if (activeUnit.id !== currentPlayingId) {
          currentPlayingId = activeUnit.id;
          localStorage.setItem('book_last_sentence_c' + activeChapterNum, activeUnit.id);
          
          if (autoScrollEnabled) {
            const rect = activeUnit.getBoundingClientRect();
            const inView = rect.top >= 70 && rect.bottom <= (window.innerHeight - 70);
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
          if (curTime >= ws && curTime <= we) {
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
  }
  requestAnimationFrame(syncPlayback);
}

requestAnimationFrame(syncPlayback);

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
</script>
</body>
</html>
"""
    full_html = html_head + html_tail
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Master multi-chapter interactive reader successfully compiled -> {output_html_path}")
    return output_html_path
