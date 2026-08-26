"""
Module: extract_epub.py
Description: Unabridged 1-Sentence-1-Card EPUB Sentence Extractor with abbreviation and parenthetical protection.
"""

import zipfile
import re
import json
from html.parser import HTMLParser

def split_into_atomic_sentences(text):
    abbr_map = {
        'Mr.': '__ABBR_MR__',
        'Mrs.': '__ABBR_MRS__',
        'Ms.': '__ABBR_MS__',
        'Dr.': '__ABBR_DR__',
        'Prof.': '__ABBR_PROF__',
        'Sr.': '__ABBR_SR__',
        'Jr.': '__ABBR_JR__',
        'vs.': '__ABBR_VS__',
        'etc.': '__ABBR_ETC__',
        'e.g.': '__ABBR_EG__',
        'i.e.': '__ABBR_IE__',
        'U.S.': '__ABBR_US__',
        'U.K.': '__ABBR_UK__',
        'a.m.': '__ABBR_AM__',
        'p.m.': '__ABBR_PM__',
        'St.': '__ABBR_ST__',
        'Gen.': '__ABBR_GEN__',
        'Capt.': '__ABBR_CAPT__',
        'Col.': '__ABBR_COL__',
        'Lt.': '__ABBR_LT__',
        'Jan.': '__ABBR_JAN__',
        'Feb.': '__ABBR_FEB__',
        'Mar.': '__ABBR_MAR__',
        'Apr.': '__ABBR_APR__',
        'Aug.': '__ABBR_AUG__',
        'Sept.': '__ABBR_SEPT__',
        'Oct.': '__ABBR_OCT__',
        'Nov.': '__ABBR_NOV__',
        'Dec.': '__ABBR_DEC__'
    }
    
    protected = text
    for k, v in abbr_map.items():
        protected = protected.replace(k, v)
        
    protected = re.sub(r'(\d+)\.(\d+)', r'\1__DOT__\2', protected)
    
    # Split pattern for terminal punctuation + quotes/parens + space + capital
    # Footnote markers such as `.*` must remain with the preceding sentence
    # while still allowing the boundary before the next sentence.
    pattern = re.compile(r'([.!?]+[\"\'”’\)\*]*)\s+(?=[\"\'“‘\(]?[A-Z0-9])')
    tokens = pattern.split(protected)
    sentences = []
    
    i = 0
    while i < len(tokens):
        part = tokens[i]
        if i + 1 < len(tokens):
            part += tokens[i+1]
            i += 2
        else:
            i += 1
        part = part.strip()
        if not part:
            continue
        for k, v in abbr_map.items():
            part = part.replace(v, k)
        part = part.replace('__DOT__', '.')
        sentences.append(part)
        
    return sentences

class ChapterParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.current_tag = None
        self.current_attrs = {}
        self.current_text = []
        self.recording = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ['h1', 'h2', 'h3', 'h4', 'p', 'blockquote', 'li']:
            self.current_tag = tag
            self.current_attrs = attrs_dict
            self.current_text = []
            self.recording = True

    def handle_endtag(self, tag):
        if self.recording and tag == self.current_tag:
            full_text = ''.join(self.current_text).strip()
            if full_text:
                self.elements.append({
                    'tag': self.current_tag,
                    'class': self.current_attrs.get('class', ''),
                    'text': re.sub(r'\s+', ' ', full_text)
                })
            self.recording = False
            self.current_tag = None

    def handle_data(self, data):
        if self.recording:
            self.current_text.append(data)

def extract_chapter_from_epub(epub_path, chapter_internal_path, out_json_path):
    with zipfile.ZipFile(epub_path, 'r') as z:
        raw_html = z.read(chapter_internal_path).decode('utf-8')
        
    parser = ChapterParser()
    parser.feed(raw_html)
    
    canonical_items = []
    s_idx = 0
    for elem_idx, el in enumerate(parser.elements):
        tag = el['tag']
        txt = el['text']
        is_h = tag.startswith('h')
        
        if is_h:
            canonical_items.append({
                "id": f"s-{s_idx}",
                "elem_idx": elem_idx,
                "tag": tag,
                "text": txt,
                "is_heading": True
            })
            s_idx += 1
        else:
            sents = split_into_atomic_sentences(txt)
            for s in sents:
                canonical_items.append({
                    "id": f"s-{s_idx}",
                    "elem_idx": elem_idx,
                    "tag": tag,
                    "text": s,
                    "is_heading": False
                })
                s_idx += 1
                
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(canonical_items, f, ensure_ascii=False, indent=2)
        
    print(f"Extracted {len(canonical_items)} canonical sentences from {chapter_internal_path} -> {out_json_path}")
    return canonical_items

def extract_chapter_from_text(text_path, out_json_path):
    """Extract a chapter from a plain-text ebook export."""
    canonical_items, s_idx = [], 0
    lines = [line.strip() for line in open(text_path, encoding='utf-8').read().splitlines() if line.strip()]
    while lines and ('ebook' in lines[0].lower() or 'subscriber' in lines[0].lower() or 'sign up' in lines[0].lower()):
        lines.pop(0)
    if lines and not re.search(r'[.!?]$', lines[0]):
        canonical_items.append({'id': 's-0', 'elem_idx': 0, 'tag': 'h1', 'text': lines.pop(0), 'is_heading': True})
        s_idx = 1
    # Plain-text exports often put italicized words on separate lines. Joining
    # all remaining lines prevents artificial sentence breaks inside a paragraph.
    body = re.sub(r'\s+', ' ', ' '.join(lines)).strip()
    body = re.sub(r'\s+([,.;:!?])', r'\1', body)
    for sentence in split_into_atomic_sentences(body):
        canonical_items.append({'id': f's-{s_idx}', 'elem_idx': 1, 'tag': 'p', 'text': sentence, 'is_heading': False})
        s_idx += 1
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(canonical_items, f, ensure_ascii=False, indent=2)
    print(f'Extracted {len(canonical_items)} canonical sentences from {text_path} -> {out_json_path}')
    return canonical_items

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        extract_chapter_from_epub(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python3 extract_epub.py <epub_path> <chapter_internal_path> <out_json_path>")
