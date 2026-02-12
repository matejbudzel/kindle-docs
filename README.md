# Markdown to Kindle Formats (GitHub Pages)

This repository is set up to convert Markdown files in `markdown/` into EPUB, MOBI, and AZW files on every push to `main`.

## How it works

1. Add one or more `.md` files to `markdown/`.
2. Push to `main`.
3. GitHub Actions will:
   - install `pandoc` and `calibre`
   - convert each `markdown/*.md` file to `dist/<filename>.epub`
   - convert each generated EPUB to `dist/<filename>.mobi` and `dist/<filename>.azw`
   - generate `dist/index.html` with title names and direct links for all three formats
   - publish `dist/` to GitHub Pages using the official Pages deployment actions
The workflow runs only when files under `markdown/` change (or when the workflow file itself changes), plus manual runs via `workflow_dispatch`.

## Output

- EPUB, MOBI, and AZW files are generated in `dist/` during CI.
- `dist/` is intentionally ignored in git and is not committed.
- Published files are available on your GitHub Pages site:
  - `index.html` lists each title and provides links to `.epub`, `.mobi`, and `.azw`.

## Markdown tips

- File name determines output names: `markdown/my-book.md` -> `my-book.epub`, `my-book.mobi`, and `my-book.azw`
- EPUB builds include a Table of Contents (`--toc`) for Kindle navigation, then Calibre converts the EPUB to the Kindle-specific formats.
- Language metadata is set to `en-US`.
- Optional: if a Markdown file has YAML frontmatter with `title`, it is used as the display name in `index.html`.

Example frontmatter:

```md
---
title: My Book Title
---

# Chapter 1
...
```
