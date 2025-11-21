"""Application entry point for the desktop client."""
from __future__ import annotations

import os
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow, apply_modern_palette


def configure_environment() -> None:
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")


def main() -> None:
    configure_environment()
    app = QApplication(sys.argv)
    QGuiApplication.setOrganizationName("pdfTools")
    QGuiApplication.setApplicationName("PDF Atelier")
    apply_modern_palette(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
