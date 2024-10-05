from dataclasses import dataclass

from db_dofus_unity.protos.game.common_pb2 import InteractiveElement


@dataclass
class InteractiveElementInfo:
    state: int
    interactive_element: InteractiveElement

    def is_interactive_selectable(self):
        return self.interactive_element.on_current_map and self.state == 0
