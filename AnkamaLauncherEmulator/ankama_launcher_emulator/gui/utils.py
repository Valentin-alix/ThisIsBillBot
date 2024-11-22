from typing import Callable

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

_running: set[object] = set()


class Worker(QObject):
    success = pyqtSignal(object)
    error = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, func: Callable[[], object]) -> None:
        super().__init__()
        self.func = func

    @pyqtSlot()
    def run(self) -> None:
        try:
            self.success.emit(self.func())
        except Exception as e:
            self.error.emit(e)
        finally:
            self.finished.emit()


def run_in_background(
    func: Callable[[], object],
    on_success: Callable[[object], None] | None = None,
    on_error: Callable[[object], None] | None = None,
    parent: QObject | None = None,
) -> None:
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

    worker.finished.connect(_cleanup)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.start()
