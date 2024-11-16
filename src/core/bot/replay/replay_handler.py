from dataclasses import dataclass, field
from typing import Any

from PyQt5.QtCore import QThread

from src.gui.utils.run_in_background import run_in_background
from src.services.replayer import Replayer


@dataclass
class ReplayHandler:
    """Handles replay functionality for the bot."""

    replayer: Replayer
    _thread_worker_runnings: list[tuple[QThread, Any]] = field(
        init=False, default_factory=list
    )

    def on_replay_requested(
        self,
        path: str,
        preserve_timing: bool = False,
        speedup: float | None = None,
        use_obfuscated: bool = False,
    ) -> None:
        """
        Handle replay request.

        Args:
            path: Path to the recording file
            preserve_timing: Whether to preserve original timing between messages
            speedup: Speed multiplier for replay (e.g., 2.0 for 2x speed)
            use_obfuscated: If True, replay obfuscated messages instead of clear ones
        """
        self._thread_worker_runnings.append(
            run_in_background(
                self.replayer.get_replay_worker(
                    path, preserve_timing, speedup, use_obfuscated, do_wait_state=True
                )
            )
        )
