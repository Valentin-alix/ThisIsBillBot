import pytest
from DBDofusUnity.dofus_unity_reader.game_constants.directions import DirectionsEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

ORIGIN = (10, -5)


@pytest.mark.parametrize(
    ("delta", "four_dir_expected", "eight_dir_expected"),
    [
        ((1, 1), DirectionsEnum.DOWN_RIGHT, DirectionsEnum.RIGHT),
        ((1, -1), DirectionsEnum.DOWN_LEFT, DirectionsEnum.DOWN),
        ((-1, 1), DirectionsEnum.UP_RIGHT, DirectionsEnum.UP),
        ((-1, -1), DirectionsEnum.UP_LEFT, DirectionsEnum.LEFT),
        ((1, 0), DirectionsEnum.DOWN_RIGHT, DirectionsEnum.DOWN_RIGHT),
        ((-1, 0), DirectionsEnum.UP_LEFT, DirectionsEnum.UP_LEFT),
        ((0, 1), DirectionsEnum.UP_RIGHT, DirectionsEnum.UP_RIGHT),
        ((0, -1), DirectionsEnum.DOWN_LEFT, DirectionsEnum.DOWN_LEFT),
    ],
)
def test_advanced_orientation_matches_the_client(
    delta: tuple[int, int],
    four_dir_expected: DirectionsEnum,
    eight_dir_expected: DirectionsEnum,
) -> None:
    source = MapPoint.from_coords(*ORIGIN)
    target = MapPoint.from_coords(ORIGIN[0] + delta[0], ORIGIN[1] + delta[1])

    assert source.advanced_orientation_to(target) == four_dir_expected
    assert source.advanced_orientation_to(target, four_dir=False) == eight_dir_expected


def test_advanced_orientation_to_itself_is_down_right() -> None:
    source = MapPoint.from_coords(*ORIGIN)

    assert source.advanced_orientation_to(source) == DirectionsEnum.DOWN_RIGHT
    assert source.advanced_orientation_to(source, four_dir=False) == DirectionsEnum.DOWN_RIGHT
