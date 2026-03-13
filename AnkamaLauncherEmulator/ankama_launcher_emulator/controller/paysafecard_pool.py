import os
from threading import Lock

from utils.singleton import Singleton

from ankama_launcher_emulator.consts import PAYSAFECARDS_PATH
from ankama_launcher_emulator.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)
from ankama_launcher_emulator.web._client.line_file import read_lines


class PaysafecardPoolController(metaclass=Singleton):
    """Pins remain available until Paysafecard explicitly reports them as unusable."""

    _FILE_LOCK_TIMEOUT_SECONDS = 20.0
    _lock = Lock()

    def load(self) -> list[str]:
        with self._lock:
            with acquire_file_lock(PAYSAFECARDS_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS):
                return self._load_unlocked()

    def get_next_pin(self) -> str:
        with self._lock:
            with acquire_file_lock(PAYSAFECARDS_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS):
                pins = self._load_unlocked()
                if not pins:
                    raise ValueError("No Paysafecard PIN is available")
                return pins[0]

    def remove_pin(self, pin: str) -> None:
        with self._lock:
            with acquire_file_lock(PAYSAFECARDS_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS):
                pins = self._load_unlocked()
                if pin not in pins:
                    return
                pins.remove(pin)
                self._write_unlocked(pins)

    def _load_unlocked(self) -> list[str]:
        if not os.path.exists(PAYSAFECARDS_PATH):
            return []
        normalized_pins = [
            line.replace(" ", "").strip() for line in read_lines(PAYSAFECARDS_PATH, encoding="utf-8")
        ]
        return [pin for pin in normalized_pins if pin]

    def _write_unlocked(self, pins: list[str]) -> None:
        atomic_write_text(PAYSAFECARDS_PATH, "".join(f"{pin}\n" for pin in pins))
