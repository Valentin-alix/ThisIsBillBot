import dataclasses
from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.common_pb2 import (
    Character,
    CharacterCharacteristics,
)
from src.core.logic.grid.map_point import MapPoint
from src.core.repositories.map_reader import MapReader
from src.core.repositories.world_graph_reader import WorldGraphReader
from src.core.states.map_state import MapState
from src.core.states.state import State


@dataclass
class PlayerState(State):
    map_state: MapState

    character: Character | None = dataclasses.field(init=False, default=None)
    characteristics: CharacterCharacteristics | None = dataclasses.field(
        init=False, default=None
    )
    is_in_fight: bool = dataclasses.field(init=False, default=False)
    is_riding: bool = dataclasses.field(init=False, default=False)

    @property
    def map_point(self):
        return next(
            MapPoint.from_cell_id(actor.disposition.cell_id)
            for actor in self.map_state.map.actors
            if actor.actor_id == self.character.id
        )

    @property
    def curr_vertex(self):
        vertex = WorldGraphReader().get_vertex(
            self.map_state.map.map_id, self.linked_zone_rp
        )
        if vertex is not None:
            return vertex
        potential_vertices = WorldGraphReader().get_vertices_by_map_id()[
            self.map_state.map.map_id
        ]

        for vertice in potential_vertices.m_values.Array:
            if vertice.m_zoneId == self.linked_zone_rp:
                return vertice
        else:
            return potential_vertices.m_values.Array[1]

    @property
    def linked_zone_rp(self) -> int:
        cell_data = MapReader().get_cell_data_by_cell_id(
            self.map_state.map.map_id, self.map_point.cell_id
        )
        return (cell_data.linkedZone & 240) >> 4
