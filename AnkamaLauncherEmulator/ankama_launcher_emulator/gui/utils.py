from typing import Any, Callable

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

_running: set[object] = set()

FuncType = Callable[[Callable], Any] | Callable[[], Any]


class Worker(QObject):
    progress = pyqtSignal(str)
    success = pyqtSignal(object)
    error = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, func: FuncType) -> None:
        super().__init__()
        self.func = func

    @pyqtSlot()
    def run(self) -> None:
        try:
            try:
                self.success.emit(self.func(self.progress.emit))  # pyright: ignore[reportCallIssue]
            except TypeError:
                self.success.emit(self.func())  # pyright: ignore[reportCallIssue]
        except Exception as e:
            self.error.emit(e)
        finally:
            self.finished.emit()


def run_in_background(
    func: FuncType,
    on_success: Callable[[object], None] | None = None,
    on_error: Callable[[object], None] | None = None,
    on_progress: Callable[[str], None] | None = None,
    parent: QObject | None = None,
) -> tuple[QThread, Worker]:
    worker = Worker(func)
    thread = QThread(parent)

    _running.add(worker)
    _running.add(thread)

    def _cleanup() -> None:
        _running.discard(worker)
        _running.discard(thread)

    worker.moveToThread(thread)
    thread.started.connect(worker.run)

    if on_success is not None:
        worker.success.connect(on_success)
    if on_error is not None:
        worker.error.connect(on_error)
    if on_progress is not None:
        worker.progress.connect(on_progress)

    worker.finished.connect(_cleanup)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.start()

    return thread, worker
