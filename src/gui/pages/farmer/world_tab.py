from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode

from src.gui.components.graphics.map_world_widget import MapWorldView
from src.signals.world_signals import WorldSignals


class WorldTab(QWidget):
    def __init__(self, world_signals: WorldSignals):
        super().__init__()
        self.setLayout(QVBoxLayout())
        scroll_area_info = SingleDirectionScrollArea()

        content_widget = QWidget()
        content_widget.setLayout(QHBoxLayout())
        world_view = MapWorldView(world_signals=world_signals)
        content_widget.layout().addWidget(world_view)

        scroll_area_info.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area_info.setWidgetResizable(True)
        scroll_area_info.setWidget(content_widget)
        scroll_area_info.enableTransparentBackground()

        self.layout().addWidget(scroll_area_info)


