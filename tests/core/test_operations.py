from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image, ImageDraw
from pypdf import PdfReader

from pdftools.core.operations import convert_images_to_pdf, remove_handwriting_marks


def create_sample_image(path: Path, color: tuple[int, int, int]) -> None:
    image = Image.new("RGB", (64, 64), color)
    image.save(path)


def test_convert_images_to_pdf__creates_pdf_from_images(tmp_path) -> None:
    image_one = tmp_path / "one.png"
    image_two = tmp_path / "two.png"
    create_sample_image(image_one, (255, 0, 0))
    create_sample_image(image_two, (0, 255, 0))

    output = tmp_path / "photos.pdf"
    result = convert_images_to_pdf([image_one, image_two], output)

    assert result == output
    assert output.exists()

    reader = PdfReader(output)
    assert len(reader.pages) == 2


def test_convert_images_to_pdf__requires_images(tmp_path) -> None:
    output = tmp_path / "photos.pdf"
    with pytest.raises(ValueError):
        convert_images_to_pdf([], output)


def test_convert_images_to_pdf__normalizes_page_size_when_requested(tmp_path) -> None:
    wide = tmp_path / "wide.png"
    tall = tmp_path / "tall.png"
    Image.new("RGB", (200, 100), (0, 0, 255)).save(wide)
    Image.new("RGB", (100, 200), (255, 255, 0)).save(tall)

    output = tmp_path / "normalized.pdf"
    convert_images_to_pdf([wide, tall], output, normalize_sizes=True)

    reader = PdfReader(output)
    assert len(reader.pages) == 2
    first_box = reader.pages[0].mediabox
    second_box = reader.pages[1].mediabox
    assert first_box.width == second_box.width
    assert first_box.height == second_box.height


def test_remove_handwriting_marks__lightens_dark_pixels() -> None:
    image = Image.new("RGB", (100, 100), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 40, 90, 60), fill=(10, 10, 10))

    cleaned = remove_handwriting_marks(image)
    center_pixel = cleaned.getpixel((50, 50))

    assert center_pixel[0] > 200
    assert center_pixel[1] > 200
    assert center_pixel[2] > 200
