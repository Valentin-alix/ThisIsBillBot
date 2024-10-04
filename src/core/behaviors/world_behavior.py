from dataclasses import dataclass, field

from com.ankama.dofus.server.game.protocol.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.map_behavior import MapBehavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.world.auto_trip import AutoTrip
from src.core.logic.world.transition_type import TransitionTypeEnum
from src.core.repositories.world_graph_reader import Edge
from src.core.states.interactive_state import InteractiveState
from src.core.states.player_state import PlayerState
from src.signals.message_events import MessageEvents


@dataclass
class WorldBehavior:
    msg_event: MessageEvents
    map_behavior: MapBehavior
    interactive_behavior: InteractiveBehavior
    interactive_state: InteractiveState
    player_state: PlayerState
    auto_trip: AutoTrip

    _auto_trip_edges: list[Edge] | None = field(default=None, init=False)
    _current_edge_index: int | None = field(default=None, init=False)

    def go_to_map_id(self, map_id: int):
        path = self.auto_trip.find_path(map_id)
        if path is None:
            return
        if len(path) == 0:
            return
        self.msg_event.received_game_msg.connect(
            self.on_new_map, MapComplementaryInformationEvent
        )
        self._auto_trip_edges = path
        if self._auto_trip_edges is not None and len(self._auto_trip_edges) > 0:
            self._current_edge_index = 0
            self.process_edge(
                self._current_edge_index,
                self._auto_trip_edges[self._current_edge_index],
            )

    def on_new_map(self, _, message: MapComplementaryInformationEvent):
        if (
            self._current_edge_index is None
            or self._auto_trip_edges is None
            or len(self._auto_trip_edges) < self._current_edge_index + 1
        ):
            print("player is arrived to destination")
            self.msg_event.received_game_msg.disconnect(
                self.on_new_map, MapComplementaryInformationEvent
            )
            return
        self.process_edge(
            self._current_edge_index, self._auto_trip_edges[self._current_edge_index]
        )

    def process_edge(self, _current_edge_index: int, edge: Edge):
        self._current_edge_index = _current_edge_index + 1
        transition = edge.m_transitions.Array[0]
        transition_type = transition.m_type
        if transition_type == TransitionTypeEnum.INTERACTIVE:
            move_path = self.map_behavior.path_finding.find_path(
                self.player_state.map_point,
                MapPoint.from_cell_id(transition.m_cellId),
            )
            interactive_element = self.interactive_state.interactive_elements_by_id[
                transition.m_id
            ]
            related_skill_uid = next(
                skill.skill_instance_uid
                for skill in interactive_element.interactive_element.enabled_skills
                if skill.skill_id == transition.m_skillId
            )
            self.interactive_behavior.move_and_use_interactive(
                move_path,
                interactive_element.interactive_element.element_id,
                related_skill_uid,
            )

        else:
            ...
