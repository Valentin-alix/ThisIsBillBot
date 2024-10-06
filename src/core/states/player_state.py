import dataclasses
from dataclasses import dataclass
from datetime import datetime

from db_dofus_unity.protos.game.common_pb2 import (
    ServerType,
    CharacterCharacteristic,
)
from src.core.logic.grid.map_point import MapPoint
from src.core.repositories.data_reader import DataReader
from src.core.repositories.map_reader import MapReader
from src.core.repositories.world_graph_reader import WorldGraphReader, Vertex
from src.core.states.entity_state import EntityState
from src.core.states.interactive_state import InteractiveState
from src.core.states.map_state import MapState
from src.core.states.state import State
from src.interfaces.models.collectable import Collectable
from src.signals.player_signals import GameInfoSignals


@dataclass
class PlayerState(State):
    game_info_signals: GameInfoSignals
    map_state: MapState
    entity_state: EntityState
    interactive_state: InteractiveState

    _breed_id: int = dataclasses.field(init=False, default=0)
    _level: int = dataclasses.field(init=False, default=1)
    _subscription_end_date: datetime = dataclasses.field(
        init=False, default_factory=lambda: datetime(1975, 1, 1)
    )
    _character_id: int = dataclasses.field(init=False, default=0)

    game_type: ServerType = dataclasses.field(init=False, default=ServerType.UNDEFINED)
    characteristic_by_id: dict[int, CharacterCharacteristic] = dataclasses.field(
        init=False, default_factory=dict
    )
    waypoint_ids: list[int] = dataclasses.field(init=False, default_factory=list)
    jobs_lvl_by_id: dict[int, int] = dataclasses.field(init=False, default_factory=dict)
    is_riding: bool = dataclasses.field(init=False, default=False)

    def get_stat_usable_by_id(self, stat_id: int) -> int:
        stat = self.characteristic_by_id[stat_id].usable
        return stat.base - stat.used

    @property
    def breed_id(self):
        return self._breed_id

    @breed_id.setter
    def breed_id(self, value: int):
        self._breed_id = value
        self.game_info_signals.breed_id.emit(value)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value: int):
        self._level = value
        self.game_info_signals.level.emit(value)

    @property
    def subscription_end_date(self):
        return self._subscription_end_date

    @subscription_end_date.setter
    def subscription_end_date(self, value: datetime):
        self._subscription_end_date = value
        self.game_info_signals.subscription_end_date.emit(value)

    @property
    def character_id(self):
        return self._character_id

    @character_id.setter
    def character_id(self, value: int):
        self._character_id = value

    @property
    def is_sub(self) -> bool:
        return (
            datetime.now(tz=self.subscription_end_date.tzinfo)
            < self.subscription_end_date
        )

    @property
    def limited_lvl(self) -> int:
        return min(self.level, 200)

    @property
    def map_point(self):
        return MapPoint.from_cell_id(
            self.entity_state.actor_by_id[self.character_id].disposition.cell_id
        )

    def get_farmable_collectables(self) -> list[Collectable]:
        farmable_collectables: list[Collectable] = []
        for stated_element in self.interactive_state.stated_element_by_id.values():
            if stated_element.state != 0:
                continue
            related_interactive = self.interactive_state.interactive_element_by_id.get(
                stated_element.element_id
            )
            if (
                not related_interactive
                or related_interactive.on_current_map is not True
                or len(related_interactive.enabled_skills) == 0
            ):
                continue
            skill = related_interactive.enabled_skills[0]
            data_skill = DataReader().skill_by_id[skill.skill_id]
            if data_skill.gatheredRessourceItem == -1:
                continue
            collectable = Collectable(
                interactive_element=related_interactive,
                skill=skill,
                resource_item_id=data_skill.gatheredRessourceItem,
            )
            if collectable.is_farmable(
                self.jobs_lvl_by_id.get(data_skill.parentJobId, 1)
            ):
                farmable_collectables.append(collectable)

        return farmable_collectables

    @property
    def curr_vertex(self) -> Vertex:
        vertex = WorldGraphReader().get_vertex(
            self.map_state.map_id, self.linked_zone_rp
        )
        if vertex is not None:
            return vertex

        potential_vertices = WorldGraphReader().get_vertices_by_map_id[
            self.map_state.map_id
        ]

        for vertice in potential_vertices.m_values.Array:
            if vertice.m_zoneId == self.linked_zone_rp:
                return vertice

        return potential_vertices.m_values.Array[1]

    @property
    def linked_zone_rp(self) -> int:
        cell_data = MapReader().get_cell_data_by_cell_id(
            self.map_state.map_id, self.map_point.cell_id
        )
        return (cell_data.linkedZone & 240) >> 4
