import sys

from PyQt5.QtCore import QPointF, Qt, pyqtSlot
from PyQt5.QtGui import QPolygonF, QColor, QFont, QPen, QPainter
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsPolygonItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsEllipseItem,
)

from src.core.data_center.map_reader import MapReader
from src.core.logic.grid.consts import CELL_HEIGHT, CELL_WIDTH
from src.core.logic.grid.map_point import MapPoint, MAP_POINT_BY_CELL_ID
from src.signals.grid_signals import GridSignals
from src.signals.world_signals import MapSignals

CELL_BORDER_COLOR = QColor("#A9A9A9")
CELL_TEXT_COLOR = Qt.black

CIRCLE_CELL_SIZE = 15


class SquareCell(QGraphicsPolygonItem):
    MOVABLE = Qt.lightGray
    BLOCK = Qt.darkGray
    EMPTY = Qt.black
    PATH_FINDING_TREATED = Qt.green
    PATH_FINDING_START = Qt.white
    PATH_FINDING_END = Qt.red

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
    ACTOR = Qt.red
    STATED = Qt.green
    STATED_DOWN = QColor(144, 238, 144)
    OBSTACLE = Qt.darkGray

    def __init__(self, cell_id: int) -> None:
        super().__init__(
            -CIRCLE_CELL_SIZE,
            -CIRCLE_CELL_SIZE,
            2 * CIRCLE_CELL_SIZE,
            2 * CIRCLE_CELL_SIZE,
        )
        self.is_obstacle: bool = False
        self.count_actor: int = 0
        self.state_element: int | None = None

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

    def set_state_element(self, state: int | None) -> None:
        self.state_element = state
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
            if self.state_element == 0:
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
        self.setAlignment(Qt.AlignTop)
        self.grid_signals = grid_signals
        self.debug_signals = debug_signals
        self.scene: QGraphicsScene = QGraphicsScene()  # type: ignore

        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.cell_square_by_coord: dict[tuple[int, int], SquareCell] = {}
        self.cell_state_by_coord: dict[tuple[int, int], StateCell] = {}

        self.setScene(self.scene)

        self.init_grid()

        self.scale(0.75, 0.75)

        self.grid_signals.count_actor_on_cell_id.connect(
            self.on_new_count_actor_on_cell_id
        )
        self.grid_signals.set_stated_element_on_cell_id.connect(
            self.on_set_stated_element_on_cell_id
        )
        self.grid_signals.set_obstacle_on_cell_id.connect(
            self.on_set_obstacle_on_cell_id
        )
        self.grid_signals.new_map_id.connect(self.on_new_map_id)

        if self.debug_signals:
            self.debug_signals.white_cell.connect(self.on_debug_white_cell)
            self.debug_signals.red_cells.connect(self.on_debug_red_cells)
            self.debug_signals.green_cell.connect(self.on_debug_green_cell)

        self.fitInView(self.scene.sceneRect(), mode=Qt.AspectRatioMode.KeepAspectRatio)
        self.resizeEvent = self.on_resize  # type: ignore

    def init_grid(self) -> None:
        x: float
        y: float
        for cell_id, point in MAP_POINT_BY_CELL_ID.items():
            x, y = point.pixel_coord
            coord_cell = (point.x, point.y)
            square_cell, state_cell = self.add_cell(x, y, cell_id)
            self.cell_square_by_coord[coord_cell] = square_cell
            self.cell_state_by_coord[coord_cell] = state_cell

    def on_resize(self, event):
        self.fitInView(self.scene.sceneRect(), mode=Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    def add_cell(
        self, x: float, y: float, cell_id: int
    ) -> tuple[SquareCell, StateCell]:
        square_cell = SquareCell(cell_id)
        square_cell.setPos(x, y)
        self.scene.addItem(square_cell)

        state_cell = StateCell(cell_id)
        state_cell.setPos(x, y)
        self.scene.addItem(state_cell)

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

    @pyqtSlot(int, int)
    def on_new_count_actor_on_cell_id(self, cell_id: int, count_actor: int):
        mp = MapPoint.from_cell_id(cell_id)
        self.cell_state_by_coord[(mp.x, mp.y)].set_count_actor(count_actor)

    @pyqtSlot(int, object)
    def on_set_stated_element_on_cell_id(self, cell_id: int, state: int | None):
        mp = MapPoint.from_cell_id(cell_id)
        self.cell_state_by_coord[(mp.x, mp.y)].set_state_element(state)

    @pyqtSlot(int, bool)
    def on_set_obstacle_on_cell_id(self, cell_id: int, is_obstacle: bool):
        mp = MapPoint.from_cell_id(cell_id)
        self.cell_state_by_coord[(mp.x, mp.y)].set_is_obstacle(is_obstacle)

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
