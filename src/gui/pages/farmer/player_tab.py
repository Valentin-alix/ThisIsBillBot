from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode

from src.gui.components.player_info.player_info_widget import PlayerInfoWidget
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals


class PlayerTab(QWidget):
    def __init__(self, grid_signals: GridSignals, game_info_signals: GameInfoSignals):
        super().__init__()
        self.setLayout(QVBoxLayout())
        scroll_area_info = SingleDirectionScrollArea()

        player_info_widget = PlayerInfoWidget(grid_signals, game_info_signals)

        scroll_area_info.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area_info.setWidgetResizable(True)
        scroll_area_info.setWidget(player_info_widget)
        scroll_area_info.enableTransparentBackground()

        self.layout().addWidget(scroll_area_info)
