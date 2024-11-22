import sys

from PyQt6.QtCore import QPointF, Qt, pyqtSlot
from PyQt6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
)

from D3Database.data_center.map_reader import MapReader
from D3Database.grid.consts import CELL_HEIGHT, CELL_WIDTH
from D3Database.grid.map_point import MAP_POINT_BY_CELL_ID, MapPoint
from D3Database.models.datas.collectionsroot import Collectable
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import StatedElement
from src.core.signals.grid_signals import GridSignals
from src.core.signals.world_signals import MapSignals
from src.gui.utils.profiling import profiled_slot

CELL_BORDER_COLOR = QColor("#A9A9A9")
CELL_TEXT_COLOR = Qt.GlobalColor.black

CIRCLE_CELL_SIZE = 15


class SquareCell(QGraphicsPolygonItem):
    MOVABLE = Qt.GlobalColor.lightGray
    BLOCK = Qt.GlobalColor.darkGray
    EMPTY = Qt.GlobalColor.black
    PATH_FINDING_TREATED = Qt.GlobalColor.green
    PATH_FINDING_START = Qt.GlobalColor.white
    PATH_FINDING_END = Qt.GlobalColor.red

    def __init__(self, cell_id: int):
        super().__init__()

        # draw 2d isometric square
        self.setPolygon(
            QPolygonF(
                [
                    QPointF(-CELL_WIDTH / 2, 0),
                    QPointF(0, CELL_HEIGHT / 2),
                    QPointF(CELL_WIDTH / 2, 0),
                    QPointF(0, -CELL_HEIGHT / 2),
                ]
            )
        )
        text = str(cell_id)
        self.text_item = QGraphicsTextItem(text, parent=self)
        self.text_item.setDefaultTextColor(CELL_TEXT_COLOR)
        self.text_item.setFont(QFont("Arial", 10))
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
        self.text_item.setPlainText(text)

        pen = QPen(CELL_BORDER_COLOR)
        pen.setWidth(1)
        self.setPen(pen)


class StateCell(QGraphicsEllipseItem):
    ACTOR = Qt.GlobalColor.red
    STATED = Qt.GlobalColor.green
    STATED_DOWN = QColor(144, 238, 144)
    OBSTACLE = Qt.GlobalColor.darkGray

    def __init__(self, cell_id: int) -> None:
        super().__init__(
            -CIRCLE_CELL_SIZE,
            -CIRCLE_CELL_SIZE,
            2 * CIRCLE_CELL_SIZE,
            2 * CIRCLE_CELL_SIZE,
        )
        self.is_obstacle: bool = False
        self.count_actor: int = 0
        self.state_element: StatedElement | None = None
        self.collectable: Collectable | None = None

        text = str(cell_id)
        self.text_item = QGraphicsTextItem(text, parent=self)
        self.text_item.setDefaultTextColor(CELL_TEXT_COLOR)
        self.text_item.setFont(QFont("Arial", 10))
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
        self.text_item.setPlainText(text)

        self.update_state()

    @property
    def is_empty(self):
        return not self.is_obstacle and self.count_actor == 0 and not self.state_element

    def set_count_actor(self, count_actor: int) -> None:
        self.count_actor = count_actor
        self.update_state()

    def set_state_element(
        self, stated_element: StatedElement | None, collectable: Collectable | None
    ) -> None:
        self.state_element = stated_element
        self.collectable = collectable
        self.update_state()

    def set_is_obstacle(self, is_obstacle: bool) -> None:
        self.is_obstacle = is_obstacle
        self.update_state()

    def update_state(self) -> None:
        if self.is_obstacle:
            self.setVisible(True)
            self.setBrush(self.OBSTACLE)
        elif self.state_element is not None:
            self.setVisible(True)
            if self.collectable is not None:
                self.setBrush(self.STATED)
            else:
                self.setBrush(self.STATED_DOWN)
        elif self.count_actor > 0:
            self.setVisible(True)
            self.setBrush(self.ACTOR)
        else:
            self.setVisible(False)


