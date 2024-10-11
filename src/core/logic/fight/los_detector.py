from src.core.data_center.map_reader import MapReader
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.map_tools import MapTools


class LosDetector:
    @staticmethod
    def los_between(
        map_id: int,
        taken_mps: set[MapPoint],
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


if __name__ == "__main__":
    los = LosDetector.los_between(
        map_id=153879301,
        taken_mps=set(),
        start=MapPoint.from_cell_id(496),
        end=MapPoint.from_cell_id(442),
    )
    print(los)
