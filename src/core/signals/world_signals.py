from d3_database.grid.map_point import MapPoint
from PyQt6.QtCore import QObject, pyqtSignal


class MapSignals(QObject):
    white_cell = pyqtSignal(MapPoint)
    green_cell = pyqtSignal(MapPoint)
    red_cells = pyqtSignal(set)


class WorldSignals(QObject):
    curr_map_pos = pyqtSignal(object)
    color_pos = pyqtSignal(object, tuple)
    color_pos_batch = pyqtSignal(list)  # list of (map_pos, color) tuples
    arrow_pos = pyqtSignal(object, object)
    arrow_pos_batch = pyqtSignal(list)  # list of (map_pos_start, map_pos_end) tuples
    reset_weight = pyqtSignal()
    reset_path = pyqtSignal()
