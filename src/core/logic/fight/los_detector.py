from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.map_tools import MapTools
from src.core.repositories.map_reader import MapReader
from src.core.states.entity_state import EntityState
from src.signals.grid_signals import GridSignals


class LosDetector:
    @staticmethod
    def los_between(
        map_id: int,
        entity_state: EntityState,
        start: MapPoint,
        end: MapPoint,
    ) -> bool:
        line = MapTools.get_mps_between(start, end)
        if len(line) == 0:
            return True

        for index in range(len(line) - 1):
            mp = line[index]
            if (
                entity_state.is_entity_actor_on_cell_id(mp.cell_id)
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
    entity_state = EntityState(GridSignals())

    los = LosDetector.los_between(
        153879301,
        entity_state=entity_state,
        start=MapPoint.from_cell_id(299),
        end=MapPoint.from_cell_id(326),
    )
    print(los)
