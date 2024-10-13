from typing import Iterable

from data_center.map_reader import MapReader
from grid.map_point import MapPoint
from src.core.logic.grid.map_tools import MapTools


class LosDetector:
    @staticmethod
    def los_between(
        map_id: int,
        taken_mps: Iterable[MapPoint],
        start: MapPoint,
        end: MapPoint,
    ) -> bool:
        line = MapTools.get_mps_between(start, end)
        if len(line) == 0:
            return True

        for index in range(len(line) - 1):
            mp = line[index]
            if (
                mp in taken_mps
                or (
                    MapReader()
                    .get_cell_data_by_cell_id(map_id=map_id, cell_id=mp.cell_id)
                    .los
                )
                != 1
            ):
                return False

        return True
