from PyQt5.QtCore import QObject, pyqtSignal


class GridSignals(QObject):
    new_map_id = pyqtSignal(int)
    count_actor_on_cell_id = pyqtSignal(int, int)
    set_obstacle_on_cell_id = pyqtSignal(int, bool)
    set_stated_element_on_cell_id = pyqtSignal(int, bool)
