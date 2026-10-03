from collections.abc import Iterator
from dataclasses import dataclass, field

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from DBDofusUnity.dofus_unity_reader.models.world_graph import Edge, Vertice

from src.core.engine.contexts import WorldPathContext
from src.core.engine.movements.world.edge import iter_valid_outgoing_edges
from src.core.engine.movements.world.map_position import get_dist_to_maps
from src.core.signals.world_signals import WorldSignals
from src.utils.astar import Astar, Node


@dataclass
class AstarWorld(Astar[Vertice, Edge]):
    world_signals: WorldSignals | None = None
    context: WorldPathContext | None = field(init=False, default=None)

    def _get_context(self) -> WorldPathContext:
        if self.context is None:
            raise RuntimeError("World path context must be set before pathing")
        return self.context

    def set_context(self, context: WorldPathContext) -> None:
        self.context = context

    def get_neighbors(self, data: Vertice) -> Iterator[Vertice]:
        context = self._get_context()
        if self.world_signals:
            map_data = DataReader().map_info_by_map_id[data.m_mapId]
            if map_data.posX != context.current_map_pos.posX or map_data.posY != context.current_map_pos.posY:
                self.world_signals.color_pos.emit(map_data, (0, 255, 0))
        for edge in iter_valid_outgoing_edges(data, context.transition):
            yield edge.m_to

    def get_dist(self, current: Vertice, ends: "set[Vertice]") -> float:
        curr_map_pos = DataReader().map_info_by_map_id[current.m_mapId]
        ends_map_pos = [DataReader().map_info_by_map_id[end.m_mapId] for end in ends]
        cost_to_ends = get_dist_to_maps(curr_map_pos, ends_map_pos)
        return cost_to_ends

    def reconstruct_path(self, node: Node[Vertice], do_reverse: bool) -> list[Edge]:
        result: list[Edge] = []
        while node.parent is not None:
            edge = WorldGraphReader().get_edge_by_src_and_dst_vertex(node.parent.data, node.data)
            result.append(edge)
            node = node.parent
        result.reverse()
        return result
