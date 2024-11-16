from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode

from src.core.signals.grid_signals import GridSignals
from src.gui.components.graphics.grid_widget import GridView


class MapTab(QWidget):
    def __init__(self, grid_signals: GridSignals):
        super().__init__()
        self.setLayout(QVBoxLayout())
        scroll_area_info = SingleDirectionScrollArea()

        content_widget = QWidget()
        content_widget.setLayout(QHBoxLayout())

        grid_view = GridView(grid_signals)
        content_widget.layout().addWidget(grid_view)

        scroll_area_info.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area_info.setWidgetResizable(True)
        scroll_area_info.setWidget(content_widget)
        scroll_area_info.enableTransparentBackground()

        self.layout().addWidget(scroll_area_info)
