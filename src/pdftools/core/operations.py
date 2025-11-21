"""High-level PDF operations reused by GUI/CLI/server surfaces."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from pypdf import PdfReader, PdfWriter
from PIL import Image

from .ranges import parse_page_ranges


class PDFOperationError(RuntimeError):
    """Raised when a PDF operation fails."""


def normalize_paths(paths: Iterable[str | Path]) -> list[Path]:
    """Convert incoming paths to `Path` objects and ensure they exist."""

    resolved: list[Path] = []
    for value in paths:
        path = Path(value).expanduser().resolve()
        resolved.append(path)
    return resolved


def merge_pdfs(files: Sequence[str | Path], output_path: str | Path) -> Path:
    """Merge the given PDF files into ``output_path`` and return the destination path."""

    pdf_paths = normalize_paths(files)
    if not pdf_paths:
        raise ValueError("At least one PDF must be supplied for merging.")

    writer = PdfWriter()
    for pdf in pdf_paths:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)

    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        writer.write(handle)
    return destination


def split_pdf(source: str | Path, ranges_expr: str, output_dir: str | Path) -> list[Path]:
    """Split ``source`` PDF into ``output_dir`` based on ``ranges_expr``.

    Returns a list of generated file paths.
    """

    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    reader = PdfReader(source_path)
    ranges = parse_page_ranges(ranges_expr, len(reader.pages))

    destination_dir = Path(output_dir).expanduser().resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)

    exported: list[Path] = []
    base_name = source_path.stem
    for index, (start, end) in enumerate(ranges, start=1):
        writer = PdfWriter()
        for page_index in range(start - 1, end):
            writer.add_page(reader.pages[page_index])

        suffix = f"{start:02d}" if start == end else f"{start:02d}-{end:02d}"
        destination = destination_dir / f"{base_name}_part{index:02d}_{suffix}.pdf"
        with destination.open("wb") as handle:
            writer.write(handle)
        exported.append(destination)

    return exported


def convert_images_to_pdf(images: Sequence[str | Path], output_path: str | Path) -> Path:
    """Convert one or more images into a single multi-page PDF.

    The order of ``images`` controls their page order inside the PDF.
    """

    image_paths = normalize_paths(images)
    if not image_paths:
        raise ValueError("至少需要选择一张图片。")

    prepared: list[Image.Image] = []
    for image_path in image_paths:
        with Image.open(image_path) as img:
            prepared.append(_prepare_for_pdf(img))

    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    first, *rest = prepared
    # Pillow writes the first page explicitly; append_images adds subsequent pages in order.
    first.save(destination, "PDF", save_all=True, append_images=rest, resolution=300.0)
    for image in prepared:
        image.close()
    return destination


def _prepare_for_pdf(image: Image.Image) -> Image.Image:
    """Ensure the PIL image is RGB with no alpha channel for PDF export."""

    if image.mode in ("RGBA", "LA"):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        composited = Image.alpha_composite(background, rgba)
        return composited.convert("RGB")

    if image.mode == "P":
        return image.convert("RGB")

    if image.mode != "RGB":
        return image.convert("RGB")

    return image.copy()
