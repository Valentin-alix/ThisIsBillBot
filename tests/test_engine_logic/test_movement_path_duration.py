from dofus_unity_reader.game_constants.directions import DirectionsEnum
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.movements.map.path_finding.movement_path import (
    RUN_LINEAR_DURATION,
    RUN_VERTICAL_DIAG_DURATION,
    WALK_LINEAR_DURATION,
    MovementPath,
)
from src.core.engine.movements.map.path_finding.path_element import PathElement

# DOWN_RIGHT is orthogonal -> linear step cost.
_LINEAR = DirectionsEnum.DOWN_RIGHT


def _linear_path(step_count: int) -> list[PathElement]:
    return [
        PathElement(step=MapPoint.from_cell_id(cell_id), orientation=_LINEAR) for cell_id in range(step_count)
    ]


def test_get_duration_until_uses_full_path_run_speed_for_short_prefix() -> None:
    # A long path runs; the delay to reach an early cell must use RUN speed, not
    # the WALK fallback that get_total_duration would apply to a <=2 element slice.
    path_elements = _linear_path(5)

    duration = MovementPath.get_duration_until(
        path_elements, 2, inventory_weight=0, inventory_weight_max=1000
    )

    assert duration == 2 * RUN_LINEAR_DURATION / 1000
    # And it is strictly faster than the buggy walk-based estimate of the slice.
    walk_estimate = MovementPath.get_total_duration(
        path_elements[:2], inventory_weight=0, inventory_weight_max=1000
    )
    assert walk_estimate == 2 * WALK_LINEAR_DURATION / 1000
    assert duration < walk_estimate


def test_get_duration_until_edges() -> None:
    path_elements = _linear_path(5)

    assert MovementPath.get_duration_until(path_elements, 0, 0, 1000) == 0
    # Reaching the last cell equals the full-path duration.
    assert MovementPath.get_duration_until(path_elements, len(path_elements), 0, 1000) == (
        MovementPath.get_total_duration(path_elements, 0, 1000)
    )


def test_run_duration_matches_the_unity_client() -> None:
    # Logged movement of session 20260731T155836: cells 444 -> 220, eight vertical diagonal steps.
    # The real client confirmed after 1145 ms; the AS3 constants predicted 1200 ms and made every
    # confirm late. Guards against someone restoring 170/255/150 from `RunningMovementBehavior.as`.
    path_elements = MovementPath.get_path_elements_from_cells([444, 416, 388, 360, 332, 304, 276, 248, 220])
    assert all(element.orientation is DirectionsEnum.UP for element in path_elements)

    duration = MovementPath.get_total_duration(path_elements, inventory_weight=0, inventory_weight_max=1000)

    assert duration == 8 * RUN_VERTICAL_DIAG_DURATION / 1000 == 1.080


def test_get_duration_until_overweight_walks() -> None:
    path_elements = _linear_path(5)

    duration = MovementPath.get_duration_until(
        path_elements, 2, inventory_weight=2000, inventory_weight_max=1000
    )

    assert duration == 2 * WALK_LINEAR_DURATION / 1000
