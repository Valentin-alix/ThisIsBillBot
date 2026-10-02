from dataclasses import dataclass

from DBDofusUnity.dofus_unity_reader.game_constants.directions import DirectionsEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from src.core.engine.movements.map.path_finding.path_element import PathElement

WALK_HORIZONTAL_DIAG_DURATION = 510
WALK_VERTICAL_DIAG_DURATION = 425
WALK_LINEAR_DURATION = 480

RUN_HORIZONTAL_DIAG_DURATION = 220
RUN_VERTICAL_DIAG_DURATION = 135
RUN_LINEAR_DURATION = 150


@dataclass
class MovementPath:
    start: MapPoint
    end: MapPoint
    path: list[PathElement]

    def get_key_cells(self) -> list[int]:
        curr_orientation: DirectionsEnum | None = None
        key_cells: list[int] = []

        for index, cell_path in enumerate(self.path):
            if cell_path.orientation != curr_orientation:
                key_cells.append(
                    MovementPath.get_key_by_cell_and_direction(cell_path.step.cell_id, cell_path.orientation)
                )
                curr_orientation = cell_path.orientation

        if curr_orientation is None:
            raise ValueError("Can't determine end orientation is path is empty")

        key_cells.append(MovementPath.get_key_by_cell_and_direction(self.end.cell_id, curr_orientation))

        return key_cells

    def get_next_step(self, current_mp: MapPoint) -> MapPoint | None:
        steps = [element.step for element in self.path] + [self.end]
        try:
            index = steps.index(current_mp)
        except ValueError:
            return None
        if index + 1 < len(steps):
            return steps[index + 1]
        return None

    @staticmethod
    def get_step_duration(
        linear_velocity: float,
        horizontal_diagonal_velocity: float,
        vertical_diagonal_velocity: float,
        orientation: DirectionsEnum,
    ) -> float:
        if (orientation % 2) != 0:
            return linear_velocity
        if (orientation % 4) == 0:
            return horizontal_diagonal_velocity
        return vertical_diagonal_velocity

    @staticmethod
    def get_path_elements_from_cells(cells: list[int]) -> list[PathElement]:
        if len(cells) == 0:
            return []
        if len(cells) == 1:
            return [PathElement(step=MapPoint.from_cell_id(cells[0]), orientation=DirectionsEnum.RIGHT)]
        path: list[PathElement] = []
        for i in range(1, len(cells)):
            previous_mp = MapPoint.from_cell_id(cells[i - 1])
            target_mp = MapPoint.from_cell_id(cells[i])
            path.append(PathElement(step=previous_mp, orientation=previous_mp.orientation_to(target_mp)))
        return path

    @staticmethod
    def get_total_duration(
        path_elements: list[PathElement],
        inventory_weight: int,
        inventory_weight_max: int,
    ) -> float:
        if len(path_elements) == 0:
            return 0

        linear_velocity, horizontal_diagonal_velocity, vertical_diagonal_velocity = MovementPath.get_velocity(
            inventory_weight=inventory_weight,
            inventory_weight_max=inventory_weight_max,
            path_elements=path_elements,
        )

        total_duration: float = 0
        for step in path_elements:
            total_duration += MovementPath.get_step_duration(
                linear_velocity,
                horizontal_diagonal_velocity,
                vertical_diagonal_velocity,
                step.orientation,
            )

        return total_duration / 1000

    @staticmethod
    def get_duration_until(
        path_elements: list[PathElement],
        step_count: int,
        inventory_weight: int,
        inventory_weight_max: int,
    ) -> float:
        if len(path_elements) == 0 or step_count <= 0:
            return 0

        linear_velocity, horizontal_diagonal_velocity, vertical_diagonal_velocity = MovementPath.get_velocity(
            inventory_weight=inventory_weight,
            inventory_weight_max=inventory_weight_max,
            path_elements=path_elements,
        )
        total_duration: float = 0
        for step in path_elements[:step_count]:
            total_duration += MovementPath.get_step_duration(
                linear_velocity,
                horizontal_diagonal_velocity,
                vertical_diagonal_velocity,
                step.orientation,
            )

        return total_duration / 1000

    @staticmethod
    def get_velocity(inventory_weight: int, inventory_weight_max: int, path_elements: list[PathElement]):
        can_run = not (inventory_weight / inventory_weight_max > 1 or len(path_elements) <= 2)
        if not can_run:
            return WALK_LINEAR_DURATION, WALK_HORIZONTAL_DIAG_DURATION, WALK_VERTICAL_DIAG_DURATION
        return RUN_LINEAR_DURATION, RUN_HORIZONTAL_DIAG_DURATION, RUN_VERTICAL_DIAG_DURATION

    @staticmethod
    def get_key_by_cell_and_direction(cell_id: int, direction: DirectionsEnum) -> int:
        key = cell_id
        key |= direction << 12
        return key
