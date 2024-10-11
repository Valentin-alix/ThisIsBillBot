from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode

from src.gui.components.graphics.grid_widget import GridView
from src.gui.components.player_info.player_info_widget import PlayerInfoWidget
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals


class MapTab(QWidget):
    def __init__(self, grid_signals: GridSignals, game_info_signals: GameInfoSignals):
        super().__init__()
        self.setLayout(QVBoxLayout())
        scroll_area_info = SingleDirectionScrollArea()

        content_widget = QWidget()
        content_widget.setLayout(QHBoxLayout())

        grid_view = GridView(grid_signals)
        content_widget.layout().addWidget(grid_view)

        player_info_widget = PlayerInfoWidget(grid_signals, game_info_signals)
        content_widget.layout().addWidget(player_info_widget)

        scroll_area_info.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area_info.setWidgetResizable(True)
        scroll_area_info.setWidget(content_widget)
        scroll_area_info.enableTransparentBackground()

        self.layout().addWidget(scroll_area_info)
