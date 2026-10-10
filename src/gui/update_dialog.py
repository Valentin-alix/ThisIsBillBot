import logging
import os
from collections.abc import Callable

from PyQt6.QtCore import QEventLoop, QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from src.gui.application import Application
from src.services.release_update import (
    SKIP_UPDATE_ENV,
    clean_update_staging,
    consume_update_status,
    prepare_update,
)
from src.utils.runtime_support import RuntimeSetupError


class StartupWorker(QThread):
    progress = pyqtSignal(str)

    def __init__(
        self, application: Application, task: Callable[[Callable[[str], None]], bool | None]
    ) -> None:
        super().__init__(application)
        self.task = task
        self.result: bool | None = None
        self.error: RuntimeSetupError | OSError | None = None

    def run(self) -> None:
        try:
            self.result = self.task(self.progress.emit)
        except (RuntimeSetupError, OSError) as error:
            self.error = error


def run_startup_task(
    application: Application, task: Callable[[Callable[[str], None]], bool | None]
) -> bool | None:
    worker = StartupWorker(application, task)
    loop = QEventLoop()
    worker.progress.connect(application.startup_splash.set_status)
    worker.finished.connect(loop.quit)
    worker.start()
    loop.exec()
    worker.wait()
    error, result = worker.error, worker.result
    worker.deleteLater()
    if error is not None:
        raise error
    return result


def check_release_update(application: Application) -> bool:
    clean_update_staging()
    status = consume_update_status()
    if status:
        logging.getLogger(__name__).warning("Update failed: %s", status)
        QMessageBox.warning(None, "Update failed", status)
    if os.environ.pop(SKIP_UPDATE_ENV, None) == "1":
        return False
    try:
        return bool(run_startup_task(application, prepare_update))
    except (RuntimeSetupError, OSError) as error:
        logging.getLogger(__name__).warning("Update failed: %s", error, exc_info=True)
        QMessageBox.warning(None, "Update failed", f"{error}\n\nContinuing with the current bundle.")
        return False