class GridView(QGraphicsView):
    def __init__(
        self,
        grid_signals: GridSignals,
        debug_signals: MapSignals | None = None,
    ) -> None:
        super().__init__()
        self.setStyleSheet("border: 0px")
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.grid_signals = grid_signals
        self.debug_signals = debug_signals
        self._scene: QGraphicsScene = QGraphicsScene()

        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.cell_square_by_coord: dict[tuple[int, int], SquareCell] = {}
        self.cell_state_by_coord: dict[tuple[int, int], StateCell] = {}

        self.setScene(self._scene)

        self.init_grid()

        self.scale(0.75, 0.75)

        self.grid_signals.count_actor_on_cell_id_batch.connect(
            profiled_slot(self.on_new_count_actor_on_cell_id_batch)
        )
        self.grid_signals.set_stated_element_on_cell_id_batch.connect(
            profiled_slot(self.on_set_stated_element_on_cell_id_batch)
        )
        self.grid_signals.set_obstacle_on_cell_id_batch.connect(
            profiled_slot(self.on_set_obstacle_on_cell_id_batch)
        )
        self.grid_signals.new_map_id.connect(profiled_slot(self.on_new_map_id))

        if self.debug_signals:
            self.debug_signals.white_cell.connect(self.on_debug_white_cell)
            self.debug_signals.red_cells.connect(self.on_debug_red_cells)
            self.debug_signals.green_cell.connect(self.on_debug_green_cell)

        self.fitInView(self._scene.sceneRect(), mode=Qt.AspectRatioMode.KeepAspectRatio)
        self.resizeEvent = self.on_resize

    def mousePressEvent(self, event: QMouseEvent | None):
        if event is not None and event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            item = self._scene.itemAt(scene_pos, self.transform())
            if isinstance(item, (SquareCell, StateCell)):
                cell_id = int(item.text_item.toPlainText())
                self.grid_signals.cell_id_clicked.emit(cell_id)
            elif isinstance(item, QGraphicsTextItem):
                cell_id = int(item.toPlainText())
                self.grid_signals.cell_id_clicked.emit(cell_id)

        return super().mousePressEvent(event)

    def init_grid(self) -> None:
        self.setUpdatesEnabled(False)

        x: float
        y: float
        for cell_id, point in MAP_POINT_BY_CELL_ID.items():
            x, y = point.pixel_coord
            coord_cell = (point.x, point.y)
            square_cell, state_cell = self.add_cell(x, y, cell_id)
            self.cell_square_by_coord[coord_cell] = square_cell
            self.cell_state_by_coord[coord_cell] = state_cell

        self.setUpdatesEnabled(True)

    def on_resize(self, event):
        self.fitInView(self._scene.sceneRect(), mode=Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    def add_cell(
        self, x: float, y: float, cell_id: int
    ) -> tuple[SquareCell, StateCell]:
        square_cell = SquareCell(cell_id)
        square_cell.setPos(x, y)
        self._scene.addItem(square_cell)

        state_cell = StateCell(cell_id)
        state_cell.setPos(x, y)
        self._scene.addItem(state_cell)

        return square_cell, state_cell

    @pyqtSlot(int)
    def on_new_map_id(self, map_id: int):
        for cell_data in MapReader().map_by_id(map_id).mapData.cellsData:
            mp = MapPoint.from_cell_id(cell_data.cellNumber)
            cell_square = self.cell_square_by_coord[(mp.x, mp.y)]
            if cell_data.mov == 1:
                cell_square.setBrush(SquareCell.MOVABLE)
            elif cell_data.los != 1:
                cell_square.setBrush(SquareCell.BLOCK)
            else:
                cell_square.setBrush(SquareCell.EMPTY)

    @pyqtSlot(list)
    def on_new_count_actor_on_cell_id_batch(self, items: list[tuple[int, int]]):
        self.setUpdatesEnabled(False)
        for cell_id, count_actor in items:
            if cell_id not in MAP_POINT_BY_CELL_ID:
                continue
            mp = MapPoint.from_cell_id(cell_id)
            self.cell_state_by_coord[(mp.x, mp.y)].set_count_actor(count_actor)
        self.setUpdatesEnabled(True)

    @pyqtSlot(list)
    def on_set_stated_element_on_cell_id_batch(
        self, items: list[tuple[int, StatedElement | None, Collectable | None]]
    ):
        self.setUpdatesEnabled(False)
        for cell_id, stated_element, collectable in items:
            mp = MapPoint.from_cell_id(cell_id)
            self.cell_state_by_coord[(mp.x, mp.y)].set_state_element(
                stated_element, collectable
            )
        self.setUpdatesEnabled(True)

    @pyqtSlot(list)
    def on_set_obstacle_on_cell_id_batch(self, items: list[tuple[int, bool]]):
        self.setUpdatesEnabled(False)
        for cell_id, is_obstacle in items:
            mp = MapPoint.from_cell_id(cell_id)
            self.cell_state_by_coord[(mp.x, mp.y)].set_is_obstacle(is_obstacle)
        self.setUpdatesEnabled(True)

    @pyqtSlot(MapPoint)
    def on_debug_white_cell(self, mp: MapPoint):
        self.cell_state_by_coord[(mp.x, mp.y)].setVisible(True)
        self.cell_state_by_coord[(mp.x, mp.y)].setBrush(SquareCell.PATH_FINDING_START)

    @pyqtSlot(MapPoint)
    def on_debug_red_cells(self, mps: set[MapPoint]):
        for mp in mps:
            self.cell_state_by_coord[(mp.x, mp.y)].setVisible(True)
            self.cell_state_by_coord[(mp.x, mp.y)].setBrush(SquareCell.PATH_FINDING_END)

    @pyqtSlot(MapPoint)
    def on_debug_green_cell(self, mp: MapPoint):
        self.cell_state_by_coord[(mp.x, mp.y)].setVisible(True)
        self.cell_state_by_coord[(mp.x, mp.y)].setBrush(SquareCell.PATH_FINDING_TREATED)


if __name__ == "__main__":
    application = QApplication(sys.argv)
    widget = GridView(GridSignals())
    widget.on_new_map_id(153886720)
    widget.show()
    application.exec()
