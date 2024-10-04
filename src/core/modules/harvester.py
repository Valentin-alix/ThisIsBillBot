from dataclasses import dataclass, field
from threading import Event

from com.ankama.dofus.server.game.protocol.interactive.element_pb2 import (
    InteractiveUseEndedEvent,
)
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.map_behavior import MapBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.interactive_state import InteractiveState, Collectable
from src.core.states.inventory_state import InventoryState
from src.core.states.player_state import PlayerState
from src.signals.harvester_signals import HarvesterSignals
from src.signals.message_events import MessageEvents


@dataclass
class Harvester:
    msg_event: MessageEvents
    harvester_signals: HarvesterSignals
    map_behavior: MapBehavior
    path_finding: Pathfinding
    interactive_behavior: InteractiveBehavior
    interactive_state: InteractiveState
    player_state: PlayerState
    inventory_state: InventoryState
    is_playing: Event = field(init=False, default_factory=Event)

    def __post_init__(self):
        self.harvester_signals.play.connect(self.on_start)
        self.harvester_signals.stop.connect(self.on_stop)

    def on_start(self):
        self.msg_event.received_game_msg.connect(
            self.on_collected, InteractiveUseEndedEvent
        )
        self.start()

    def on_stop(self):
        self.is_playing.clear()
        self.msg_event.received_game_msg.disconnect(
            self.on_collected, InteractiveUseEndedEvent
        )

    def start(self):
        self.is_playing.set()
        self.collect()

    def on_collected(self, _, message: InteractiveUseEndedEvent):
        if not self.is_playing.is_set():
            return
        if not self.collect():
            # TODO move map
            ...

    def collect(self) -> bool:
        collectables = self.interactive_state.get_farmable_collectables()
        collectable_info = self.get_near_collectable(collectables)
        if collectable_info is None:
            return False

        move_path, collectable = collectable_info
        self.interactive_behavior.move_and_use_interactive(
            move_path,
            collectable.interactive_element.interactive_element.element_id,
            collectable.skill.skill_instance_uid,
        )
        return True

    def get_near_collectable(
        self,
        collectables: list[Collectable],
    ) -> tuple[MovementPath, Collectable] | None:
        near_move_path: tuple[MovementPath, Collectable, float] | None = None
        for collectable in collectables:
            move_path = self.path_finding.get_near_path_to_interactive(
                collectable.interactive_element.interactive_element.element_id,
                collectable.skill.skill_id,
            )
            if move_path is None:
                continue
            total_duration = move_path.get_total_duration(
                self.player_state.is_riding,
                self.inventory_state.inventory_weight.inventory_weight,
                self.inventory_state.inventory_weight.weight_max,
            )
            if near_move_path is None or total_duration < near_move_path[-1]:
                near_move_path = (move_path, collectable, total_duration)

        return near_move_path[:-1] if near_move_path else None
