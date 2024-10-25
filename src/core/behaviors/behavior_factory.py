from dataclasses import dataclass, field
from typing import Any

from src.core.behaviors.behavior import Behavior


type Instruction = tuple[Behavior, dict[str, Any]]


@dataclass
class BehaviorFactory(Behavior):
    _instructions: list[Instruction] = field(init=False, default_factory=list)

    def run(self, instructions: list[Instruction]) -> None:
        self._instructions = instructions
        self.process_instruction()

    def process_instruction(self):
        if len(self._instructions) == 0:
            return self.finish()
        behavior, args = self._instructions.pop()
        behavior.start(**args, callback=self.process_instruction, parent=self)
