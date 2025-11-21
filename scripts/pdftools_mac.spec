# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec that builds the PDF Atelier GUI as a standalone macOS .app.

Usage (from repository root):
    pyinstaller scripts/pdftools_mac.spec
"""
from __future__ import annotations

from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
src_dir = project_root / "src"
assets_dir = project_root / "assets"

datas = []
if assets_dir.exists():
    datas.append((str(assets_dir), "assets"))

block_cipher = None

a = Analysis(
    ["src/pdftools/gui/main.py"],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher, name="pdftools.pyz")

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="pdftools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name="PDF Atelier.app",
    icon=None,
    bundle_identifier="com.pdftools.atelier",
    info_plist=None,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
