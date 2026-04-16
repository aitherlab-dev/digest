#!/usr/bin/env python3
"""Конвертер md → html для дайджестов в едином тёмном стиле."""
import re, sys, html, pathlib

MONTHS = {1:"января",2:"февраля",3:"марта",4:"апреля",5:"мая",6:"июня",7:"июля",8:"августа",9:"сентября",10:"октября",11:"ноября",12:"декабря"}

CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0f0f14; color: #e0e0e0; font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; }
h1 { color: #fff; font-size: 28px; margin-bottom: 8px; }
.date { color: #888; font-size: 14px; margin-bottom: 32px; }
h2 { color: #fff; font-size: 22px; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 1px solid #2a2a3a; }
.card { background: #1a1a24; border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; }
.card-title { font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 6px; }
.card-title a { color: #fff; text-decoration: none; }
.card-title a:hover { text-decoration: underline; }
.card-desc { font-size: 14px; color: #b0b0b0; margin-bottom: 8px; }
.card-meta { font-size: 12px; color: #666; }
.card-meta a { color: #5cb8ff; text-decoration: none; }
.card-meta a:hover { text-decoration: underline; }
.home-link { display: inline-block; margin-bottom: 20px; color: #5cb8ff; text-decoration: none; font-size: 14px; }
.home-link:hover { text-decoration: underline; }
.footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #2a2a3a; color: #555; font-size: 12px; text-align: center; }
"""

def md_link(s):
    # [text](url) → <a>
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{html.escape(m.group(2))}">{html.escape(m.group(1))}</a>', s)

def convert(md_path, html_path, date_str):
    with open(md_path, encoding='utf-8') as f:
        md = f.read()

    y, m, d = date_str.split('-')
    date_pretty = f"{int(d)} {MONTHS[int(m)]} {y}"

    out = [f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Дайджест — {date_pretty}</title>
<style>{CSS}</style>
</head>
<body>
<a href="../index.html" class="home-link">← Все дайджесты</a>
<h1>Дайджест</h1>
<div class="date">{date_pretty}</div>
"""]

    # Parse MD: skip top # header, walk through lines
    lines = md.splitlines()
    i = 0
    # skip till first ##
    while i < len(lines) and not lines[i].startswith('## '):
        i += 1

    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith('## '):
            section = line[3:].strip()
            out.append(f'<h2>{html.escape(section)}</h2>')
            i += 1
        elif line.startswith('### '):
            # title line
            title_raw = line[4:].strip()
            # strip leading "N. "
            title_raw = re.sub(r'^\d+\.\s*', '', title_raw)
            # collect description lines until next ### or ## or EOF
            desc_lines = []
            i += 1
            while i < len(lines):
                nxt = lines[i].rstrip()
                if nxt.startswith('### ') or nxt.startswith('## '):
                    break
                if nxt:
                    desc_lines.append(nxt)
                i += 1
            # Split last line as source link if it looks like [text](url)
            source_html = ''
            if desc_lines and re.match(r'^\s*\[.+\]\(http', desc_lines[-1]):
                source_html = md_link(desc_lines[-1])
                desc_lines = desc_lines[:-1]
            desc_html = md_link(' '.join(desc_lines))
            out.append('<div class="card">')
            out.append(f'  <div class="card-title">{html.escape(title_raw)}</div>')
            if desc_html.strip():
                out.append(f'  <div class="card-desc">{desc_html}</div>')
            if source_html:
                out.append(f'  <div class="card-meta">{source_html}</div>')
            out.append('</div>')
        elif line.startswith('- ['):
            # github-style list items: - [name](url) — desc
            out.append('<div class="card">')
            # convert whole line
            content_html = md_link(line[2:])
            # split "text — desc" if present
            out.append(f'  <div class="card-desc">{content_html}</div>')
            out.append('</div>')
            i += 1
        else:
            i += 1

    out.append(f'<div class="footer">Собрано автоматически · {date_pretty}</div>')
    out.append('</body></html>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f"✓ {html_path}")

if __name__ == '__main__':
    src_dir = pathlib.Path('/home/sasha/WORK/NEWS')
    dst_dir = pathlib.Path('/home/sasha/WORK/digest-repo/daily')
    dst_dir.mkdir(parents=True, exist_ok=True)
    # Convert only md files that don't have matching html, OR pass all
    for md in sorted(src_dir.glob('daily-*.md')):
        date_str = md.stem.replace('daily-', '')
        out = dst_dir / f'{date_str}.html'
        convert(md, out, date_str)
