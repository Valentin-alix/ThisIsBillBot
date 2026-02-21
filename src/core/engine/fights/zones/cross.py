from dataclasses import dataclass
from utils.cache import cache
from DBDofusUnity.dofus_unity_reader.game_constants.directions import DirectionsEnum
from DBDofusUnity.dofus_unity_reader.game_constants.spell_shape_enum import SpellShapeEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint

from src.core.engine.fights.zones.zone import Zone
from src.core.signals.grid_signals import GridSignals
from src.core.signals.player_signals import GameInfoSignals
from src.core.signals.world_signals import MapSignals


@dataclass(frozen=True)
class Cross(Zone):
    shape: SpellShapeEnum | None
    alternative_size: int
    size: int
    is_diagonal: bool = False
    is_all_directions: bool = False

    @property
    def min_radius(self):
        return self.alternative_size

    @property
    def radius(self):
        return self.size

    @property
    def is_only_perpendicular(self):
        return self.shape == SpellShapeEnum.T or self.shape == SpellShapeEnum.minus

    @property
    def is_diag_all_direction(self):
        return self.is_diagonal and self.is_all_directions

    @cache
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum | None) -> set[MapPoint]:
        mps: set[MapPoint] = set()
        if self.min_radius == 0:
            mps.add(mp)

        coords: list[tuple[int, int]] = []

        disabled_directions: list[DirectionsEnum] = []
        if self.is_only_perpendicular:
            match direction:
                case DirectionsEnum.DOWN_RIGHT | DirectionsEnum.UP_LEFT:
                    disabled_directions = [
                        DirectionsEnum.DOWN_RIGHT,
                        DirectionsEnum.UP_LEFT,
                    ]
                case DirectionsEnum.UP_RIGHT | DirectionsEnum.DOWN_LEFT:
                    disabled_directions = [
                        DirectionsEnum.UP_RIGHT,
                        DirectionsEnum.DOWN_LEFT,
                    ]
                case DirectionsEnum.DOWN | DirectionsEnum.UP:
                    disabled_directions = [DirectionsEnum.DOWN, DirectionsEnum.UP]
                case DirectionsEnum.RIGHT | DirectionsEnum.LEFT:
                    disabled_directions = [DirectionsEnum.RIGHT, DirectionsEnum.LEFT]

        for radius in range(self.radius, 0, -1):
            if radius < self.min_radius:
                continue

            if not self.is_diag_all_direction:
                if DirectionsEnum.DOWN_RIGHT not in disabled_directions:
                    coords.append((mp.x + radius, mp.y))
                if DirectionsEnum.UP_LEFT not in disabled_directions:
                    coords.append((mp.x - radius, mp.y))
                if DirectionsEnum.UP_RIGHT not in disabled_directions:
                    coords.append((mp.x, mp.y + radius))
                if DirectionsEnum.DOWN_LEFT not in disabled_directions:
                    coords.append((mp.x, mp.y - radius))

            if self.is_diag_all_direction or self.is_all_directions:
                if DirectionsEnum.DOWN not in disabled_directions:
                    coords.append((mp.x + radius, mp.y - radius))
                if DirectionsEnum.UP not in disabled_directions:
                    coords.append((mp.x - radius, mp.y + radius))
                if DirectionsEnum.RIGHT not in disabled_directions:
                    coords.append((mp.x + radius, mp.y + radius))
                if DirectionsEnum.LEFT not in disabled_directions:
                    coords.append((mp.x - radius, mp.y - radius))

        for coord in coords:
            if coord in MAP_POINT_BY_COORD:
                mps.add(MapPoint.from_coords(*coord))

        return mps


if __name__ == "__main__":
    grid_signals = GridSignals()
    debug_signals = MapSignals()
    game_info_signals = GameInfoSignals()
