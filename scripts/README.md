# Packaging

## Build the macOS `.app`

1. Create/activate a virtual environment (Python 3.11+ recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   pip install pyinstaller
   ```
2. From the repository root, run:
   ```bash
   pyinstaller scripts/pdftools_mac.spec
   ```
   The build artifacts land in `dist/`, producing `PDF Atelier.app`.

## Install on macOS

1. Open `dist` in Finder (`open dist`) and drag `PDF Atelier.app` to `/Applications` (or use `cp -R dist/PDF\ Atelier.app /Applications/`).
2. On first launch, macOS Gatekeeper may block the unsigned bundle. Right-click the app, choose *Open*, then confirm to trust it. For distribution, sign and notarize the bundle with your Apple Developer ID.

## Troubleshooting

- Ensure `assets/` ships with the bundle: the spec copies it at runtime. Update `scripts/pdftools_mac.spec` if you add new resource directories.
- If PyInstaller complains about PySide6 plugins, install the exact version pinned in `pyproject.toml` and delete any stale `build/` or `dist/` directories before rerunning.
