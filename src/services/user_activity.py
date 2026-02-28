import logging
from collections import deque
from datetime import datetime, timezone
from queue import Queue
from threading import Thread
from typing import Literal

from PyQt6.QtCore import QObject, pyqtSignal
from pydantic import BaseModel, ValidationError

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import USER_ACTIVITY_PATH
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.atomic_file import atomic_write_text
from utils.singleton import Singleton

_MAX_ENTRIES = 500
logger = logging.getLogger(__name__)


class UserActivityEntry(BaseModel):
    happened_at: datetime
    severity: Literal["info", "warning", "error"]
    message: str
    login: str | None = None


class UserActivityFile(BaseModel):
    entries: tuple[UserActivityEntry, ...] = ()


class UserActivitySignals(QObject):
    entry_added = pyqtSignal()


class UserActivityService(metaclass=Singleton):
    def __init__(self) -> None:
        self._entries: tuple[UserActivityEntry, ...] = ()
        self.signals = UserActivitySignals()
        self._queue: Queue[UserActivityEntry | None] = Queue()
        self._worker = Thread(target=self._run, daemon=True)
        self._worker.start()

    def recent(self) -> tuple[UserActivityEntry, ...]:
        return self._entries

    def record(
        self,
        severity: Literal["info", "warning", "error"],
        message: str,
        *,
        login: str | None = None,
    ) -> None:
        entry = UserActivityEntry(
            happened_at=datetime.now(timezone.utc),
            severity=severity,
            message=message,
            login=login,
        )
        self._queue.put(entry)

    def close(self) -> None:
        if not self._worker.is_alive():
            return
        self._queue.join()
        self._queue.put(None)
        self._worker.join()

    def _run(self) -> None:
        persisted_entries: tuple[UserActivityEntry, ...] = ()
        try:
            if USER_ACTIVITY_PATH.exists():
                persisted_entries = UserActivityFile.model_validate_json(
                    USER_ACTIVITY_PATH.read_text(encoding="utf-8")
                ).entries
        except (OSError, ValidationError) as error:
            logger.warning("Cannot read user activity: %s", error)

        entries = deque(persisted_entries, maxlen=_MAX_ENTRIES)
        self._entries = tuple(entries)

        while True:
            entry = self._queue.get()
            if entry is None:
                self._queue.task_done()
                return
            entries.append(entry)
            snapshot = tuple(entries)
            self._entries = snapshot
            self.signals.entry_added.emit()

            try:
                atomic_write_text(
                    USER_ACTIVITY_PATH,
                    UserActivityFile(entries=snapshot).model_dump_json(indent=2),
                )
            except (OSError, ValidationError) as error:
                logger.warning("Cannot record user activity: %s", error)
            finally:
                self._queue.task_done()
