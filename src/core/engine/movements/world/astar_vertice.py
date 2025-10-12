from collections.abc import Iterator
from dataclasses import dataclass, field

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from DBDofusUnity.dofus_unity_reader.models.world_graph import Edge, Vertice

from src.core.engine.contexts import WorldPathContext
from src.core.engine.movements.world.edge import iter_valid_outgoing_edges
from src.core.engine.movements.world.map_position import get_dist_to_maps
from src.core.signals.world_signals import WorldSignals
from src.utils.astar import Astar, Node, OpenSet, SearchNodeDict


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

    def find_path(
        self,
        start: Vertice,
        ends: set[Vertice],
        heuristic_scale: float = 1,
        do_reverse: bool = False,
        max_iteration: int = 9999,
    ) -> list[Edge] | None:
        open_set: OpenSet[Vertice] = OpenSet()

        start_node = Node(
            data=start,
            cost_to_node=0,
            total_cost=self.get_dist(start, ends),
        )

        search_node_dict = SearchNodeDict[Vertice]()
        search_node_dict[start] = start_node
        open_set.push(start_node)

        iteration = 0
        while open_set and iteration <= max_iteration:
            iteration += 1
            current_node = open_set.pop()
            if self.is_goal_reached(current_node.data, ends):
                return self.reconstruct_path(current_node, do_reverse)

            current_node.closed = True

            for node in (search_node_dict[data] for data in self.get_neighbors(current_node.data)):
                if node.closed:
                    continue

                try:
                    cost_to_node = current_node.cost_to_node + self.get_dist(
                        current_node.data,
                        {node.data},
                    )
                except KeyError:
                    continue

                if cost_to_node >= node.cost_to_node:
                    continue

                if node.in_open_set:
                    open_set.remove(node)

                node.parent = current_node
                node.cost_to_node = cost_to_node
                node.total_cost = cost_to_node + self.get_dist(node.data, ends) * heuristic_scale

                open_set.push(node)

        return None
