import random
import sys
from dataclasses import dataclass

import icecream

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_element import PathElement

WALK_HORIZONTAL_DIAG_DURATION_MEAN = 0.5390895873608917
WALK_HORIZONTAL_DIAG_DURATION_VAR = 0.001067391740768872

WALK_VERTICAL_DIAG_DURATION_MEAN = 0.5497773144868948
WALK_VERTICAL_DIAG_DURATION_VAR = 0.002915269054054996

WALK_LINEAR_DURATION_MEAN = 0.41758097349105827
WALK_LINEAR_DURATION_VAR = 7.474874375074591e-05

RUN_HORIZONTAL_DIAG_DURATION_MEAN = 0.45367340545271156
RUN_HORIZONTAL_DIAG_DURATION_VAR = 0.00034615919722585025

RUN_VERTICAL_DIAG_DURATION_MEAN = 0.17209191803287516
RUN_VERTICAL_DIAG_DURATION_VAR = 8.024245923248129e-05

RUN_LINEAR_DURATION_MEAN = 0.1426003061828884
RUN_LINEAR_DURATION_VAR = 7.64093133014606e-06

MOUNT_WALK_HORIZONTAL_DIAG_DURATION_MEAN = 0.49119408032942263
MOUNT_WALK_HORIZONTAL_DIAG_DURATION_VAR = 3.989744728559326e-05

MOUNT_WALK_VERTICAL_DIAG_DURATION_MEAN = 0.31889592910345615
MOUNT_WALK_VERTICAL_DIAG_DURATION_VAR = 5.019864616842067e-05

MOUNT_WALK_LINEAR_DURATION_MEAN = 0.4633602883596644
MOUNT_WALK_LINEAR_DURATION_VAR = 6.422502754135058e-06

MOUNT_RUN_HORIZONTAL_DIAG_DURATION_MEAN = 0.17441830453875082
MOUNT_RUN_HORIZONTAL_DIAG_DURATION_VAR = 1.619182665664463e-05

MOUNT_RUN_VERTICAL_DIAG_DURATION_MEAN = 0.1171778480358038
MOUNT_RUN_VERTICAL_DIAG_DURATION_VAR = 4.612344074579732e-06

MOUNT_RUN_LINEAR_DURATION_MEAN = 0.1461911486904954
MOUNT_RUN_LINEAR_DURATION_VAR = 3.4772192848653018e-06


