# pdfTools 2.0

PDF Atelier 2.0 是一款基于 PySide6 的桌面工具，提供常用的 PDF 合并、拆分以及“照片转 PDF”等工作流。核心逻辑完全封装在 `pdftools.core` 中，可在 GUI、CLI 或未来的自动化服务之间复用。

## 主要特性
- **PDF 合并**：拖拽/排列多个 PDF，生成单个输出文件。
- **PDF 拆分**：通过表达式（如 `1-3,5,7-`）批量拆分页面，实时展示导出结果。
- **照片转 PDF**：
  - 支持添加、移除、上移/下移以调整页序。
  - 标准模式按调整后的顺序生成多页 PDF。
  - “统一尺寸生成 PDF”按钮会将所有图片缩放到第一页大小，确保排版一致。
  - “清理手写并生成 PDF”按钮在导出前弱化手写痕迹，恢复试卷底稿。
- **任务后台化**：所有耗时操作交给 `TaskRunner` 的 Qt 线程池，避免界面卡顿。

## 快速开始
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

运行桌面端（会自动创建/重用虚拟环境）：
```bash
bash scripts/run_gui.sh
```

如需直接调用入口，可使用：
```bash
python -m pdftools.gui.main
```

## 测试
```bash
source .venv/bin/activate
pytest
```

## 文档
- `AGENTS.md`：仓库结构、命名规范、测试和构建命令。
- `docs/photo_to_pdf_design.md`：照片转 PDF 功能的详细设计方案、错误处理与后续规划。

遇到问题或需要新功能，可在 GitHub Issues 中提交需求。欢迎贡献代码并遵循 Conventional Commits 规范。
