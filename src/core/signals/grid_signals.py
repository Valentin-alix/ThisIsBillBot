from PyQt5.QtCore import QObject, pyqtSignal


class GridSignals(QObject):
    new_map_id = pyqtSignal(int)
    count_actor_on_cell_id = pyqtSignal(int, int)
    count_actor_on_cell_id_batch = pyqtSignal(list)  # list of (cell_id, count)
    set_obstacle_on_cell_id = pyqtSignal(int, bool)
    set_obstacle_on_cell_id_batch = pyqtSignal(list)  # list of (cell_id, is_obstacle)
    set_stated_element_on_cell_id = pyqtSignal(int, object, object)
    set_stated_element_on_cell_id_batch = pyqtSignal(list)  # list of (cell_id, stated_element, collectable)
    cell_id_clicked = pyqtSignal(int)
    is_in_map_transition = pyqtSignal(bool)
