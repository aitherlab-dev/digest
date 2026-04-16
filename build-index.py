#!/usr/bin/env python3
"""Сборка index.html со списком всех дайджестов."""
import pathlib, html

MONTHS = {1:"января",2:"февраля",3:"марта",4:"апреля",5:"мая",6:"июня",7:"июля",8:"августа",9:"сентября",10:"октября",11:"ноября",12:"декабря"}

def pretty(date_str):
    y,m,d = date_str.split('-')
    return f"{int(d)} {MONTHS[int(m)]} {y}"

ROOT = pathlib.Path('/home/sasha/WORK/digest-repo')

def list_files(subdir):
    d = ROOT / subdir
    if not d.exists(): return []
    return sorted([p.stem for p in d.glob('*.html')], reverse=True)

daily = list_files('daily')
github = list_files('github')
x = list_files('x')

CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0f0f14; color: #e0e0e0; font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; }
h1 { color: #fff; font-size: 32px; margin-bottom: 8px; }
.sub { color: #888; font-size: 14px; margin-bottom: 32px; }
h2 { color: #fff; font-size: 22px; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 1px solid #2a2a3a; }
.card { background: #1a1a24; border-radius: 12px; padding: 14px 20px; margin-bottom: 10px; }
.card a { color: #fff; text-decoration: none; font-size: 16px; font-weight: 600; display: block; }
.card a:hover { color: #5cb8ff; }
.card .dim { color: #666; font-size: 12px; margin-top: 2px; font-weight: 400; }
.empty { color: #555; font-style: italic; margin: 8px 0; }
.footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #2a2a3a; color: #555; font-size: 12px; text-align: center; }
"""

out = [f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Дайджест — архив</title>
<style>{CSS}</style>
</head>
<body>
<h1>Дайджест</h1>
<div class="sub">Ежедневные сводки: мир, AI, Hacker News, Product Hunt, GitHub Trending</div>
"""]

def section(title, subdir, items):
    out.append(f'<h2>{title}</h2>')
    if not items:
        out.append('<div class="empty">пока пусто</div>')
        return
    for date_str in items:
        out.append(f'<div class="card"><a href="{subdir}/{date_str}.html">{pretty(date_str)}</a><div class="dim">{date_str}</div></div>')

section('Daily', 'daily', daily)
section('GitHub Trending', 'github', github)
section('X', 'x', x)

out.append('<div class="footer">aitherlab-dev/digest</div>')
out.append('</body></html>')

(ROOT / 'index.html').write_text('\n'.join(out), encoding='utf-8')
print(f"✓ index.html ({len(daily)} daily, {len(github)} github, {len(x)} x)")
