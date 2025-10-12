from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from PyQt6.QtCore import QObject, pyqtSignal


class MapSignals(QObject):
    white_cell = pyqtSignal(MapPoint)
    green_cell = pyqtSignal(MapPoint)
    red_cells = pyqtSignal(set)


class WorldSignals(QObject):
    curr_map_pos = pyqtSignal(object)
    color_pos = pyqtSignal(object, tuple)
    color_pos_batch = pyqtSignal(list)
    arrow_pos = pyqtSignal(object, object)
    arrow_pos_batch = pyqtSignal(list)
    reset_weight = pyqtSignal()
    reset_path = pyqtSignal()
