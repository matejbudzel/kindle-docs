#!/usr/bin/env python3
from __future__ import annotations

import argparse
import mimetypes
import posixpath
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


IMAGE_SUFFIXES = {".apng", ".avif", ".gif", ".jpeg", ".jpg", ".png", ".webp"}


def find_magick() -> list[str]:
    magick = shutil.which("magick")
    if magick:
        return [magick]

    convert = shutil.which("convert")
    if convert:
        return [convert]

    raise RuntimeError("ImageMagick is required: install the 'imagemagick' package")


def convert_image(magick_cmd: list[str], source: Path, target: Path, max_size: int, quality: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            *magick_cmd,
            str(source),
            "-auto-orient",
            "-background",
            "white",
            "-alpha",
            "remove",
            "-alpha",
            "off",
            "-resize",
            f"{max_size}x{max_size}>",
            "-colorspace",
            "Gray",
            "-ordered-dither",
            "o8x8,6",
            "-strip",
            "-quality",
            str(quality),
            str(target),
        ],
        check=True,
    )


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def rewrite_file_references(root: Path, replacements: dict[str, str]) -> None:
    if not replacements:
        return

    text_suffixes = {".html", ".htm", ".xhtml", ".xml", ".opf", ".ncx", ".css"}
    for file in root.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in text_suffixes:
            continue

        try:
            content = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        updated = content
        file_dir = relative_posix(file.parent, root)
        for old, new in replacements.items():
            old_relative = posixpath.relpath(old, start=file_dir)
            new_relative = posixpath.relpath(new, start=file_dir)
            updated = updated.replace(old, new)
            updated = updated.replace(old_relative, new_relative)
            updated = updated.replace(old.replace("/", "%2F"), new.replace("/", "%2F"))
            updated = updated.replace(old_relative.replace("/", "%2F"), new_relative.replace("/", "%2F"))

        if updated != content:
            file.write_text(updated, encoding="utf-8")


def write_epub(source_dir: Path, output_epub: Path) -> None:
    output_epub.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_epub, "w") as archive:
        mimetype = source_dir / "mimetype"
        if mimetype.exists():
            archive.write(mimetype, "mimetype", compress_type=zipfile.ZIP_STORED)

        for file in sorted(source_dir.rglob("*")):
            if not file.is_file() or file == mimetype:
                continue
            archive.write(file, relative_posix(file, source_dir), compress_type=zipfile.ZIP_DEFLATED)


def make_small_epub(input_epub: Path, output_epub: Path, max_size: int, quality: int) -> int:
    with tempfile.TemporaryDirectory(prefix="small-epub-") as tmp:
        root = Path(tmp)
        with zipfile.ZipFile(input_epub) as archive:
            archive.extractall(root)

        images = [
            file
            for file in sorted(root.rglob("*"))
            if file.is_file() and file.suffix.lower() in IMAGE_SUFFIXES
        ]
        if not images:
            return 0

        magick_cmd = find_magick()
        replacements: dict[str, str] = {}
        processed = 0
        for image in images:
            old_name = relative_posix(image, root)
            target = image.with_suffix(".small.jpg")
            convert_image(magick_cmd, image, target, max_size=max_size, quality=quality)
            image.unlink()

            replacements[old_name] = relative_posix(target, root)
            old_mime_type, _ = mimetypes.guess_type(image.name)
            new_mime_type, _ = mimetypes.guess_type(target.name)
            if old_mime_type and new_mime_type:
                replacements[old_mime_type] = new_mime_type
            processed += 1

        rewrite_file_references(root, replacements)
        write_epub(root, output_epub)
        return processed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an e-ink-friendly EPUB with smaller dithered grayscale images.")
    parser.add_argument("input_epub", type=Path)
    parser.add_argument("output_epub", type=Path)
    parser.add_argument("--max-size", type=int, default=160, help="Maximum image width/height in pixels.")
    parser.add_argument("--quality", type=int, default=65, help="JPEG quality for converted images.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    processed = make_small_epub(
        input_epub=args.input_epub,
        output_epub=args.output_epub,
        max_size=args.max_size,
        quality=args.quality,
    )

    if processed:
        print(f"Built {args.output_epub} with {processed} converted image(s)")
    else:
        print(f"No raster images found in {args.input_epub}; small EPUB not created")


if __name__ == "__main__":
    main()
