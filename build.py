#!/usr/bin/env python3
"""Собрать Гиря.html из programs.json.

Как менять GIF:
1. Открой programs.json
2. В поле "gif" у нужного упражнения укажи:
   - ссылку из интернета: https://.../exercise.gif
   - или свой файл: gifs/мой-gif.gif
3. Запусти: python3 build.py
"""

from __future__ import annotations

import base64
import json
import html as H
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROGRAMS_FILE = ROOT / "programs.json"
OUT_HTML = ROOT / "Гиря.html"
OUT_ZIP = ROOT / "Гиря.zip"
GIF_CACHE = ROOT / ".gif-cache"


def esc(s: object) -> str:
    return H.escape(str(s))


def load_gif_bytes(gif_value: str) -> bytes:
    if gif_value.startswith("data:image"):
        # уже встроенный base64 — оставить как есть, не перекачивать
        header, b64 = gif_value.split(",", 1)
        return base64.b64decode(b64)

    path = Path(gif_value)
    if not path.is_absolute():
        path = ROOT / path

    if path.exists():
        return path.read_bytes()

    if gif_value.startswith(("http://", "https://")):
        cache_name = gif_value.rsplit("/", 1)[-1]
        GIF_CACHE.mkdir(exist_ok=True)
        cache_path = GIF_CACHE / cache_name
        if not cache_path.exists():
            print(f"  скачиваю {gif_value}")
            req = urllib.request.Request(gif_value, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                cache_path.write_bytes(resp.read())
        return cache_path.read_bytes()

    raise FileNotFoundError(f"GIF не найден: {gif_value}")


def to_data_uri(data: bytes) -> str:
    return "data:image/gif;base64," + base64.b64encode(data).decode("ascii")


def load_icon_data_uri() -> str:
    icon = ROOT / "gifs" / "icon-180.png"
    if not icon.exists():
        return ""
    b64 = base64.b64encode(icon.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def build_html(programs: list) -> str:
    icon_uri = load_icon_data_uri()
    icon_link = (
        f'<link rel="apple-touch-icon" href="{icon_uri}">\n'
        f'<link rel="icon" type="image/png" href="{icon_uri}">'
        if icon_uri
        else ""
    )

    tabs_inputs = []
    tabs_labels = []
    panels = []

    for i, p in enumerate(programs):
        checked = " checked" if i == 0 else ""
        tabs_inputs.append(
            f'<input class="tab-input" type="radio" name="prog" id="tab-{p["id"]}"{checked}>'
        )
        tabs_labels.append(
            f'<label class="tab" for="tab-{p["id"]}">{esc(p["badge"])}: {esc(p["title"].split()[0])}</label>'
        )

        sections_html = []
        for s in p["sections"]:
            items = []
            for ex in s["exercises"]:
                chips = []
                if ex.get("reps"):
                    chips.append(f'повторы: {ex["reps"]}')
                if ex.get("rounds"):
                    chips.append(f'подходы: {ex["rounds"]}')
                if ex.get("rest"):
                    chips.append(f'отдых: {ex["rest"]}')
                if ex.get("equipment"):
                    chips.append(ex["equipment"])
                chips_html = "".join(f'<span class="chip">{esc(c)}</span>' for c in chips)

                items.append(
                    f"""
<details class="ex">
  <summary>
    <span class="ex-num">{esc(ex["num"])}</span>
    <span class="ex-text">
      <span class="ex-name">{esc(ex["name"])}</span>
      <span class="ex-meta">{esc(ex["reps"])} · {esc(ex["equipment"])}</span>
    </span>
    <span class="ex-hint">GIF ▼</span>
  </summary>
  <div class="ex-body">
    <div class="gif-frame"><img src="{ex["gif"]}" alt="{esc(ex["name"])}" loading="lazy"></div>
    <div class="chips">{chips_html}</div>
    <p class="tech"><strong>Техника:</strong> {esc(ex.get("technique") or "")}</p>
    <p class="goal"><strong>Цель:</strong> {esc(ex.get("goal") or "")}</p>
  </div>
</details>"""
                )

            sections_html.append(
                f"""
<section class="section">
  <h3 class="section-title">{esc(s["title"])}</h3>
  <div class="list">{"".join(items)}</div>
</section>"""
            )

        panels.append(
            f"""
<div class="panel" id="panel-{p["id"]}">
  <div class="program-head">
    <h2>{esc(p["title"])}</h2>
    <p>{esc(p["subtitle"])}</p>
  </div>
  {"".join(sections_html)}
</div>"""
        )

    show_rules = []
    for p in programs:
        show_rules.append(
            f'#tab-{p["id"]}:checked ~ .tabs label[for="tab-{p["id"]}"] {{ background: var(--ink); color: #f7fbf8; }}'
        )
        show_rules.append(f'#tab-{p["id"]}:checked ~ #panel-{p["id"]} {{ display: block; }}')

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Гиря">
<meta name="mobile-web-app-capable" content="yes">
<title>Гиря</title>
{icon_link}
<style>
:root {{
  --bg0:#dfe8e2; --bg1:#f3f7f4; --ink:#14201b; --muted:#5a6b63;
  --line:rgba(20,32,27,.12); --accent:#0b6e4f;
  --surface:rgba(255,255,255,.78); --shadow:0 14px 40px rgba(20,32,27,.12);
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  color:var(--ink);
  background:
    radial-gradient(800px 420px at 8% -8%, rgba(11,110,79,.18), transparent 60%),
    radial-gradient(600px 360px at 100% 0%, rgba(240,162,2,.15), transparent 55%),
    linear-gradient(165deg,var(--bg0),var(--bg1) 50%, #e7eee9);
  min-height:100vh;
}}
.wrap {{ width:min(980px, calc(100% - 1.5rem)); margin:0 auto; padding:1rem 0 3rem; }}
.hero {{ display:grid; gap:.85rem; padding:1rem 0 1.4rem; }}
.brand {{
  margin:0; font-size:clamp(3.2rem, 14vw, 5.5rem); font-weight:800;
  letter-spacing:-.04em; line-height:.9;
  background:linear-gradient(120deg,var(--ink) 40%, var(--accent));
  -webkit-background-clip:text; background-clip:text; color:transparent;
}}
.hero h1 {{
  margin:0; font-size:clamp(1.15rem, 3.5vw, 1.55rem); font-weight:700; max-width:18ch; line-height:1.25;
}}
.hero p {{ margin:0; color:var(--muted); max-width:40ch; line-height:1.45; }}
.tip {{
  display:inline-block; margin-top:.2rem; padding:.55rem .9rem;
  border-radius:999px; background:rgba(11,110,79,.12); color:var(--accent);
  font-size:.9rem; font-weight:700;
}}
.programs {{ margin-top:.5rem; }}
.tab-input {{ position:absolute; opacity:0; pointer-events:none; }}
.tabs {{
  display:flex; gap:.4rem; flex-wrap:wrap; margin:0 0 1rem;
  padding:.35rem; border:1px solid var(--line); border-radius:999px;
  background:rgba(243,247,244,.85);
}}
.tab {{
  padding:.7rem 1rem; border-radius:999px; cursor:pointer;
  color:var(--muted); font-weight:700; font-size:.92rem;
  -webkit-tap-highlight-color:transparent;
}}
.panel {{ display:none; }}
{chr(10).join(show_rules)}
.program-head h2 {{ margin:0 0 .3rem; font-size:clamp(1.25rem, 4vw, 1.8rem); }}
.program-head p {{ margin:0 0 1rem; color:var(--muted); }}
.section {{ margin-bottom:1.4rem; }}
.section-title {{
  margin:0 0 .7rem; color:var(--accent); text-transform:uppercase;
  letter-spacing:.04em; font-size:.85rem; font-weight:800;
}}
.list {{ display:grid; gap:.55rem; }}
.ex {{
  border:1px solid var(--line); border-radius:16px; background:var(--surface);
  overflow:hidden;
}}
.ex summary {{
  list-style:none; display:grid; grid-template-columns:auto 1fr auto;
  gap:.8rem; align-items:center; padding:.9rem 1rem; cursor:pointer;
  -webkit-tap-highlight-color:rgba(11,110,79,.15);
}}
.ex summary::-webkit-details-marker {{ display:none; }}
.ex[open] {{ box-shadow:var(--shadow); border-color:rgba(11,110,79,.35); }}
.ex[open] .ex-hint {{ color:var(--ink); }}
.ex-num {{
  width:2.1rem; height:2.1rem; border-radius:50%; display:grid; place-items:center;
  background:rgba(11,110,79,.12); color:var(--accent); font-weight:800;
}}
.ex-text {{ display:grid; gap:.15rem; min-width:0; }}
.ex-name {{ font-weight:700; font-size:1rem; }}
.ex-meta {{ color:var(--muted); font-size:.88rem; }}
.ex-hint {{ color:var(--accent); font-size:.78rem; font-weight:800; white-space:nowrap; }}
.ex-body {{ border-top:1px solid var(--line); }}
.gif-frame {{
  background:#101714; display:grid; place-items:center; min-height:220px;
}}
.gif-frame img {{
  width:100%; max-height:340px; object-fit:contain; display:block;
}}
.chips {{ display:flex; flex-wrap:wrap; gap:.35rem; padding:.9rem 1rem 0; }}
.chip {{
  font-size:.75rem; font-weight:700; padding:.3rem .6rem; border-radius:999px;
  background:rgba(11,110,79,.1); color:var(--accent);
}}
.tech, .goal {{
  margin:0; padding:.7rem 1rem 1rem; color:var(--muted); line-height:1.5; font-size:.95rem;
}}
.tech strong, .goal strong {{ color:var(--ink); }}
.goal {{ padding-top:0; }}
.footer-note {{ margin-top:1.5rem; color:var(--muted); font-size:.85rem; }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <p class="brand">Гиря</p>
    <h1>Программа с гирей — техника в один тап</h1>
    <p>Нажми на упражнение — раскроется GIF с правильным выполнением и ключевыми нюансами.</p>
    <span class="tip">Жми на упражнение ↓</span>
  </header>

  <main class="programs" id="programs">
    {"".join(tabs_inputs)}
    <div class="tabs">{"".join(tabs_labels)}</div>
    {"".join(panels)}
    <p class="footer-note">Один файл, без интернета и без Safari. Нажми упражнение — откроется GIF.</p>
  </main>
</div>
</body>
</html>
"""


def main() -> None:
    programs = json.loads(PROGRAMS_FILE.read_text(encoding="utf-8"))

    print("Вшиваю GIF...")
    for p in programs:
        for s in p["sections"]:
            for ex in s["exercises"]:
                name = ex["name"]
                src = ex["gif"]
                print(f"  • {name}")
                data = load_gif_bytes(src)
                ex["gif"] = to_data_uri(data)

    html = build_html(programs)
    OUT_HTML.write_text(html, encoding="utf-8")
    (ROOT / "index.html").write_text(html, encoding="utf-8")

    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(OUT_HTML, arcname="Гиря.html")

    size_mb = OUT_HTML.stat().st_size / 1024 / 1024
    print(f"\nГотово: {OUT_HTML.name} ({size_mb:.1f} МБ)")
    print(f"Архив: {OUT_ZIP.name}")


if __name__ == "__main__":
    main()
