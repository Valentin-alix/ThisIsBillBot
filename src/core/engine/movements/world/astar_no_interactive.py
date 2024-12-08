from dataclasses import dataclass
from time import sleep
from typing import Iterator

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.enums.transition_type import TransitionTypeEnum
from dofus_unity_reader.models.world_graph import Vertice

from src.core.engine.movements.world.astar_vertice import AstarWorld
from src.core.engine.movements.world.edge import (
    iter_valid_outgoing_edges,
)


@dataclass
class AstarNoInteractive(AstarWorld):
    def get_neighbors(self, data: Vertice) -> Iterator[Vertice]:
        if self.world_signals:
            map_data = DataReader().map_pos_by_map_id[data.m_mapId]
            self.world_signals.color_pos.emit(map_data, (0, 255, 0))
            sleep(0.01)

        for edge in iter_valid_outgoing_edges(data, game_state=self.game_state):
            transition_type = edge.m_transitions[0].m_type
            if transition_type not in [
                TransitionTypeEnum.MAP_ACTION,
                TransitionTypeEnum.SCROLL_ACTION,
                TransitionTypeEnum.SCROLL,
            ]:
                continue
            yield edge.m_to
