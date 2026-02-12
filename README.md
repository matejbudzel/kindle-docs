# Markdown to EPUB (GitHub Pages)

This repository is set up to convert Markdown files in `markdown/` into EPUB files on every push to `main`.

## How it works

1. Add one or more `.md` files to `markdown/`.
2. Push to `main`.
3. GitHub Actions will:
   - install `pandoc`
   - convert each `markdown/*.md` file to `dist/<filename>.epub`
   - generate `dist/index.html` with file names, sizes, and build metadata
   - publish `dist/` to GitHub Pages using the official Pages deployment actions

The workflow runs only when files under `markdown/` change (or when the workflow file itself changes), plus manual runs via `workflow_dispatch`.

## Output

- EPUB files are generated in `dist/` during CI.
- `dist/` is intentionally ignored in git and is not committed.
- Published files are available on your GitHub Pages site:
  - `index.html` lists all EPUB files and links directly to each `.epub`.

## Markdown tips

- File name determines output name: `markdown/my-book.md` -> `my-book.epub`
- EPUB builds include a Table of Contents (`--toc`) for Kindle navigation.
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
