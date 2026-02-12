#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import os
from pathlib import Path
from typing import Dict

OUTPUT_EXTENSIONS = ("epub", "mobi", "azw")


def format_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"

    kib = num_bytes / 1024
    if kib < 1024:
        return f"{kib:.1f} KB"

    mib = kib / 1024
    return f"{mib:.2f} MB"


def parse_frontmatter_title(markdown_file: Path) -> str | None:
    try:
        content = markdown_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            break

        if line.lower().startswith("title:"):
            _, value = line.split(":", 1)
            title = value.strip().strip('"\'')
            return title or None

    return None


def collect_titles(markdown_dir: Path) -> Dict[str, str]:
    titles: Dict[str, str] = {}
    for md_file in sorted(markdown_dir.glob("*.md"), key=lambda p: p.name.lower()):
        title = parse_frontmatter_title(md_file)
        if title:
            titles[md_file.stem] = title
    return titles


def render_index(dist_dir: Path, markdown_dir: Path, out_file: Path) -> None:
    titles = collect_titles(markdown_dir)
    markdown_files = sorted(markdown_dir.glob("*.md"), key=lambda p: p.name.lower())

    build_timestamp = os.getenv("BUILD_TIMESTAMP_UTC") or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    commit_sha = os.getenv("GITHUB_SHA", "unknown")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")
    server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    run_url = os.getenv("GITHUB_RUN_URL")
    if not run_url and run_id and repository:
        run_url = f"{server_url}/{repository}/actions/runs/{run_id}"

    rows = []
    for markdown_file in markdown_files:
        stem = markdown_file.stem
        name = titles.get(stem, stem)
        links = []

        for ext in OUTPUT_EXTENSIONS:
            generated_file = dist_dir / f"{stem}.{ext}"
            if generated_file.exists():
                size = format_size(generated_file.stat().st_size)
                links.append(
                    f'<a href="{html.escape(generated_file.name)}" download>{html.escape(ext.upper())}</a>'
                    f" ({html.escape(size)})"
                )
            else:
                links.append(f"{html.escape(ext.upper())} (missing)")

        rows.append(
            "<li>"
            f"<strong>{html.escape(name)}</strong>"
            f" — {' | '.join(links)}"
            "</li>"
        )

    list_markup = "\n      ".join(rows) if rows else "<li>No markdown files were found in this build.</li>"

    run_link = (
        f'<a href="{html.escape(run_url)}">{html.escape(run_id)}</a>' if run_url and run_id else "Unavailable"
    )

    page = f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Kindle Download Formats</title>
  </head>
  <body>
    <h1>Kindle Download Formats</h1>
    <p>Each title includes links to EPUB, MOBI, and AZW files.</p>

    <h2>Files</h2>
    <ul>
      {list_markup}
    </ul>

    <h2>Build Metadata</h2>
    <ul>
      <li>Build timestamp (UTC): {html.escape(build_timestamp)}</li>
      <li>Commit SHA: <code>{html.escape(commit_sha)}</code></li>
      <li>Actions run: {run_link}</li>
    </ul>
  </body>
</html>
"""

    out_file.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    dist_dir = Path("dist")
    markdown_dir = Path("markdown")
    out_file = dist_dir / "index.html"

    dist_dir.mkdir(parents=True, exist_ok=True)
    render_index(dist_dir=dist_dir, markdown_dir=markdown_dir, out_file=out_file)
