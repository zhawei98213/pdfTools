# 照片转 PDF 设计说明

## 背景
用户希望在现有的 PDF Atelier 2.0 桌面端中，将多张照片按顺序快速生成一个 PDF。实现方案必须满足：

- 支持常见图片格式（PNG/JPG/WebP/BMP/TIFF）。
- 可与现有 GUI 的多线程任务机制集成，避免阻塞主线程。
- 逻辑位于 `pdftools.core`，供 CLI/GUI/服务端复用。
- 提供基本的错误提示、输入校验以及测试覆盖。

## 核心流程
1. GUI 通过新 Tab “照片转 PDF” 收集图片列表与输出路径。
2. 面板把这些参数交给 `MainWindow`，由 `TaskRunner` 在线程池里执行 `convert_images_to_pdf`。
3. `convert_images_to_pdf` 使用 Pillow 读取图片、转换为 RGB，保存为多页 PDF。若启用“统一尺寸”选项，将其它图片缩放到第一张的尺寸后再导出；若启用“清理手写”，则先运行 `remove_handwriting_marks` 将暗色笔迹抹除。
4. 执行成功后 UI 弹窗提示路径，失败则展示堆栈并复位按钮状态。

## 模块设计
- `pdftools.core.operations.convert_images_to_pdf`
  - 接收 `Sequence[str | Path]` 与目标路径。
  - 调用 `normalize_paths` 保证路径有效。
  - 对每张图片执行 `_prepare_for_pdf`，确保透明通道与调色板处理正确。
  - 使用 Pillow 把首图写为 PDF，`append_images` 负责附加其余页面。
  - 输出目录自动创建，返回最终 `Path`。
- `PhotoToPDFPanel`
  - 负责 UI 控件、文件选择和输入验证。
  - 提供 `convert_requested` 信号 (list[str], str, bool, bool)，两个布尔值分别表示是否开启统一尺寸与手写清理。
  - 复用了与合并面板类似的列表操作体验，支持添加/移除/清空以及上移、下移调序，并新增“统一尺寸生成 PDF”和“清理手写并生成 PDF”按钮。
- `MainWindow`
  - 新增 Tab 以及 `_handle_photo_convert`。
  - 与 `TaskRunner` 集成，处理成功/失败反馈。

## 错误处理
- 未选择图片或输出：面板内即时弹窗提示。
- 核心函数对空序列抛 `ValueError`，供 CLI/自动化层拦截。
- 统一尺寸模式下按第一张图片宽高作为基准，采用 LANCZOS 重采样，避免拉伸失真。
- 手写清理模式先通过高斯模糊估算亮度阈值，再用白色背景替换低亮度区域，弱化手写痕迹。
- Pillow 读图失败会在 `TaskRunner` 内捕获堆栈，UI 弹窗显示。

## 测试策略
- 新增 `tests/core/test_operations.py`：
  - 构建临时彩色方块图片，验证生成 PDF 页数正确。
  - 验证未传图片时抛出 `ValueError`。
  - 验证启用统一尺寸后多页 PDF 的 `mediabox` 宽高一致。
  - 验证 `remove_handwriting_marks` 提升手写区域亮度，避免笔迹残留。
- GUI 交互目前人工验证，后续可按计划补充 Qt 测试或截图回归。

## 后续规划
- 提供 CLI 命令，例如 `pdftools photo-to-pdf --images *.jpg`。
- 支持自动旋转并读取 EXIF 方向。
- 加入压缩/质量参数以平衡体积与清晰度。
- 记忆最近输出目录，改善批量体验。
