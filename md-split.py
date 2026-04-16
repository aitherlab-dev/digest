#!/usr/bin/env python3
"""Разбивает старый монолитный MD-дайджест на несколько HTML по разделам."""
import re, html, pathlib

MONTHS = {1:"января",2:"февраля",3:"марта",4:"апреля",5:"мая",6:"июня",7:"июля",8:"августа",9:"сентября",10:"октября",11:"ноября",12:"декабря"}

# Маппинг MD-секций → таб сайта
MAP = {
    'Мир': 'world',
    'Культура и кино': 'world',
    'AI и технологии': 'ai',
    'AI и Tech': 'ai',
    'Anthropic и Claude Code': 'ai',  # объединяем "Claude Code + AI" как хочет пользователь
    'Hacker News': 'ph-hn',
    'Product Hunt': 'ph-hn',
    'GitHub Trending': 'github',
}

TAB_TITLES = {
    'world': 'Мир',
    'ai': 'Claude Code + AI',
    'ph-hn': 'PH + HN',
    'github': 'GitHub Trending',
    'x': 'X таймлайны',
    'claude-code': 'Claude Code',
}

CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0f0f14; color: #e0e0e0; font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; }
h1 { color: #fff; font-size: 28px; margin-bottom: 8px; }
.date { color: #888; font-size: 14px; margin-bottom: 32px; }
h2 { color: #fff; font-size: 22px; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 1px solid #2a2a3a; }
.card { background: #1a1a24; border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; }
.card-title { font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 6px; }
.card-desc { font-size: 14px; color: #b0b0b0; margin-bottom: 8px; }
.card-meta { font-size: 12px; color: #666; }
.card-meta a { color: #5cb8ff; text-decoration: none; }
.card-meta a:hover { text-decoration: underline; }
.home-link { display: inline-block; margin-bottom: 20px; color: #5cb8ff; text-decoration: none; font-size: 14px; }
.home-link:hover { text-decoration: underline; }
.footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #2a2a3a; color: #555; font-size: 12px; text-align: center; }
"""

def md_link(s):
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{html.escape(m.group(2))}">{html.escape(m.group(1))}</a>', s)

def items_from_section(lines):
    """Парсит пункты ### внутри секции → список (title, desc, source_html)."""
    items = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith('### '):
            title = re.sub(r'^\d+\.\s*', '', line[4:].strip())
            desc_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('### '):
                if lines[i].strip():
                    desc_lines.append(lines[i].rstrip())
                i += 1
            source = ''
            if desc_lines and re.match(r'^\s*\[.+\]\(http', desc_lines[-1]):
                source = md_link(desc_lines[-1])
                desc_lines = desc_lines[:-1]
            desc = md_link(' '.join(desc_lines))
            items.append((title, desc, source))
        elif line.startswith('- ['):  # GitHub trending list items
            items.append(('', md_link(line[2:]), ''))
            i += 1
        else:
            i += 1
    return items

def parse_md(md_path):
    """Читает MD, возвращает dict {tab: [(original_section, items)]}"""
    with open(md_path, encoding='utf-8') as f:
        lines = f.read().splitlines()
    # split by ##
    sections = {}
    i = 0
    while i < len(lines) and not lines[i].startswith('## '):
        i += 1
    while i < len(lines):
        if lines[i].startswith('## '):
            name = lines[i][3:].strip()
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith('## '):
                body.append(lines[i])
                i += 1
            sections[name] = items_from_section(body)
        else:
            i += 1
    # group by tab
    tabs = {}
    for sec, items in sections.items():
        tab = MAP.get(sec)
        if not tab: continue
        tabs.setdefault(tab, []).append((sec, items))
    return tabs

def render_page(tab, date_str, sections):
    y,m,d = date_str.split('-')
    pretty = f"{int(d)} {MONTHS[int(m)]} {y}"
    out = [f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TAB_TITLES[tab]} — {pretty}</title>
<style>{CSS}</style></head><body>
<a href="../index.html" class="home-link">← Все дайджесты</a>
<h1>{TAB_TITLES[tab]}</h1>
<div class="date">{pretty}</div>"""]
    for sec_name, items in sections:
        out.append(f'<h2>{html.escape(sec_name)}</h2>')
        for idx, (title, desc, src) in enumerate(items, 1):
            out.append('<div class="card">')
            if title:
                out.append(f'  <div class="card-title">{idx}. {html.escape(title)}</div>')
            if desc:
                out.append(f'  <div class="card-desc">{desc}</div>')
            if src:
                out.append(f'  <div class="card-meta">{src}</div>')
            out.append('</div>')
    out.append(f'<div class="footer">{pretty}</div>')
    out.append('</body></html>')
    return '\n'.join(out)

ROOT = pathlib.Path('/home/sasha/WORK/digest-repo')
SRC = pathlib.Path('/home/sasha/WORK/NEWS')

for date_str in ['2026-04-14', '2026-04-15', '2026-04-16']:
    md = SRC / f'daily-{date_str}.md'
    if not md.exists(): continue
    tabs = parse_md(md)
    for tab, secs in tabs.items():
        d = ROOT / tab
        d.mkdir(exist_ok=True)
        out = d / f'{date_str}.html'
        out.write_text(render_page(tab, date_str, secs), encoding='utf-8')
        print(f"✓ {tab}/{date_str}.html")
