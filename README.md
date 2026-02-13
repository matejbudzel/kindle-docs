# Markdown to Kindle Formats (GitHub Pages)

This repository is set up to convert Markdown files in `markdown/` into EPUB, MOBI, and AZW3 files on every push to `main`.

## How it works

1. Add one or more `.md` files to `markdown/`.
2. Push to `main`.
3. GitHub Actions will:
   - install `pandoc` and `calibre`
   - convert each `markdown/*.md` file to `dist/<filename>.epub`
   - convert each generated EPUB to `dist/<filename>.mobi` and `dist/<filename>.azw3`
   - generate `dist/index.html` with title names and direct links for all three formats
   - publish `dist/` to GitHub Pages using the official Pages deployment actions
The workflow runs only when files under `markdown/` change (or when the workflow file itself changes), plus manual runs via `workflow_dispatch`.

## Output

- EPUB, MOBI, and AZW3 files are generated in `dist/` during CI.
- `dist/` is intentionally ignored in git and is not committed.
- Published files are available on your GitHub Pages site:
  - `index.html` lists each title and provides links to `.epub`, `.mobi`, and `.azw3`.

## Web-based Codex setup

If you want the same converter toolchain available in a web-based Codex environment, run:

```bash
./scripts/setup_codex_env.sh
```

Optional environment variables:

- `PYTHON_VERSION` (default `3.12`): Python version to install/pin with `uv`
- `INSTALL_PYTHON` (default `1`): set to `0` to skip `uv` Python installation

The script installs the same core conversion dependencies used in CI (`pandoc` + `calibre`) and verifies the resulting toolchain.

## Markdown tips

- File name determines output names: `markdown/my-book.md` -> `my-book.epub`, `my-book.mobi`, and `my-book.azw3`
- EPUB builds include a Table of Contents (`--toc`) for Kindle navigation, then Calibre converts the EPUB to the Kindle-specific formats.
- `\newpage` directives in Markdown are converted to EPUB page breaks via `scripts/epub_pagebreak.lua`.
- Language metadata is set to `en-US`.
- EPUB output includes `styles/ebook.css` to keep heading/paragraph spacing compact where supported.
- Optional: if a Markdown file has YAML frontmatter with `title`, it is used as the display name in `index.html`.

Example frontmatter:

```md
---
title: My Book Title
---

# Chapter 1
...
```
