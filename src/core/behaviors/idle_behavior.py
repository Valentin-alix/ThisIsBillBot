from dataclasses import dataclass

from src.core.behaviors.behavior import Behavior


@dataclass
class IdleBehavior(Behavior):
    def run(self, duration: float):
        self.logger.info(f"Going idle for {duration:.1f}s")
        self.run_timer(duration, self.finish)