@dataclass
class MovementPath:
    start: MapPoint
    end: MapPoint
    path: list[PathElement]

    @staticmethod
    def walk_horizontal_diag_duration(is_riding: bool):
        if is_riding:
            return random.gauss(
                MOUNT_WALK_HORIZONTAL_DIAG_DURATION_MEAN,
                MOUNT_WALK_HORIZONTAL_DIAG_DURATION_VAR,
            )
        return random.gauss(
            WALK_HORIZONTAL_DIAG_DURATION_MEAN, WALK_HORIZONTAL_DIAG_DURATION_VAR
        )

    @staticmethod
    def walk_vertical_diag_duration(is_riding: bool):
        if is_riding:
            return random.gauss(
                MOUNT_WALK_VERTICAL_DIAG_DURATION_MEAN,
                MOUNT_WALK_VERTICAL_DIAG_DURATION_VAR,
            )
        return random.gauss(
            WALK_VERTICAL_DIAG_DURATION_MEAN,
            WALK_VERTICAL_DIAG_DURATION_VAR,
        )

    @staticmethod
    def walk_linear_duration(is_riding: bool):
        if is_riding:
            return random.gauss(
                MOUNT_WALK_LINEAR_DURATION_MEAN,
                MOUNT_WALK_LINEAR_DURATION_VAR,
            )
        return random.gauss(WALK_LINEAR_DURATION_MEAN, WALK_LINEAR_DURATION_VAR)

    @staticmethod
    def run_horizontal_diag_duration(is_riding: bool):
        if is_riding:
            return random.gauss(
                MOUNT_RUN_HORIZONTAL_DIAG_DURATION_MEAN,
                MOUNT_RUN_HORIZONTAL_DIAG_DURATION_VAR,
            )
        return random.gauss(
            RUN_HORIZONTAL_DIAG_DURATION_MEAN,
            RUN_HORIZONTAL_DIAG_DURATION_VAR,
        )

    @staticmethod
    def run_vertical_diag_duration(is_riding: bool):
        if is_riding:
            return random.gauss(
                MOUNT_RUN_VERTICAL_DIAG_DURATION_MEAN,
                MOUNT_RUN_VERTICAL_DIAG_DURATION_VAR,
            )
        return random.gauss(
            RUN_VERTICAL_DIAG_DURATION_MEAN,
            RUN_VERTICAL_DIAG_DURATION_VAR,
        )

    @staticmethod
    def run_linear_duration(is_riding: bool):
        if is_riding:
            return random.gauss(RUN_LINEAR_DURATION_MEAN, RUN_LINEAR_DURATION_VAR)
        return random.gauss(
            MOUNT_RUN_LINEAR_DURATION_MEAN, MOUNT_RUN_LINEAR_DURATION_VAR
        )

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

    def get_step_duration(
        self,
        is_riding: bool,
        inventory_weight: int,
        inventory_weight_max: int,
        orientation: DirectionsEnum,
    ) -> float:
        if inventory_weight_max != 0:
            weight_coeff = inventory_weight / inventory_weight_max
        else:
            weight_coeff = 0

        can_run = weight_coeff < 1.0 and len(self.path) > 2
        if not can_run:
            if orientation % 2 == 0:
                if orientation % 4 == 0:
                    return MovementPath.walk_horizontal_diag_duration(is_riding)
                else:
                    return MovementPath.walk_vertical_diag_duration(is_riding)
            else:
                return MovementPath.walk_linear_duration(is_riding)
        else:
            if orientation % 2 == 0:
                if orientation % 4 == 0:
                    return MovementPath.run_horizontal_diag_duration(is_riding)
                else:
                    return MovementPath.run_vertical_diag_duration(is_riding)
            else:
                return MovementPath.run_linear_duration(is_riding)

    def get_total_duration(
        self, is_riding: bool, inventory_weight: int, inventory_weight_max: int
    ) -> float:
        if len(self.path) == 0:
            return 0

        total_duration: float = 0
        curr_orientation: DirectionsEnum = self.path[0].orientation
        for step in self.path[1:]:
            total_duration += self.get_step_duration(
                is_riding,
                inventory_weight,
                inventory_weight_max,
                curr_orientation,
            )
            curr_orientation = step.orientation

        # add last path duration
        total_duration += self.get_step_duration(
            is_riding,
            inventory_weight,
            inventory_weight_max,
            curr_orientation,
        )
        return total_duration

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
    key_cells = [538, 62, 48]
    for key_cell in key_cells:
        icecream.ic(DirectionsEnum(MovementPath.get_direction_by_key(key_cell)))
        icecream.ic(MovementPath.get_cell_id_by_key(key_cell))

    sys.exit()

    movz_path = MovementPath(
        start=MapPoint.from_cell_id(402),
        path=[
            PathElement(step=MapPoint.from_cell_id(402), orientation=DirectionsEnum.UP),
            PathElement(step=MapPoint.from_cell_id(430), orientation=DirectionsEnum.UP),
            PathElement(
                step=MapPoint.from_cell_id(444), orientation=DirectionsEnum.LEFT
            ),
            PathElement(step=MapPoint.from_cell_id(459), orientation=DirectionsEnum.UP),
        ],
        end=MapPoint.from_cell_id(459),
    )
    print(movz_path.get_total_duration(False, 0, 1))

    # key_cells = [24742]
    # for key_cell in key_cells:
    #     icecream.ic(DirectionsEnum(MovementPath.get_direction_by_key(key_cell)))
    #     icecream.ic(MovementPath.get_cell_id_by_key(key_cell))
