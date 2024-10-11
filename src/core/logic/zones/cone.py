import sys
from dataclasses import dataclass

from PyQt5.QtWidgets import QApplication

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint, MAP_POINT_BY_COORD
from src.core.logic.zones.zone import Zone
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.interactive_state import InteractiveState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.gui.components.graphics.grid_widget import GridView
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import MapSignals


@dataclass
class Cone(Zone):
    alternative_size: int
    size: int

    def __post_init__(self):
        self.min_radius: int = self.alternative_size
        self.radius: int = self.size

    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]:
        mps: set[MapPoint] = set()
        if self.radius == 0:
            if self.min_radius == 0:
                mps.add(mp)
            return mps

        coords: list[tuple[int, int]] = []

        match direction:
            case DirectionsEnum.UP_LEFT:
                for step, i in enumerate(range(mp.x, mp.x - self.radius - 1, -1)):
                    for j in range(-step, step + 1):
                        if not abs(mp.x - i) + abs(j) >= self.min_radius:
                            continue
                        coords.append((i, j + mp.y))
            case DirectionsEnum.DOWN_LEFT:
                for step, j in enumerate(range(mp.y, mp.y - self.radius - 1, -1)):
                    for i in range(-step, step + 1):
                        if not abs(i) + abs(mp.y - j) >= self.min_radius:
                            continue
                        coords.append((i + mp.x, j))
            case DirectionsEnum.DOWN_RIGHT:
                for step, i in enumerate(range(mp.x, mp.x + self.radius + 1)):
                    for j in range(-step, step + 1):
                        if not abs(mp.x - i) + abs(j) >= self.min_radius:
                            continue
                        coords.append((i, j + mp.y))
            case DirectionsEnum.UP_RIGHT:
                for step, j in enumerate(range(mp.y, mp.y + self.radius + 1)):
                    for i in range(-step, step + 1):
                        if not abs(i) + abs(mp.y - j) >= self.min_radius:
                            continue
                        coords.append((i + mp.x, j))

        for coord in coords:
            if coord in MAP_POINT_BY_COORD:
                mps.add(MapPoint.from_coords(*coord))

        return mps


if __name__ == "__main__":
    grid_signals = GridSignals()
    debug_signals = MapSignals()
    game_info_signals = GameInfoSignals()

    map_state = MapState(grid_signals=grid_signals)
    entity_state = EntityState(grid_signals=grid_signals)
    interactive_state = InteractiveState(grid_signals=grid_signals)
    player_state = PlayerState(
        game_info_signals=game_info_signals,
        interactive_state=interactive_state,
        entity_state=entity_state,
        map_state=map_state,
    )
    fight_state = FightState(
        game_info_signals=game_info_signals, player_state=player_state
    )
    player_state = PlayerState(
        map_state=map_state,
        game_info_signals=game_info_signals,
        entity_state=entity_state,
        interactive_state=interactive_state,
    )

    map_state.map_id = 154010373
    start = MapPoint.from_cell_id(506)
    end = MapPoint.from_cell_id(452)

    cone = Cone(size=5, alternative_size=1)

    application = QApplication(sys.argv)
    widget = GridView(grid_signals=grid_signals, debug_signals=debug_signals)
    widget.on_new_map_id(map_state.map_id)
    for cell in cone.get_mps(end, DirectionsEnum.UP_RIGHT):
        debug_signals.green_cell.emit(cell)
    widget.show()

    application.exec()
