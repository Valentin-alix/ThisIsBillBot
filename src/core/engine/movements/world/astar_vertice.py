from dataclasses import dataclass
from typing import Iterator

from d3_database.data_center.data_reader import DataReader
from d3_database.data_center.world_graph_reader import WorldGraphReader
from d3_database.models.world_graph import Edge, Vertice

from src.core.engine.movements.world.edge import iter_valid_outgoing_edges
from src.core.engine.movements.world.map_position import get_dist_to_maps
from src.core.signals.world_signals import WorldSignals
from src.core.states.game_state import GameState
from src.utils.astar import Astar, Node


@dataclass
class AstarWorld(Astar[Vertice]):
    game_state: GameState
    world_signals: WorldSignals | None = None

    def get_neighbors(self, data: Vertice) -> Iterator[Vertice]:
        if self.world_signals:
            map_data = DataReader().map_pos_by_map_id[data.m_mapId]
            if (
                map_data.posX != self.game_state.map.map_pos.posX
                or map_data.posY != self.game_state.map.map_pos.posY
            ):
                self.world_signals.color_pos.emit(map_data, (0, 255, 0))
        for edge in iter_valid_outgoing_edges(data, game_state=self.game_state):
            yield edge.m_to

    def get_dist(self, current: Vertice, ends: "set[Vertice]") -> float:
        curr_map_pos = DataReader().map_pos_by_map_id[current.m_mapId]
        ends_map_pos = [DataReader().map_pos_by_map_id[end.m_mapId] for end in ends]
        cost_to_ends = get_dist_to_maps(curr_map_pos, ends_map_pos)
        return cost_to_ends

    def reconstruct_path(self, node: Node[Vertice], do_reverse: bool) -> list[Edge]:
        result: list[Edge] = []
        while node.parent is not None:
            edge = WorldGraphReader().get_edge_by_src_and_dst_vertex(
                node.parent.data, node.data
            )
            result.append(edge)
            node = node.parent
        result.reverse()
        return result
