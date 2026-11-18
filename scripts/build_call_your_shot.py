#!/usr/bin/env python3
"""Build /call-your-shot/ from call-your-shot/shots.json.

Each shot: "called" and "due" (YYYY-MM-DD), "shot", "why", and an optional
"status" (null while open). Newest called date first. Only Nathan's own
shots belong in this file.

    python3 scripts/build_call_your_shot.py
"""
from __future__ import annotations

import json
from pathlib import Path

from build_speaking import (
    ICON,
    MASTHEAD,
    SITE,
    THEME_BUTTON,
    chrome_close,
    esc,
    full_date,
    tabs,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "call-your-shot" / "shots.json"
OUT = ROOT / "call-your-shot" / "index.html"
REQUIRED = ("called", "due", "shot", "why")


def load() -> list[dict]:
    shots = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(shots, list):
        raise SystemExit("shots.json must be a list")
    for i, s in enumerate(shots):
        for key in REQUIRED:
            if not str(s.get(key) or "").strip():
                raise SystemExit(f"shot {i} is missing {key}")
        full_date(s["called"])
        full_date(s["due"])
    return sorted(shots, key=lambda s: (s["called"], s["due"]), reverse=True)


def page_head(title: str, description: str, path: str) -> str:
    url = f"{SITE}{path}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Nathan Colestock">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{SITE}/avatar.jpg">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{SITE}/avatar.jpg">
<meta name="theme-color" content="#4C5A2B">
<link rel="icon" type="image/svg+xml" href="{ICON}">
<title>{esc(title)} — Nathan Colestock</title>
<link rel="stylesheet" href="/style.css">
</head>"""


def entry(s: dict) -> str:
    status = ""
    if s.get("status"):
        status = (
            '\n          <div class="shot-row"><dt>Status</dt>'
            f'<dd>{esc(s["status"])}</dd></div>'
        )
    return f"""      <li class="shot">
        <dl class="shot-fields">
          <div class="shot-row"><dt>Called</dt><dd><time datetime="{esc(s["called"])}">{esc(full_date(s["called"]))}</time></dd></div>
          <div class="shot-row"><dt>Must be true by</dt><dd><time datetime="{esc(s["due"])}">{esc(full_date(s["due"]))}</time></dd></div>
          <div class="shot-row"><dt>Shot</dt><dd>{esc(s["shot"])}</dd></div>
          <div class="shot-row"><dt>Why</dt><dd>{esc(s["why"])}</dd></div>{status}
        </dl>
      </li>"""


def items(shots: list[dict]) -> str:
    years = {s["called"][:4] for s in shots}
    show_years = len(years) > 1
    blocks: list[str] = []
    open_year = None
    for s in shots:
        year = s["called"][:4]
        if show_years and year != open_year:
            open_year = year
            blocks.append(
                f'      <li class="shot-year"><h2 class="shot-year-label">{esc(year)}</h2></li>'
            )
        blocks.append(entry(s))
    return "\n".join(blocks)


def page(shots: list[dict]) -> str:
    description = (
        "Nathan Colestock’s called shots, with the date each was called "
        "and the date it must be true."
    )
    return f"""{page_head("Call Your Shot", description, "/call-your-shot/")}
<body>
<div id="mapbg" aria-hidden="true"></div>
{THEME_BUTTON}
<main class="view active" id="view-shots">
  <div class="shell">
{MASTHEAD}
{tabs("Call Your Shot")}
    <section class="shots" aria-label="Call Your Shot">
    <ul class="shot-list">
{items(shots)}
    </ul>
    </section>
    <footer class="home-foot">© 2026 Nathan Colestock</footer>
  </div>
</main>
{chrome_close()}"""


def main() -> None:
    shots = load()
    OUT.write_text(page(shots), encoding="utf-8")
    print(f"wrote {len(shots)} shot(s) to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
