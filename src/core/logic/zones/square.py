import sys

from PyQt5.QtWidgets import QApplication

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.zones.ZRectangle import ZRectangle
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.interactive_state import InteractiveState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.gui.components.graphics.grid_widget import GridView
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import MapSignals


class Square(ZRectangle):
    def __init__(self, min_radius: int, size: int, is_diagonal_free: bool):
        super().__init__(
            min_radius=min_radius,
            alternative_size=size,
            size=size,
            is_diagonal_free=is_diagonal_free,
        )


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

    rectangle = Square(min_radius=0, size=1, is_diagonal_free=False)

    application = QApplication(sys.argv)
    widget = GridView(grid_signals=grid_signals, debug_signals=debug_signals)
    widget.on_new_map_id(map_state.map_id)
    for cell in rectangle.get_mps(end, DirectionsEnum.UP_RIGHT):
        debug_signals.green_cell.emit(cell)
    widget.show()

    application.exec()
