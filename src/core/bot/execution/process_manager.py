from dataclasses import dataclass, field

import psutil

from src.services.logging.logger import Logger


@dataclass
class ProcessManager:
    """Manages bot process lifecycle (kill, restart, etc.)."""

    logger: Logger
    pid: int | None = field(init=False, default=None)

    def kill_process(self):
        """Kill the Dofus process associated with this bot."""
        if self.pid is None:
            return self.logger.warning("No pid to kill")
        try:
            process = psutil.Process(self.pid)
            process.terminate()
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                self.logger.info("timeout, force kill process")
                process.kill()
            self.logger.info(f"killed pid : {self.pid}")
        except psutil.NoSuchProcess:
            self.logger.info("process of related pid is not running anymore, skip.")
        self.pid = None
