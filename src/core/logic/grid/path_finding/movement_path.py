from dataclasses import dataclass

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_element import PathElement

WALK_HORIZONTAL_DIAG_DURATION = 510
WALK_VERTICAL_DIAG_DURATION = 425
WALK_LINEAR_DURATION = 480

RUN_HORIZONTAL_DIAG_DURATION = 255
RUN_VERTICAL_DIAG_DURATION = 150
RUN_LINEAR_DURATION = 170

RUN_MOUNT_HORIZONTAL_DIAG_DURATION = 200
RUN_MOUNT_VERTICAL_DIAG_DURATION = 120
RUN_MOUNT_LINEAR_DURATION = 135


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
                    MovementPath.get_key_by_cell_and_direction(
                        cell_path.step.cell_id, cell_path.orientation
                    )
                )
                curr_orientation = cell_path.orientation

        if curr_orientation is None:
            raise ValueError("Can't determine end orientation is path is empty")

        key_cells.append(
            MovementPath.get_key_by_cell_and_direction(
                self.end.cell_id, curr_orientation
            )
        )

        return key_cells

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
            return [
                PathElement(
                    step=MapPoint.from_cell_id(cells[0]),
                    orientation=DirectionsEnum.RIGHT,
                )
            ]
        path: list[PathElement] = []
        for i in range(1, len(cells)):
            previous_mp = MapPoint.from_cell_id(cells[i - 1])
            target_mp = MapPoint.from_cell_id(cells[i])
            path.append(
                PathElement(
                    step=previous_mp, orientation=previous_mp.orientation_to(target_mp)
                )
            )
        return path

    @staticmethod
    def get_total_duration(
        path_elements: list[PathElement],
        is_riding: bool,
        inventory_weight: int,
        inventory_weight_max: int,
    ) -> float:
        if len(path_elements) == 0:
            return 0

        if inventory_weight / inventory_weight_max >= 1 or len(path_elements) <= 2:
            can_run = False
        else:
            can_run = True

        speed_multiplier = 1
        if not can_run:
            linear_velocity = WALK_LINEAR_DURATION / speed_multiplier
            horizontal_diagonal_velocity = (
                WALK_HORIZONTAL_DIAG_DURATION / speed_multiplier
            )
            vertical_diagonal_velocity = WALK_VERTICAL_DIAG_DURATION / speed_multiplier
        elif is_riding:
            linear_velocity = RUN_MOUNT_LINEAR_DURATION / speed_multiplier
            horizontal_diagonal_velocity = (
                RUN_MOUNT_HORIZONTAL_DIAG_DURATION / speed_multiplier
            )
            vertical_diagonal_velocity = (
                RUN_MOUNT_VERTICAL_DIAG_DURATION / speed_multiplier
            )
        else:
            linear_velocity = RUN_LINEAR_DURATION / speed_multiplier
            horizontal_diagonal_velocity = (
                RUN_HORIZONTAL_DIAG_DURATION / speed_multiplier
            )
            vertical_diagonal_velocity = RUN_VERTICAL_DIAG_DURATION / speed_multiplier

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
    def get_cell_id_by_key(key: int) -> int:
        return key & 0x3FF

    @staticmethod
    def get_direction_by_key(key: int) -> DirectionsEnum:
        return DirectionsEnum((key >> 12) & 7)

    @staticmethod
    def get_key_by_cell_and_direction(cell_id: int, direction: DirectionsEnum) -> int:
        key = cell_id
        key |= direction << 12
        return key


if __name__ == "__main__":
    # print(MapPoint.from_cell_id(340))
    key_cells = [295, 28968, 28901]
    key_cells = [295, 4395, 343, 29016, 330, 29003, 24880, 24852]
    for key in key_cells:
        print(
            MovementPath.get_direction_by_key(key).name,
            MovementPath.get_cell_id_by_key(key),
        )
    # path = MovementPath.get_path_elements_from_cells([452, 438])
    # print(4.713 - 4.213)
    # duration = MovementPath.get_total_duration(path, False, 0, 1)
    # print(duration)
