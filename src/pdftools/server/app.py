"""FastAPI surface that reuses the core PDF primitives."""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
import uvicorn

from pdftools.core import merge_pdfs, split_pdf

app = FastAPI(title="pdfTools API", version="0.2.0")


def _write_uploads(files: List[UploadFile], temp_dir: Path) -> list[Path]:
    saved_paths: list[Path] = []
    for upload in files:
        destination = temp_dir / (upload.filename or "upload.pdf")
        with destination.open("wb") as handle:
            handle.write(upload.file.read())
        saved_paths.append(destination)
    return saved_paths


@app.post("/merge", response_class=FileResponse)
async def merge_endpoint(files: List[UploadFile] = File(...)) -> FileResponse:
    loop = asyncio.get_event_loop()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        saved = await loop.run_in_executor(None, _write_uploads, files, tmp_dir)
        destination = tmp_dir / "merged.pdf"
        await loop.run_in_executor(None, merge_pdfs, saved, destination)
        return FileResponse(destination, media_type="application/pdf", filename="merged.pdf")


@app.post("/split", response_class=FileResponse)
async def split_endpoint(
    file: UploadFile = File(...),
    ranges: str = Form("all"),
) -> FileResponse:
    loop = asyncio.get_event_loop()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        source = tmp_dir / (file.filename or "source.pdf")
        with source.open("wb") as handle:
            handle.write(file.file.read())
        output_dir = tmp_dir / "parts"
        output_dir.mkdir(parents=True, exist_ok=True)
        exported: list[Path] = await loop.run_in_executor(None, split_pdf, source, ranges, output_dir)
        archive = tmp_dir / "split.zip"
        await loop.run_in_executor(None, _zip_files, exported, archive)
        return FileResponse(archive, media_type="application/zip", filename="split_parts.zip")


def _zip_files(files: list[Path], destination: Path) -> Path:
    from zipfile import ZipFile

    with ZipFile(destination, "w") as archive:
        for path in files:
            archive.write(path, arcname=path.name)
    return destination


def run() -> None:
    uvicorn.run("pdftools.server.app:app", reload=False, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    run()
