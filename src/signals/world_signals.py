from grid.map_point import MapPoint
from PyQt5.QtCore import QObject, pyqtSignal


class MapSignals(QObject):
    white_cell = pyqtSignal(MapPoint)
    green_cell = pyqtSignal(MapPoint)
    red_cells = pyqtSignal(set)


class WorldSignals(QObject):
    curr_map_pos = pyqtSignal(object)
    color_pos = pyqtSignal(object, tuple)
    arrow_pos = pyqtSignal(object, object)
    reset_weight = pyqtSignal()
    reset_path = pyqtSignal()
