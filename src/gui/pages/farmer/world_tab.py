import sys

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode

from src.core.data_center.data_reader import DataReader
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


if __name__ == "__main__":
    application = QApplication(sys.argv)
    world_signals = WorldSignals()
    widget = WorldTab(world_signals)
    widget.resize(700, 700)

    coords = [(5, 5), (1, 6), (2, 8)]
    for coord in coords:
        world_signals.color_pos.emit(
            DataReader().map_pos_by_coord[coord][0], (0, 255, 0)
        )
    world_signals.curr_map_pos.emit(DataReader().map_pos_by_coord[(4, 4)][0])
    widget.show()
    application.exec()
