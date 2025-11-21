# Repository Guidelines

## Project Structure & Module Organization
pdfTools 2.0 keeps executable code inside `src/pdftools/`, split into small, purpose-driven packages. `src/pdftools/gui/` hosts the Tkinter desktop client (main entry `src/pdftools/gui/app.py`). `src/pdftools/ops/` collects pure PDF primitives (split/merge, metadata cleanup, compression) that can be reused by GUI actions, the CLI, or automated agents. Workflow managers such as the CLI runner and batch routines live in `src/pdftools/workflows/`. Shared fixtures, sample PDFs, and font assets stay in `assets/`, while release automation, PyInstaller specs, and helper scripts belong in `scripts/`. Tests mirror this layout: `tests/unit/gui/test_merge_panel.py` exercises widgets, and `tests/integration/test_cli_merge.py` validates flows end-to-end.

## Build, Test, and Development Commands
```
python -m venv .venv && source .venv/bin/activate  # create local env
pip install -e .[dev]                              # install runtime+dev extras
make gui                                           # run Tkinter app with autoreload
make cli ARGS="merge samples/invoice.pdf"          # execute CLI workflow
make lint                                          # black + ruff + mypy
make test                                          # pytest suite with coverage gate
make package                                       # build PyInstaller bundle in dist/
```
Run commands from repo root so paths resolve correctly; keep `.venv` and `dist/` out of git.

To start the desktop app without remembering the full command chain, run `bash scripts/run_gui.sh`. The script guards the virtual environment, installs editable deps on demand, and launches `pdftools.gui.main`.

## Core Features
- Merge multiple PDFs into one ordered document.
- Split a PDF into custom page ranges using expressions like `1-3,5`.
- Convert common image formats (PNG/JPG/BMP/WebP/TIFF) into a single multi-page PDF via the “照片转 PDF” tab.
- See `docs/photo_to_pdf_design.md` for the detailed design and execution plan behind the photo workflow.

## Coding Style & Naming Conventions
Target Python 3.11+, 4-space indentation, and exhaustive type hints on public APIs. Always format with `black` and address `ruff` warnings instead of silencing them. Classes use PascalCase, modules and functions stay in snake_case, and CLI flags adopt kebab-case (`--output-dir`). GUI resource identifiers follow `component_action` (e.g., `merge_button`). Prefer dataclasses for immutable configs and centralize logging through `pdftools.logging.get_logger()`.

## Testing Guidelines
Pytest drives both unit and integration checks. Name tests `test_<module>__<behavior>` so failures map directly to features. Unit tests should mock filesystem access and drop sample PDFs under `assets/fixtures/`. Integration tests run real merges/splits on lightweight PDFs; mark slower flows with `@pytest.mark.slow` and isolate them using `pytest -m "not slow"` during incremental work. Keep coverage ≥90% via `pytest --cov=src/pdftools --cov-report=term-missing` and fail builds when the gate is missed.

## Commit & Pull Request Guidelines
Use Conventional Commits (`feat:`, `fix:`, `chore:`) and keep each commit scoped to a single behavior change plus its tests. Rebase before opening PRs, include a short summary, linked issue, validation command list, and screenshots or sample PDFs whenever UI or rendering changes occur. Do not request review until lint/test/package targets are green, and ensure new modules include documentation or docstrings that explain agent-facing surfaces.
