"""Main PySide6 window delivering native-feeling UX."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QStatusBar, QTabWidget

from pdftools.core import convert_images_to_pdf, merge_pdfs, split_pdf
from pdftools.gui.panels import MergePanel, PhotoToPDFPanel, SplitPanel
from pdftools.services.tasks import TaskRunner


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Atelier 2.0")
        self.setMinimumSize(960, 640)
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.setWindowIcon(QIcon())

        self.runner = TaskRunner()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)

        self.merge_panel = MergePanel()
        self.split_panel = SplitPanel()
        self.photo_panel = PhotoToPDFPanel()
        self.tabs.addTab(self.merge_panel, "合并")
        self.tabs.addTab(self.split_panel, "拆分")
        self.tabs.addTab(self.photo_panel, "照片转 PDF")

        self.merge_panel.merge_requested.connect(self._handle_merge)
        self.merge_panel.status_message.connect(self.status_bar.showMessage)
        self.split_panel.split_requested.connect(self._handle_split)
        self.split_panel.status_message.connect(self.status_bar.showMessage)
        self.photo_panel.convert_requested.connect(self._handle_photo_convert)
        self.photo_panel.status_message.connect(self.status_bar.showMessage)

    # ------------------------------------------------------------------ Ops
    def _handle_merge(self, files: list[str], output: str) -> None:
        self.merge_panel.set_running(True)
        self.status_bar.showMessage("正在合并 PDF…")
        self.runner.run(
            merge_pdfs,
            files,
            output,
            on_finished=lambda path: self._merge_finished(path),
            on_failed=lambda error: self._task_failed(error, self.merge_panel),
        )

    def _handle_split(self, source: str, ranges: str, output_dir: str) -> None:
        self.split_panel.set_running(True)
        self.status_bar.showMessage("正在拆分 PDF…")
        self.runner.run(
            split_pdf,
            source,
            ranges,
            output_dir,
            on_finished=lambda paths: self._split_finished(paths),
            on_failed=lambda error: self._task_failed(error, self.split_panel),
        )

    def _handle_photo_convert(
        self, images: list[str], output: str, normalize: bool, clean_handwriting: bool
    ) -> None:
        self.photo_panel.set_running(True)
        self.status_bar.showMessage("正在生成 PDF…")
        self.runner.run(
            convert_images_to_pdf,
            images,
            output,
            normalize_sizes=normalize,
            clean_handwriting=clean_handwriting,
            on_finished=lambda path: self._photo_convert_finished(path),
            on_failed=lambda error: self._task_failed(error, self.photo_panel),
        )

    def _merge_finished(self, path: Path) -> None:
        self.merge_panel.set_running(False)
        self.status_bar.showMessage("合并完成。")
        QMessageBox.information(self, "合并成功", f"文件已保存到\n{path}")

    def _split_finished(self, paths: list[Path]) -> None:
        self.split_panel.set_running(False)
        self.split_panel.show_outputs(paths)
        self.status_bar.showMessage(f"拆分完成，共导出 {len(paths)} 个文件。")
        QMessageBox.information(self, "拆分成功", f"导出 {len(paths)} 个 PDF。")

    def _photo_convert_finished(self, path: Path) -> None:
        self.photo_panel.set_running(False)
        self.status_bar.showMessage("图片已转换为 PDF。")
        QMessageBox.information(self, "转换成功", f"文件已保存到\n{path}")

    def _task_failed(self, error: str, panel) -> None:
        panel.set_running(False)
        self.status_bar.showMessage("操作失败。")
        QMessageBox.critical(self, "出错了", error)


def apply_modern_palette(app: QApplication) -> None:
    from PySide6.QtGui import QPalette

    app.setStyle("fusion")
    palette = app.palette()
    for role, factor in (
        (QPalette.ColorRole.Window, 110),
        (QPalette.ColorRole.Base, 102),
        (QPalette.ColorRole.Button, 108),
    ):
        palette.setColor(role, palette.color(role).lighter(factor))
    app.setPalette(palette)
