from src.core.logic.path_finding.map_point import MapPoint
from src.core.logic.path_finding.map_tools import MapTools


class DataMapProvider:
    @staticmethod
    def fill_entity_on_cell_array(
        cell_array: dict[int, bool], allow_throught_entity: bool
    ):
        entities = []
        for entity in entities:
            # if entity is blocking
            ...
        return cell_array

    @staticmethod
    def point_mov(
        x: int,
        y: int,
        allow_through_entity: bool = True,
        previous_cell_id: int = -1,
        end_cell_id: int = -1,
        avoid_obstacle: bool = True,
    ):
        if not MapPoint.is_in_map(x, y):
            return False
        # TODO Get cell_data
        datas_map: list
        cell_id = MapTools.get_cell_id_by_coord(x, y)
        return True

    @staticmethod
    def point_special_effects(x: int, y: int) -> int:
        cell_id = MapTools.get_cell_id_by_coord(x, y)
        return 0
