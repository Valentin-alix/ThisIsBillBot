from PyQt5.QtCore import QObject, pyqtSignal

from src.core.logic.grid.map_point import MapPoint


class PathFindingSignals(QObject):
    start_cell = pyqtSignal(MapPoint)
    treated_cell = pyqtSignal(MapPoint)
    end_cells = pyqtSignal(set)
