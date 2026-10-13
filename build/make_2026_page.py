"""Build 2026.html (the public season page) from the dashboard page source.

Usage, from the repo root:  python3 build/make_2026_page.py

Inputs:  build/dashboard-page.html  (the same page the private Claude dashboard runs)
         build/vendor/d3.min.js     (d3 v7.9.0, inlined so the page has no outside dependencies)
Output:  2026.html at the repo root. It loads its scores from 2026-data.json at runtime,
         so weekly updates only change 2026-data.json; rebuild only when the page itself changes.
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
page = open('build/dashboard-page.html').read()
d3 = open('build/vendor/d3.min.js').read()
style, rest = page.split('</style>', 1)
style = style.replace('<style>', '')
# public version: no "you" highlighting
rest = rest.replace("const ME = 'Zach';", "const ME = '';")
assert "const ME = '';" in rest
rest = rest.replace('<h1>Friends O\' Flembot · Season 21 so far</h1>',
  '<a class="fb-back" href="./">← Hall of Champions</a>\n    <h1>Friends O\' Flembot · Season 21 so far</h1>')
assert 'fb-back' in rest
shim = r"""
window.dash = (() => {
  let DATA = null, failed = false;
  const calcs = {}, cbs = [];
  const pal = {
    light: ['#2f6fdb', '#d9622b', '#1f9e74', '#8a5cd6', '#c4417a', '#b08600', '#2a9bb5', '#6b7a8f'],
    dark:  ['#6ea1ff', '#f08a5d', '#46c49a', '#b18cf2', '#ec6fa3', '#e0b43a', '#5cc3db', '#9aa8bb']
  };
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  const run = () => cbs.forEach(f => f());
  const api = {
    get colors() { return mq.matches ? pal.dark : pal.light; },
    calc(id, o) { calcs[id] = o; },
    data(id) {
      if (failed) return { status: 'error', data: [] };
      if (!DATA) return { status: 'loading', data: [] };
      if (id in DATA) return { status: 'ok', data: DATA[id] };
      const c = calcs[id];
      if (!c) return { status: 'missing', data: [] };
      if (!('value' in c)) c.value = c.fn(...c.inputs.map(i => api.data(i).data));
      return { status: 'ok', data: c.value };
    },
    onData(fn) { cbs.push(fn); fn(); },
    params() { return {}; }, setParams() {}, resetParams() {}, setLink() {}, refresh() {}
  };
  fetch('2026-data.json', { cache: 'no-cache' })
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(d => {
      DATA = d;
      const wk = Math.max(...d.matchups.map(r => Number(r.week)));
      const el = document.getElementById('fb-asof'); if (el) el.textContent = 'Week ' + wk;
      run();
    })
    .catch(() => { failed = true; run(); });
  let t;
  const redraw = () => { clearTimeout(t); t = setTimeout(run, 120); };
  window.addEventListener('resize', redraw);
  mq.addEventListener('change', redraw);
  return api;
})();
"""
tokens = """
:root {
  --font-anthropic-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-anthropic-serif: Georgia, "Times New Roman", serif;
  --color-bg: #faf9f6; --color-panel: #ffffff; --color-fg: #1d1c1a; --color-fg-muted: #6b6862;
  --color-border-line: #e4e1da; --color-ok: #1b7f4c; --color-warn: #a66a00; --color-bad: #c0392b;
  --cds-border: #d9d5cc; --cds-chart-grid: #ece9e2; --cds-chart-muted: #b9b4aa; --cds-chart-reference: #8a857b;
  --cds-surface-popover: #ffffff; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.12); --cds-text-secondary: #6b6862;
  --cds-font-size-caption: 12px; --cds-font-size-body: 14px; --cds-font-size-heading: 16px; --cds-font-size-title: 30px;
  --cds-font-weight-medium: 600;
  --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 14px; --cds-gap-lg: 22px;
  --cds-pad-xs: 5px; --cds-pad-sm: 9px; --cds-pad-lg: 18px; --cds-radius: 10px; --cds-dur-slow: 300ms;
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #1a1918; --color-panel: #23221f; --color-fg: #eeebe4; --color-fg-muted: #a39f96;
    --color-border-line: #3a3833; --color-ok: #5cc98d; --color-warn: #e0b43a; --color-bad: #f07a6a;
    --cds-border: #45423c; --cds-chart-grid: #33312d; --cds-chart-muted: #6d6961; --cds-chart-reference: #8e897f;
    --cds-surface-popover: #2c2a27; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.5); --cds-text-secondary: #a39f96;
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); }
#dash-root { max-width: 1200px; margin-inline: auto; padding: 28px 16px 48px; }
@media (min-width: 700px) { #dash-root { padding: 36px 28px 64px; } }
.fb-back { display: inline-block; font-size: var(--cds-font-size-caption); color: var(--color-fg-muted); text-decoration: none; margin-bottom: var(--cds-gap-sm); }
.fb-back:hover { color: var(--color-fg); }
.fb-foot { font-size: var(--cds-font-size-caption); color: var(--color-fg-muted); margin-top: var(--cds-gap-sm); }
.fb b { font-weight: var(--cds-font-weight-medium); }
"""
foot = '\n<p class="fb-foot">Updated through <span id="fb-asof">the latest week</span>. Scores come from the weekly recap emails and are subject to Yahoo stat corrections.</p>'
body = rest.replace('<script>', '<script>' + shim + '\n', 1)
# put footer at end of .fb container: before first <script>
i = body.index('<script>')
j = body.rindex('</div>', 0, i)
body = body[:j] + foot + '\n' + body[j:]
out = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flembot 2026 Season</title>
<meta name="description" content="Friends O' Flembot Season 21: standings, schedule luck and weekly scores.">
<style>{tokens}{style}</style>
<script>{d3}</script>
</head><body><div id="dash-root">{body}</div></body></html>"""
open('2026.html', 'w').write(out)
print('wrote 2026.html', len(out), 'bytes')
