# digest

Ежедневные дайджесты: мир, AI, Hacker News, Product Hunt, GitHub Trending.

**Сайт:** https://aitherlab-dev.github.io/digest/

Структура:
- `daily/YYYY-MM-DD.html` — ежедневный дайджест
- `github/YYYY-MM-DD.html` — еженедельный GitHub Trending
- `x/YYYY-MM-DD.html` — X-дайджест
- `index.html` — список архивов
- `build-index.py` — пересобирает index.html по содержимому папок
- `md-to-html.py` — конвертер MD-архивов (используется для бэкфилла)

Генерируется автоматически скиллами Claude Code из `~/WORK/Workspace/.claude/skills/`.
