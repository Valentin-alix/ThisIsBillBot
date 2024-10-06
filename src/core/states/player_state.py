import dataclasses
from dataclasses import dataclass
from datetime import datetime

from db_dofus_unity.protos.game.common_pb2 import (
    CharacterCharacteristicDetailed,
    ServerType,
)
from src.core.logic.grid.map_point import MapPoint
from src.core.repositories.data_reader import DataReader
from src.core.repositories.map_reader import MapReader
from src.core.repositories.world_graph_reader import WorldGraphReader
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.interactive_state import InteractiveState
from src.core.states.map_state import MapState
from src.core.states.state import State
from src.interfaces.models.collectable import Collectable


@dataclass
class PlayerState(State):
    map_state: MapState
    entity_state: EntityState
    fight_state: FightState
    interactive_state: InteractiveState

    breed_id: int = dataclasses.field(init=False, default=0)
    level: int = dataclasses.field(init=False, default=1)

    subscription_end_date: datetime = dataclasses.field(
        init=False, default_factory=lambda: datetime(1975, 1, 1)
    )
    game_type: ServerType = dataclasses.field(init=False, default=ServerType.UNDEFINED)
    character_id: int = dataclasses.field(init=False, default=0)
    detail_stat_value_by_id: dict[int, CharacterCharacteristicDetailed] = (
        dataclasses.field(init=False, default_factory=dict)
    )
    jobs_lvl_by_id: dict[int, int] = dataclasses.field(init=False, default_factory=dict)
    is_riding: bool = dataclasses.field(init=False, default=False)

    @property
    def limited_lvl(self) -> int:
        return min(self.level, 200)

    @property
    def map_point(self):
        if self.fight_state.in_fight:
            return MapPoint.from_cell_id(
                self.fight_state.actor_by_id[self.character_id].disposition.cell_id
            )
        return MapPoint.from_cell_id(
            self.entity_state.actor_by_id[self.character_id].disposition.cell_id
        )

    def get_farmable_collectables(self) -> list[Collectable]:
        farmable_collectables: list[Collectable] = []
        for (
            interactive_element
        ) in self.interactive_state.interactive_element_by_id.values():
            state_element = self.interactive_state.stated_element_by_id.get(
                interactive_element.element_id
            )
            if (
                not interactive_element.on_current_map
                or state_element is None
                or state_element.state != 0
            ):
                continue
            if len(interactive_element.enabled_skills) == 0:
                continue
            skill = interactive_element.enabled_skills[0]
            data_skill = DataReader().skill_by_id[skill.skill_id]
            if data_skill.gatheredRessourceItem == -1:
                continue
            collectable = Collectable(
                interactive_element=interactive_element,
                skill=skill,
                resource_item_id=data_skill.gatheredRessourceItem,
            )
            if collectable.is_farmable(
                self.jobs_lvl_by_id.get(data_skill.parentJobId, 1)
            ):
                farmable_collectables.append(collectable)

        return farmable_collectables

    @property
    def curr_vertex(self):
        vertex = WorldGraphReader().get_vertex(
            self.map_state.map_id, self.linked_zone_rp
        )
        if vertex is not None:
            return vertex

        potential_vertices = WorldGraphReader().get_vertices_by_map_id()[
            self.map_state.map_id
        ]

        for vertice in potential_vertices.m_values.Array:
            if vertice.m_zoneId == self.linked_zone_rp:
                return vertice
        else:
            return potential_vertices.m_values.Array[1]

    @property
    def linked_zone_rp(self) -> int:
        cell_data = MapReader().get_cell_data_by_cell_id(
            self.map_state.map_id, self.map_point.cell_id
        )
        return (cell_data.linkedZone & 240) >> 4
