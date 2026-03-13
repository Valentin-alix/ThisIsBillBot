import sys
from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import StatedElement
from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.grid.consts import CELL_HEIGHT, CELL_WIDTH
from DBDofusUnity.dofus_unity_reader.grid.map_point import MAP_POINT_BY_CELL_ID, MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.collectionsroot import Collectable
from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSlot
from PyQt6.QtGui import QColor, QFont, QMouseEvent, QPaintEvent, QPainter, QPen, QPicture, QPolygonF, QShowEvent
from PyQt6.QtWidgets import QApplication, QWidget

from src.core.signals.grid_signals import GridSignals
from src.core.signals.world_signals import MapSignals
from src.gui.utils.profiling import profiled_slot

CELL_BORDER_COLOR = QColor("#A9A9A9")
CIRCLE_CELL_SIZE = 15

_MOVABLE_COLOR = QColor(Qt.GlobalColor.lightGray)
_BLOCK_COLOR = QColor(Qt.GlobalColor.darkGray)
_EMPTY_COLOR = QColor(Qt.GlobalColor.black)
_DEFAULT_COLOR = QColor(Qt.GlobalColor.white)
_ACTOR_COLOR = QColor(Qt.GlobalColor.red)
_STATED_COLOR = QColor(Qt.GlobalColor.green)
_STATED_DOWN_COLOR = QColor(144, 238, 144)
_PATH_START_COLOR = QColor(Qt.GlobalColor.white)
_PATH_END_COLOR = QColor(Qt.GlobalColor.red)
_PATH_TREATED_COLOR = QColor(Qt.GlobalColor.green)

_CELL_POINTS = tuple(
    (cell_id, point.pixel_coord, (point.x, point.y)) for cell_id, point in MAP_POINT_BY_CELL_ID.items()
)
_MIN_X = min(pixel[0] for _, pixel, _ in _CELL_POINTS) - CELL_WIDTH / 2
_MAX_X = max(pixel[0] for _, pixel, _ in _CELL_POINTS) + CELL_WIDTH / 2
_MIN_Y = min(pixel[1] for _, pixel, _ in _CELL_POINTS) - CELL_HEIGHT / 2
_MAX_Y = max(pixel[1] for _, pixel, _ in _CELL_POINTS) + CELL_HEIGHT / 2
_SCENE_RECT = QRectF(_MIN_X, _MIN_Y, _MAX_X - _MIN_X, _MAX_Y - _MIN_Y)
_CELL_POLYGON_BY_ID = {
    cell_id: QPolygonF(
        [
            QPointF(x - CELL_WIDTH / 2, y),
            QPointF(x, y + CELL_HEIGHT / 2),
            QPointF(x + CELL_WIDTH / 2, y),
            QPointF(x, y - CELL_HEIGHT / 2),
        ]
    )
    for cell_id, (x, y), _ in _CELL_POINTS
}
_CELL_TEXT_RECT_BY_ID = {
    cell_id: QRectF(x - CELL_WIDTH / 2, y - CELL_HEIGHT / 2, CELL_WIDTH, CELL_HEIGHT)
    for cell_id, (x, y), _ in _CELL_POINTS
}


def readable_text_color(background: QColor) -> QColor:
    luminance = (0.299 * background.red() + 0.587 * background.green() + 0.114 * background.blue()) / 255
    return QColor(Qt.GlobalColor.black) if luminance > 0.5 else QColor(Qt.GlobalColor.white)


@dataclass(slots=True)
class CellState:
    is_obstacle: bool = False
    count_actor: int = 0
    stated_element: StatedElement | None = None
    collectable: Collectable | None = None
    debug_color: QColor | None = None

    def color(self) -> QColor | None:
        if self.debug_color is not None:
            return self.debug_color
        if self.is_obstacle:
            return _BLOCK_COLOR
        if self.stated_element is not None:
            return _STATED_COLOR if self.collectable is not None else _STATED_DOWN_COLOR
        if self.count_actor > 0:
            return _ACTOR_COLOR
        return None


