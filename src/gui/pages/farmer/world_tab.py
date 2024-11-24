from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode

from src.core.signals.world_signals import WorldSignals
from src.gui.components.graphics.map_world_widget import MapWorldView


class WorldTab(QWidget):
    def __init__(self, world_signals: WorldSignals, parent: QWidget | None = None):
        super().__init__(parent=parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        scroll_area_info = SingleDirectionScrollArea(self)

        content_widget = QWidget(scroll_area_info)
        content_widget_layout = QHBoxLayout()
        content_widget.setLayout(content_widget_layout)
        world_view = MapWorldView(world_signals=world_signals)
        content_widget_layout.addWidget(world_view)

        scroll_area_info.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area_info.setWidgetResizable(True)
        scroll_area_info.setWidget(content_widget)
        scroll_area_info.enableTransparentBackground()

        layout.addWidget(scroll_area_info)
