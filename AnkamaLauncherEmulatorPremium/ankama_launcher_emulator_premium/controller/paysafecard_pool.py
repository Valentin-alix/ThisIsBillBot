import os
from threading import Lock

from base_python.singleton import Singleton

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import PAYSAFECARDS_PATH
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.line_file import (
    read_lines,
    write_lines,
)


class PaysafecardPoolController(metaclass=Singleton):
    """Thread-safe accessor for a flat ``paysafecards.txt`` file (one pin per line).

    Pins are loaded lazily and pruned in-place when ``remove`` is called.
    """

    _lock = Lock()

    def load(self) -> list[str]:
        with self._lock:
            return self._load_unlocked()

    def reserve_next_pin(self) -> str:
        with self._lock:
            pins = self._load_unlocked()
            if not pins:
                raise ValueError("No Paysafecard PIN is available")
            reserved_pin = pins[0]
            self._write_unlocked(pins[1:])
            return reserved_pin

    def restore_reserved_pin(self, pin: str) -> None:
        with self._lock:
            pins = self._load_unlocked()
            if pin not in pins:
                self._write_unlocked([pin, *pins])

    def _load_unlocked(self) -> list[str]:
        if not os.path.exists(PAYSAFECARDS_PATH):
            return []
        normalized_pins = [
            line.replace(" ", "").strip() for line in read_lines(PAYSAFECARDS_PATH, encoding="utf-8")
        ]
        return [pin for pin in normalized_pins if pin]

    def _write_unlocked(self, pins: list[str]) -> None:
        lines = [f"{pin}\n" for pin in pins]
        write_lines(PAYSAFECARDS_PATH, lines, create_parent=True, encoding="utf-8")