class GridView(QWidget):
    def __init__(
        self,
        grid_signals: GridSignals,
        debug_signals: MapSignals | None = None,
    ) -> None:
        super().__init__()
        self.grid_signals = grid_signals
        self.debug_signals = debug_signals
        self._map_id = 0
        self._rendered_map_id = 0
        self._cell_color_by_id: dict[int, QColor] = {}
        self._state_by_cell_id = {cell_id: CellState() for cell_id in MAP_POINT_BY_CELL_ID}
        self._active_cell_ids: set[int] = set()
        self._font = QFont("Arial", 10)
        self._static_grid_picture = QPicture()
        self._rebuild_static_grid_picture()

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

    def paintEvent(self, a0: QPaintEvent | None) -> None:
        if self._map_id != self._rendered_map_id:
            self._load_map_colors()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        offset_x, offset_y, scale = self._view_transform()
        painter.translate(offset_x, offset_y)
        painter.scale(scale, scale)
        painter.drawPicture(0, 0, self._static_grid_picture)

        for cell_id in self._active_cell_ids:
            color = self._state_by_cell_id[cell_id].color()
            if color is None:
                continue
            x, y = MAP_POINT_BY_CELL_ID[cell_id].pixel_coord
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), CIRCLE_CELL_SIZE, CIRCLE_CELL_SIZE)
            painter.setPen(readable_text_color(color))
            painter.drawText(
                QRectF(
                    x - CIRCLE_CELL_SIZE,
                    y - CIRCLE_CELL_SIZE,
                    CIRCLE_CELL_SIZE * 2,
                    CIRCLE_CELL_SIZE * 2,
                ),
                Qt.AlignmentFlag.AlignCenter,
                str(cell_id),
            )
        painter.end()
        super().paintEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        if a0 is not None and a0.button() == Qt.MouseButton.LeftButton:
            offset_x, offset_y, scale = self._view_transform()
            scene_pos = QPointF(
                (a0.position().x() - offset_x) / scale,
                (a0.position().y() - offset_y) / scale,
            )
            for cell_id, (x, y), _ in _CELL_POINTS:
                if self._cell_polygon(x, y).containsPoint(scene_pos, Qt.FillRule.OddEvenFill):
                    self.grid_signals.cell_id_clicked.emit(cell_id)
                    break
        super().mousePressEvent(a0)

    def showEvent(self, a0: QShowEvent | None) -> None:
        if self._map_id != self._rendered_map_id:
            self._load_map_colors()
        super().showEvent(a0)

    @staticmethod
    def _cell_polygon(x: float, y: float) -> QPolygonF:
        return QPolygonF(
            [
                QPointF(x - CELL_WIDTH / 2, y),
                QPointF(x, y + CELL_HEIGHT / 2),
                QPointF(x + CELL_WIDTH / 2, y),
                QPointF(x, y - CELL_HEIGHT / 2),
            ]
        )

    def _view_transform(self) -> tuple[float, float, float]:
        scale = min(self.width() / _SCENE_RECT.width(), self.height() / _SCENE_RECT.height()) * 0.95
        offset_x = (self.width() - _SCENE_RECT.width() * scale) / 2 - _SCENE_RECT.left() * scale
        offset_y = (self.height() - _SCENE_RECT.height() * scale) / 2 - _SCENE_RECT.top() * scale
        return offset_x, offset_y, scale

    def _load_map_colors(self) -> None:
        self._cell_color_by_id.clear()
        if self._map_id == 0:
            self._rendered_map_id = 0
            return
        map_reader = MapReader()
        map_data = map_reader.map_by_id(self._map_id)
        for cell_data in map_data.mapData.cellsData:
            if cell_data.mov == 1:
                color = _MOVABLE_COLOR
            elif cell_data.los != 1:
                color = _BLOCK_COLOR
            else:
                color = _EMPTY_COLOR
            self._cell_color_by_id[cell_data.cellNumber] = color
        self._rendered_map_id = self._map_id
        self._rebuild_static_grid_picture()

    def _rebuild_static_grid_picture(self) -> None:
        self._static_grid_picture = QPicture()
        painter = QPainter(self._static_grid_picture)
        painter.setFont(self._font)
        border_pen = QPen(CELL_BORDER_COLOR)
        border_pen.setCosmetic(True)
        painter.setPen(border_pen)
        for cell_id, _, _ in _CELL_POINTS:
            color = self._cell_color_by_id.get(cell_id, _DEFAULT_COLOR)
            painter.setBrush(color)
            painter.drawPolygon(_CELL_POLYGON_BY_ID[cell_id])
            painter.setPen(readable_text_color(color))
            painter.drawText(_CELL_TEXT_RECT_BY_ID[cell_id], Qt.AlignmentFlag.AlignCenter, str(cell_id))
            painter.setPen(border_pen)
        painter.end()

    def _request_visible_update(self) -> None:
        if self.isVisible():
            self.update()

    @pyqtSlot(int)
    def on_new_map_id(self, map_id: int) -> None:
        self._map_id = map_id
        if self.isVisible():
            self._load_map_colors()
            self.update()

    @pyqtSlot(list)
    def on_new_count_actor_on_cell_id_batch(self, items: list[tuple[int, int]]) -> None:
        for cell_id, count_actor in items:
            if cell_id in self._state_by_cell_id:
                self._state_by_cell_id[cell_id].count_actor = count_actor
                self._update_active_cell(cell_id)
        self._request_visible_update()

    @pyqtSlot(list)
    def on_set_stated_element_on_cell_id_batch(
        self, items: list[tuple[int, StatedElement | None, Collectable | None]]
    ) -> None:
        for cell_id, stated_element, collectable in items:
            state = self._state_by_cell_id[cell_id]
            state.stated_element = stated_element
            state.collectable = collectable
            self._update_active_cell(cell_id)
        self._request_visible_update()

    @pyqtSlot(list)
    def on_set_obstacle_on_cell_id_batch(self, items: list[tuple[int, bool]]) -> None:
        for cell_id, is_obstacle in items:
            self._state_by_cell_id[cell_id].is_obstacle = is_obstacle
            self._update_active_cell(cell_id)
        self._request_visible_update()

    @pyqtSlot(MapPoint)
    def on_debug_white_cell(self, mp: MapPoint) -> None:
        self._state_by_cell_id[mp.cell_id].debug_color = _PATH_START_COLOR
        self._update_active_cell(mp.cell_id)
        self._request_visible_update()

    @pyqtSlot(MapPoint)
    def on_debug_red_cells(self, mps: set[MapPoint]) -> None:
        for mp in mps:
            self._state_by_cell_id[mp.cell_id].debug_color = _PATH_END_COLOR
            self._update_active_cell(mp.cell_id)
        self._request_visible_update()

    @pyqtSlot(MapPoint)
    def on_debug_green_cell(self, mp: MapPoint) -> None:
        self._state_by_cell_id[mp.cell_id].debug_color = _PATH_TREATED_COLOR
        self._update_active_cell(mp.cell_id)
        self._request_visible_update()

    def _update_active_cell(self, cell_id: int) -> None:
        if self._state_by_cell_id[cell_id].color() is None:
            self._active_cell_ids.discard(cell_id)
        else:
            self._active_cell_ids.add(cell_id)


if __name__ == "__main__":
    application = QApplication(sys.argv)
    widget = GridView(GridSignals())
    widget.on_new_map_id(153886720)
    widget.show()
    application.exec()
