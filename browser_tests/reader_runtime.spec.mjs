import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { test, expect } from '@playwright/test';

function buildFixture() {
  const root = mkdtempSync(join(tmpdir(), 'reader-browser-'));
  const script = String.raw`
import json, sys, wave
from pathlib import Path
from validate_outputs import validate_for_release
from html_builder import build_master_reader
root = Path(sys.argv[1]); (root / 'audio').mkdir()
with wave.open(str(root / 'audio' / 'chapter_01.wav'), 'wb') as output:
    output.setnchannels(1); output.setsampwidth(2); output.setframerate(8000); output.writeframes(b'\0\0' * 8000)
(root / 'audio' / 'chapter_01.mp3').write_bytes(b'gate-fixture')
canonical = [{'id':'s-1','text':'Observed sentence.'}]
analysis = [{**canonical[0], 'trans':'可播放句子。', 'vocab':[]}]
aligned = [{**analysis[0], 'word_spans':[{'word':'Observed','start':0.2,'end':0.4},{'word':'sentence.','start':0.4,'end':0.7}], 'start':0.2,'end':0.7,'raw_start':0.2,'raw_end':0.7,'has_audio_match':True,'fallback_used':False,'alignment_status':'validated','matched_token_count':2,'source_token_count':2,'match_ratio':1.0}]
for suffix, data in [('canonical_sentences',canonical),('full_analysis',analysis),('aligned_sentences',aligned)]:
    (root / ('book_ch01_' + suffix + '.json')).write_text(json.dumps(data), encoding='utf-8')
report = root / 'reader_validation_report.json'; _, token = validate_for_release(root, report)
assert token
aligned.append({'id':'s-2','text':'Estimated reference.','trans':'不可播放。','vocab':[],'word_spans':[{'word':'Estimated','start':0.7,'end':0.8,'timing_source':'estimated'}],'raw_start':0.7,'raw_end':0.8,'has_audio_match':True,'fallback_used':False,'alignment_status':'validated','matched_token_count':1,'source_token_count':2,'match_ratio':0.5})
(root / 'book_ch01_aligned_sentences.json').write_text(json.dumps(aligned), encoding='utf-8')
build_master_reader('Browser fixture','Runtime gate','Test author',[{'num':1,'title':'Chapter One','audio':'./audio/chapter_01.wav','aligned_json':str(root / 'book_ch01_aligned_sentences.json')}],str(root / 'reader.html'),release_token=token,release_report_path=report)
print(root / 'reader.html')
`;
  execFileSync('python3', ['-c', script, root], { cwd: process.cwd(), encoding: 'utf8' });
  return root;
}

test('reader plays observed text and refuses estimated timing', async ({ page }) => {
  const root = buildFixture();
  await page.addInitScript(() => {
    let currentTime = 0;
    Object.defineProperty(HTMLMediaElement.prototype, 'currentTime', {
      configurable: true,
      get: () => currentTime,
      set: value => { currentTime = value; window.__readerSeek = value; },
    });
    HTMLMediaElement.prototype.play = function () { window.__readerPlayCalls = (window.__readerPlayCalls || 0) + 1; return Promise.resolve(); };
  });
  const server = createServer((request, response) => {
    const relative = new URL(request.url, 'http://localhost').pathname.replace(/^\//, '');
    try {
      const body = readFileSync(resolve(root, relative || 'reader.html'));
      response.writeHead(200, { 'Content-Type': relative.endsWith('.wav') ? 'audio/wav' : 'text/html' });
      response.end(body);
    } catch { response.writeHead(404); response.end(); }
  });
  await new Promise(resolveListen => server.listen(0, '127.0.0.1', resolveListen));
  const port = server.address().port;
  await page.goto(`http://127.0.0.1:${port}/reader.html`);
  await page.waitForFunction(() => document.readyState === 'complete');
  const observed = page.locator('#c1-s-1');
  await expect(observed).toHaveAttribute('data-matched', '1');
  await observed.locator('.sentence-text').evaluate(element => element.click());
  await expect.poll(() => page.evaluate(() => window.__readerSeek)).toBe(0.2);
  await expect.poll(() => page.evaluate(() => window.__readerPlayCalls)).toBe(1);
  await expect(observed).toHaveClass(/active/);

  const estimated = page.locator('#c1-s-2');
  await expect(estimated).toHaveAttribute('data-matched', '0');
  await estimated.locator('.sentence-text').evaluate(element => element.click());
  expect(await page.evaluate(() => window.__readerSeek)).toBe(0.2);
  expect(await page.evaluate(() => window.__readerPlayCalls)).toBe(1);
  await new Promise(resolveClose => server.close(resolveClose));
});
