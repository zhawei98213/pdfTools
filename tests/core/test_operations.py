from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

from pdftools.core.operations import convert_images_to_pdf


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
