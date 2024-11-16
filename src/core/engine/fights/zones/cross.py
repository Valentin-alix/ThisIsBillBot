from dataclasses import dataclass

from D3Database.enums.directions import DirectionsEnum
from D3Database.grid.map_point import MAP_POINT_BY_COORD, MapPoint
from D3Database.utils import cache
from src.core.engine.fights.spell_shape import SpellShapeEnum
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

    # map_state = MapState(grid_signals=grid_signals)
    # entity_state = EntityState(grid_signals=grid_signals)
    # interactive_state = InteractiveState(grid_signals=grid_signals)
    # player_state = PlayerState(
    #     game_info_signals=game_info_signals,
    #     interactive_state=interactive_state,
    #     entity_state=entity_state,
    #     map_state=map_state,
    # )
    # fight_state = FightState(
    #     game_info_signals=game_info_signals, player_state=player_state
    # )
    # player_state = PlayerState(
    #     map_state=map_state,
    #     game_info_signals=game_info_signals,
    #     entity_state=entity_state,
    #     interactive_state=interactive_state,
    # )

    # map_state.map_id = 154010373
    # start = MapPoint.from_cell_id(506)
    # end = MapPoint.from_cell_id(452)

    # cross = Cross(
    #     shape=None, size=5, alternative_size=1, is_all_directions=True, is_diagonal=True
    # )

    # application = QApplication(sys.argv)
    # widget = GridView(grid_signals=grid_signals, debug_signals=debug_signals)
    # widget.on_new_map_id(map_state.map_id)
    # for cell in cross.get_mps(end, DirectionsEnum.UP_RIGHT):
    #     debug_signals.green_cell.emit(cell)
    # widget.show()

    # application.exec()
