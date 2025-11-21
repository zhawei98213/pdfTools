"""PySide6 widgets composing the desktop experience."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MergePanel(QWidget):
    merge_requested = Signal(list, str)
    status_message = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        header = QLabel("合并多个 PDF")
        header.setProperty("class", "h2")
        main_layout.addWidget(header)

        hint = QLabel("拖拽或添加文件，按期望顺序排列，然后选择输出路径。")
        hint.setWordWrap(True)
        main_layout.addWidget(hint)

        list_row = QHBoxLayout()
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.setAlternatingRowColors(True)
        self.file_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        list_row.addWidget(self.file_list)

        reorder_controls = QVBoxLayout()
        move_up = QPushButton("上移")
        move_up.clicked.connect(self.move_selected_up)
        reorder_controls.addWidget(move_up)

        move_down = QPushButton("下移")
        move_down.clicked.connect(self.move_selected_down)
        reorder_controls.addWidget(move_down)
        reorder_controls.addStretch(1)
        list_row.addLayout(reorder_controls)

        main_layout.addLayout(list_row)

        controls = QHBoxLayout()
        add_button = QPushButton("添加文件…")
        add_button.clicked.connect(self.add_files)
        controls.addWidget(add_button)

        remove_button = QPushButton("移除选中")
        remove_button.clicked.connect(self.remove_selected)
        controls.addWidget(remove_button)

        clear_button = QPushButton("清空列表")
        clear_button.clicked.connect(self.clear_list)
        controls.addWidget(clear_button)

        controls.addStretch(1)
        main_layout.addLayout(controls)

        form = QFormLayout()
        self.output_path = QLineEdit()
        browse = QPushButton("选择输出…")
        browse.clicked.connect(self.choose_output)
        container = QHBoxLayout()
        container.addWidget(self.output_path)
        container.addWidget(browse)
        form.addRow("输出文件", container)
        main_layout.addLayout(form)

        self.merge_button = QPushButton("开始合并")
        self.merge_button.clicked.connect(self.emit_merge)
        self.merge_button.setProperty("class", "primary")
        main_layout.addWidget(self.merge_button)

    # ------------------------------------------------------------------ API
    def add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "选择 PDF", filter="PDF Files (*.pdf)")
        if not files:
            return
        for file in files:
            item = QListWidgetItem(str(file))
            self.file_list.addItem(item)
        self.status_message.emit(f"已添加 {len(files)} 个文件。")

    def remove_selected(self) -> None:
        for item in self.file_list.selectedItems():
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
        self.status_message.emit("已移除选中的文件。")

    def move_selected_up(self) -> None:
        items = self.file_list.selectedItems()
        if not items:
            return
        moved = False
        for item in sorted(items, key=self.file_list.row):
            row = self.file_list.row(item)
            if row == 0:
                continue
            self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            item.setSelected(True)
            moved = True
        if moved:
            self.status_message.emit("已上移选中文件。")

    def move_selected_down(self) -> None:
        items = self.file_list.selectedItems()
        if not items:
            return
        moved = False
        for item in sorted(items, key=self.file_list.row, reverse=True):
            row = self.file_list.row(item)
            if row == self.file_list.count() - 1:
                continue
            self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            item.setSelected(True)
            moved = True
        if moved:
            self.status_message.emit("已下移选中文件。")

    def clear_list(self) -> None:
        self.file_list.clear()
        self.status_message.emit("列表已清空。")

    def choose_output(self) -> None:
        target, _ = QFileDialog.getSaveFileName(
            self, "保存合并结果", filter="PDF Files (*.pdf)", selectedFilter="PDF Files (*.pdf)"
        )
        if target:
            if not target.lower().endswith(".pdf"):
                target = f"{target}.pdf"
            self.output_path.setText(target)

    def emit_merge(self) -> None:
        files = [self.file_list.item(index).text() for index in range(self.file_list.count())]
        output = self.output_path.text().strip()
        if not files:
            QMessageBox.warning(self, "缺少文件", "请至少添加一个 PDF。")
            return
        if not output:
            QMessageBox.warning(self, "缺少输出路径", "请选择输出文件。")
            return
        self.merge_requested.emit(files, output)

    def set_running(self, running: bool) -> None:
        self.merge_button.setDisabled(running)


class SplitPanel(QWidget):
    split_requested = Signal(str, str, str)
    status_message = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("拆分 PDF")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        hint = QLabel("使用 1-3,5,7- 这种语法控制输出。留空或写 all 表示完整 PDF。")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QFormLayout()

        self.source_path = QLineEdit()
        source_button = QPushButton("选择文件…")
        source_button.clicked.connect(self.choose_source)
        source_row = QHBoxLayout()
        source_row.addWidget(self.source_path)
        source_row.addWidget(source_button)
        form.addRow("源 PDF", source_row)

        self.output_dir = QLineEdit()
        dir_button = QPushButton("选择目录…")
        dir_button.clicked.connect(self.choose_output_dir)
        dir_row = QHBoxLayout()
        dir_row.addWidget(self.output_dir)
        dir_row.addWidget(dir_button)
        form.addRow("输出目录", dir_row)

        self.range_field = QLineEdit()
        self.range_field.setPlaceholderText("1-3,5,7-")
        form.addRow("范围", self.range_field)

        layout.addLayout(form)

        self.split_button = QPushButton("开始拆分")
        self.split_button.setProperty("class", "primary")
        self.split_button.clicked.connect(self.emit_split)
        layout.addWidget(self.split_button)

        self.output_preview = QTextEdit()
        self.output_preview.setReadOnly(True)
        self.output_preview.setPlaceholderText("输出文件将在这里列出…")
        layout.addWidget(self.output_preview)

    def choose_source(self) -> None:
        file, _ = QFileDialog.getOpenFileName(self, "选择 PDF", filter="PDF Files (*.pdf)")
        if file:
            self.source_path.setText(file)

    def choose_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_dir.setText(directory)

    def emit_split(self) -> None:
        source = self.source_path.text().strip()
        output_dir = self.output_dir.text().strip()
        ranges = self.range_field.text().strip() or "all"
        if not source:
            QMessageBox.warning(self, "缺少源文件", "请选择需要拆分的 PDF。")
            return
        if not output_dir:
            QMessageBox.warning(self, "缺少输出目录", "请选择拆分结果的保存位置。")
            return
        self.split_requested.emit(source, ranges, output_dir)

    def set_running(self, running: bool) -> None:
        self.split_button.setDisabled(running)

    def show_outputs(self, paths: Iterable[str | Path]) -> None:
        lines = "\n".join(str(Path(path)) for path in paths)
        self.output_preview.setPlainText(lines or "暂无输出")


class PhotoToPDFPanel(QWidget):
    convert_requested = Signal(list, str, bool)
    status_message = Signal(str)

    SUPPORTED_EXTENSIONS = "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("照片转换为 PDF")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        hint = QLabel("支持 PNG/JPG/WebP 等常见格式，可按顺序合并到一个 PDF 中。")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        list_row = QHBoxLayout()

        self.photo_list = QListWidget()
        self.photo_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.photo_list.setAlternatingRowColors(True)
        self.photo_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        list_row.addWidget(self.photo_list)

        controls = QVBoxLayout()
        add_button = QPushButton("添加图片…")
        add_button.clicked.connect(self.add_images)
        controls.addWidget(add_button)

        remove_button = QPushButton("移除选中")
        remove_button.clicked.connect(self.remove_selected)
        controls.addWidget(remove_button)

        clear_button = QPushButton("清空列表")
        clear_button.clicked.connect(self.clear_list)
        controls.addWidget(clear_button)
        controls.addStretch(1)

        list_row.addLayout(controls)
        layout.addLayout(list_row)

        form = QFormLayout()
        self.output_path = QLineEdit()
        browse = QPushButton("选择输出…")
        browse.clicked.connect(self.choose_output)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_path)
        output_row.addWidget(browse)
        form.addRow("输出文件", output_row)
        layout.addLayout(form)

        self.convert_button = QPushButton("生成 PDF")
        self.convert_button.setProperty("class", "primary")
        self.convert_button.clicked.connect(lambda: self.emit_convert(False))
        layout.addWidget(self.convert_button)

        self.uniform_button = QPushButton("统一尺寸生成 PDF")
        self.uniform_button.clicked.connect(lambda: self.emit_convert(True))
        layout.addWidget(self.uniform_button)

    def add_images(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            filter=f"Image Files ({self.SUPPORTED_EXTENSIONS})",
        )
        if not files:
            return
        for file in files:
            self.photo_list.addItem(QListWidgetItem(file))
        self.status_message.emit(f"已添加 {len(files)} 张图片。")

    def remove_selected(self) -> None:
        for item in self.photo_list.selectedItems():
            row = self.photo_list.row(item)
            self.photo_list.takeItem(row)
        self.status_message.emit("已移除选中的图片。")

    def clear_list(self) -> None:
        self.photo_list.clear()
        self.status_message.emit("图片列表已清空。")

    def choose_output(self) -> None:
        target, _ = QFileDialog.getSaveFileName(
            self,
            "保存 PDF",
            filter="PDF Files (*.pdf)",
            selectedFilter="PDF Files (*.pdf)",
        )
        if target:
            if not target.lower().endswith(".pdf"):
                target = f"{target}.pdf"
            self.output_path.setText(target)

    def emit_convert(self, normalize: bool) -> None:
        files = [self.photo_list.item(index).text() for index in range(self.photo_list.count())]
        output = self.output_path.text().strip()
        if not files:
            QMessageBox.warning(self, "缺少图片", "请至少选择一张图片。")
            return
        if not output:
            QMessageBox.warning(self, "缺少输出路径", "请选择 PDF 输出位置。")
            return
        self.convert_requested.emit(files, output, normalize)

    def set_running(self, running: bool) -> None:
        self.convert_button.setDisabled(running)
        self.uniform_button.setDisabled(running)
