#!/usr/bin/env python3
"""Сборка index.html со вкладками: Мир | GitHub | X | AI | PH + HN."""
import pathlib, html, json

MONTHS = {1:"января",2:"февраля",3:"марта",4:"апреля",5:"мая",6:"июня",7:"июля",8:"августа",9:"сентября",10:"октября",11:"ноября",12:"декабря"}

def pretty(date_str):
    y,m,d = date_str.split('-')
    return f"{int(d)} {MONTHS[int(m)]} {y}"

ROOT = pathlib.Path('/home/sasha/WORK/digest-repo')

TABS = [
    ('world', 'Мир'),
    ('github', 'GitHub'),
    ('x', 'X'),
    ('ai', 'AI'),
    ('ph-hn', 'PH + HN'),
]

def list_files(subdir):
    d = ROOT / subdir
    if not d.exists(): return []
    return sorted([p.stem for p in d.glob('*.html')], reverse=True)

data = {tab: list_files(tab) for tab, _ in TABS}

CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0f0f14; color: #e0e0e0; font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; }
h1 { color: #fff; font-size: 32px; margin-bottom: 8px; }
.sub { color: #888; font-size: 14px; margin-bottom: 28px; }
.tabs { display: flex; gap: 4px; border-bottom: 1px solid #2a2a3a; margin-bottom: 20px; flex-wrap: wrap; }
.tab { background: none; border: none; color: #888; padding: 10px 16px; font-size: 15px; cursor: pointer; border-bottom: 2px solid transparent; font-family: inherit; transition: color .15s, border-color .15s; }
.tab:hover { color: #ccc; }
.tab.active { color: #fff; border-bottom-color: #5cb8ff; }
.panel { display: none; }
.panel.active { display: block; }
.card { background: #1a1a24; border-radius: 12px; padding: 14px 20px; margin-bottom: 10px; }
.card a { color: #fff; text-decoration: none; font-size: 16px; font-weight: 600; display: block; }
.card a:hover { color: #5cb8ff; }
.card .dim { color: #666; font-size: 12px; margin-top: 2px; font-weight: 400; }
.empty { color: #555; font-style: italic; margin: 8px 0; }
.footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #2a2a3a; color: #555; font-size: 12px; text-align: center; }
"""

JS = """
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.panel');
function activate(name) {
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  panels.forEach(p => p.classList.toggle('active', p.dataset.tab === name));
  location.hash = name;
}
tabs.forEach(t => t.addEventListener('click', () => activate(t.dataset.tab)));
const initial = location.hash.replace('#','') || 'world';
activate(tabs[0]?.dataset.tab && document.querySelector(`.tab[data-tab="${initial}"]`) ? initial : 'world');
"""

out = [f"""<!DOCTYPE html>
<html lang="ru"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Дайджест</title>
<style>{CSS}</style>
</head><body>
<h1>Дайджест</h1>
<div class="sub">Ежедневные сводки · мир, AI, X-таймлайны, HN, Product Hunt, GitHub Trending</div>
<div class="tabs">"""]

for tab, title in TABS:
    out.append(f'  <button class="tab" data-tab="{tab}">{html.escape(title)}</button>')
out.append('</div>')

for tab, title in TABS:
    out.append(f'<div class="panel" data-tab="{tab}">')
    items = data[tab]
    if not items:
        out.append('  <div class="empty">пока пусто</div>')
    else:
        for date_str in items:
            out.append(f'  <div class="card"><a href="{tab}/{date_str}.html">{pretty(date_str)}</a><div class="dim">{date_str}</div></div>')
    out.append('</div>')

out.append(f'<div class="footer">aitherlab-dev/digest</div>')
out.append(f'<script>{JS}</script>')
out.append('</body></html>')

(ROOT / 'index.html').write_text('\n'.join(out), encoding='utf-8')
print(f"✓ index.html: " + ", ".join(f'{t}={len(data[t])}' for t,_ in TABS))
