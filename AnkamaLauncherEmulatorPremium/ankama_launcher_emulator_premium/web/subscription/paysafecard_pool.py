import os
from dataclasses import dataclass, field
from threading import Lock

from ankama_launcher_emulator_premium.web._client.line_file import (
    read_lines,
    write_lines,
)


@dataclass
class PaysafecardPool:
    """Thread-safe accessor for a flat ``paysafecards.txt`` file (one pin per line).

    Pins are loaded lazily and pruned in-place when ``remove`` is called.
    """

    path: str
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def load(self) -> list[str]:
        with self._lock:
            return self._load_unlocked()

    def remove(self, pin: str) -> None:
        with self._lock:
            pins = self._load_unlocked()
            kept = [existing_pin for existing_pin in pins if existing_pin != pin]
            if len(kept) != len(pins):
                self._write_unlocked(kept)

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
        if not os.path.exists(self.path):
            return []
        normalized_pins = [line.replace(" ", "").strip() for line in read_lines(self.path, encoding="utf-8")]
        return [pin for pin in normalized_pins if pin]

    def _write_unlocked(self, pins: list[str]) -> None:
        lines = [f"{pin}\n" for pin in pins]
        write_lines(self.path, lines, create_parent=True, encoding="utf-8")
