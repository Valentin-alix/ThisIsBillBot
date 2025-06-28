from dataclasses import dataclass, field

import psutil

from src.services.logging_utils.contextual_logger import ContextualLogger


@dataclass
class ProcessManager(ContextualLogger):
    """Manages bot process lifecycle (kill, restart, etc.)."""

    pid: int | None = field(init=False, default=None)

    def kill_process(self):
        """Kill the Dofus process associated with this bot."""
        if self.pid is None or not psutil.pid_exists(self.pid):
            return self.logger.info("No pid to kill")
        try:
            process = psutil.Process(self.pid)
            process.terminate()
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                self.logger.info("Timeout, force kill process")
                process.kill()
            self.logger.info(f"Killed pid : {self.pid}")
        except psutil.NoSuchProcess:
            self.logger.info("Process of related pid is not running anymore, skip.")
        self.pid = None

    def is_bot_process_running(self) -> bool:
        return self.pid is not None and psutil.pid_exists(self.pid)
