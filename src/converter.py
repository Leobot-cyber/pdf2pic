"""PDF to image conversion using PyMuPDF."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import fitz
from PIL import Image

SUPPORTED_FORMATS = {
    "PNG": {"ext": "png", "needs_pillow": False},
    "JPEG": {"ext": "jpg", "needs_pillow": False},
    "BMP": {"ext": "bmp", "needs_pillow": True},
    "TIFF": {"ext": "tiff", "needs_pillow": True},
    "WEBP": {"ext": "webp", "needs_pillow": True},
    "GIF": {"ext": "gif", "needs_pillow": True},
}

ALL_PAGES_ALIASES = {"", "all", "全部", "*"}


@dataclass
class ConversionResult:
    pdf_path: Path
    output_files: list[Path]
    page_count: int


ProgressCallback = Callable[[str, int, int], None]


def parse_page_range(spec: str, total_pages: int) -> list[int]:
    """Parse page range string into 0-based page indices.

    Examples: "all", "1-5", "1,3,5", "2-4,7"
    """
    normalized = spec.strip().lower()
    if normalized in ALL_PAGES_ALIASES:
        return list(range(total_pages))

    indices: set[int] = set()
    for part in re.split(r"[,，]", normalized):
        part = part.strip()
        if not part:
            continue

        if re.fullmatch(r"\d+-\d+", part):
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s), int(end_s)
            if start > end:
                raise ValueError(f"invalid range '{part}'")
            for page in range(start, end + 1):
                indices.add(page - 1)
        elif re.fullmatch(r"\d+", part):
            indices.add(int(part) - 1)
        else:
            raise ValueError(f"invalid segment '{part}'")

    if not indices:
        raise ValueError("empty page range")

    for index in indices:
        if index < 0 or index >= total_pages:
            raise ValueError(f"page {index + 1} out of range 1-{total_pages}")

    return sorted(indices)


def count_pages_to_convert(pdf_paths: Iterable[Path], page_range: str | None) -> int:
    total = 0
    for pdf_path in pdf_paths:
        with fitz.open(pdf_path) as doc:
            if page_range:
                indices = parse_page_range(page_range, doc.page_count)
                total += len(indices)
            else:
                total += doc.page_count
    return total


def _save_pixmap(pix: fitz.Pixmap, output_path: Path, fmt: str) -> None:
    info = SUPPORTED_FORMATS[fmt.upper()]
    ext = info["ext"]

    if not info["needs_pillow"]:
        pix.save(str(output_path))
        return

    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    save_kwargs: dict = {}
    if fmt.upper() == "JPEG":
        save_kwargs["quality"] = 95
    elif fmt.upper() == "WEBP":
        save_kwargs["quality"] = 90
    img.save(str(output_path.with_suffix(f".{ext}")), format=fmt.upper(), **save_kwargs)


def convert_pdf(
    pdf_path: Path,
    output_dir: Path,
    image_format: str,
    dpi: int = 150,
    page_range: str | None = None,
    on_page: ProgressCallback | None = None,
) -> ConversionResult:
    fmt = image_format.upper()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {image_format}")

    ext = SUPPORTED_FORMATS[fmt]["ext"]
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = pdf_path.stem
    pdf_output_dir = output_dir / stem
    pdf_output_dir.mkdir(parents=True, exist_ok=True)

    output_files: list[Path] = []

    with fitz.open(pdf_path) as doc:
        page_indices = (
            parse_page_range(page_range, doc.page_count)
            if page_range
            else list(range(doc.page_count))
        )
        page_count = len(page_indices)
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        for progress_index, page_index in enumerate(page_indices, start=1):
            if on_page:
                on_page(pdf_path.name, progress_index, page_count)

            page = doc.load_page(page_index)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            output_path = pdf_output_dir / f"{stem}_page_{page_index + 1:04d}.{ext}"
            _save_pixmap(pix, output_path, fmt)
            output_files.append(output_path)

    return ConversionResult(pdf_path=pdf_path, output_files=output_files, page_count=page_count)


def convert_batch(
    pdf_paths: Iterable[Path],
    output_dir: Path,
    image_format: str,
    dpi: int = 150,
    page_range: str | None = None,
    on_file_start: Callable[[Path, int, int], None] | None = None,
    on_page: ProgressCallback | None = None,
) -> list[ConversionResult]:
    paths = list(pdf_paths)
    results: list[ConversionResult] = []

    for file_index, pdf_path in enumerate(paths, start=1):
        if on_file_start:
            on_file_start(pdf_path, file_index, len(paths))

        result = convert_pdf(
            pdf_path=pdf_path,
            output_dir=output_dir,
            image_format=image_format,
            dpi=dpi,
            page_range=page_range,
            on_page=on_page,
        )
        results.append(result)

    return results
