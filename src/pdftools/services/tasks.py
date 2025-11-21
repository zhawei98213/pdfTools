"""Generic background task helpers shared by GUI and future agents."""
from __future__ import annotations

import traceback
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class WorkerSignals(QObject):
    started = Signal()
    finished = Signal(object)
    failed = Signal(str)


class Worker(QRunnable):
    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self) -> None:  # pragma: no cover - run inside Qt thread pool
        self.signals.started.emit()
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:  # noqa: BLE001
            error = traceback.format_exc()
            self.signals.failed.emit(error)
            return
        self.signals.finished.emit(result)


class TaskRunner(QObject):
    """High-level helper to schedule blocking work off the UI thread."""

    task_started = Signal()
    task_finished = Signal(object)
    task_failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.pool = QThreadPool.globalInstance()

    def run(
        self,
        fn: Callable[..., Any],
        *args: Any,
        on_finished: Callable[[Any], None] | None = None,
        on_failed: Callable[[str], None] | None = None,
        **kwargs: Any,
    ) -> None:
        worker = Worker(fn, *args, **kwargs)
        worker.signals.started.connect(self.task_started)
        if on_finished:
            worker.signals.finished.connect(on_finished)
        worker.signals.finished.connect(self.task_finished)
        if on_failed:
            worker.signals.failed.connect(on_failed)
        worker.signals.failed.connect(self.task_failed)
        self.pool.start(worker)
