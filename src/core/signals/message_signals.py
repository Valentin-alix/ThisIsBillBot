from threading import Event

from PyQt6.QtCore import QObject, pyqtSignal


class MessageInfoSignals(QObject):
    msg_info = pyqtSignal(object, bool)

    def __init__(self) -> None:
        super().__init__()
        self._capture_enabled = Event()

    @property
    def capture_enabled(self) -> bool:
        return self._capture_enabled.is_set()

    def set_capture_enabled(self, enabled: bool) -> None:
        if enabled:
            self._capture_enabled.set()
        else:
            self._capture_enabled.clear()
