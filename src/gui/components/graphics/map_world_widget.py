from collections import defaultdict
from dataclasses import dataclass
from math import floor

from dofus_unity_reader.models.datas.map_positions_root import MapInformationRootItem
from PyQt6.QtCore import QRectF, Qt, pyqtSlot
from PyQt6.QtGui import QColor, QPainter, QPen, QResizeEvent
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QStyleOptionGraphicsItem,
    QWidget,
)

from src.core.signals.world_signals import WorldSignals
from src.gui.components.graphics.graphic_text import TEXT_SIZE, GraphicText
from src.gui.utils.profiling import profiled_slot

type Coord = tuple[int, int]
type RGBColor = tuple[int, int, int]

CELL_SIZE: int = 50
LIMIT_GRID = 8

WIDTH_AROUND_CURRENT_MAP = CELL_SIZE * LIMIT_GRID * 2
HEIGHT_AROUND_CURRENT_MAP = CELL_SIZE * LIMIT_GRID * 2


class SquareMap(QGraphicsRectItem):
    DEFAULT = Qt.GlobalColor.white

    def __init__(self):
        self.colors_by_map_id: dict[int, RGBColor] = {}
        rect = QRectF(0, 0, CELL_SIZE, CELL_SIZE)
        super().__init__(rect)
        self.set_border()

    def add_color(self, map_id: int, color: RGBColor):
        self.colors_by_map_id[map_id] = color
        self.update()

    def reset_color(self):
        self.colors_by_map_id.clear()
        self.setBrush(SquareMap.DEFAULT)

    def set_border(self):
        pen = QPen(QColor("#A9A9A9"))
        pen.setWidth(0)
        self.setPen(pen)

    def paint(
        self,
        painter: QPainter | None,
        option: QStyleOptionGraphicsItem | None,
        widget: QWidget | None = None,
    ) -> None:
        if painter is None or option is None:
            return
        if len(self.colors_by_map_id) == 0:
            return super().paint(painter, option, widget)

        all_colors = set(self.colors_by_map_id.values())
        divided_height = floor(self.boundingRect().height() / len(all_colors))
        for index, color in enumerate(all_colors):
            painter.setBrush(QColor(*color))
            rect = QRectF(
                self.boundingRect().x(),
                self.boundingRect().y() + divided_height * index,
                self.boundingRect().width(),
                divided_height,
            )
            painter.drawRect(rect)


class MapCircle(QGraphicsEllipseItem):
    def __init__(self) -> None:
        super().__init__(
            CELL_SIZE // 4,
            CELL_SIZE // 4 + TEXT_SIZE,
            CELL_SIZE // 2,
            CELL_SIZE // 2,
        )
        self.setZValue(1)
        self.setBrush(Qt.GlobalColor.red)


@dataclass
class CurrMapInfo:
    state: MapCircle
    map_pos: MapInformationRootItem


class MapWorldView(QGraphicsView):
    def __init__(self, world_signals: WorldSignals | None = None, debug: bool = False) -> None:
        super().__init__()
        self.is_curr_map_visible: bool = False
        self.debug = debug
        self.world_signals = world_signals
        self.curr_map_info: CurrMapInfo | None = None
        self.line_items: list[QGraphicsLineItem] = []
        self._scene: QGraphicsScene = QGraphicsScene()
        self.square_by_coord: dict[Coord, SquareMap] = {}
        self.map_pos_by_coord: dict[Coord, set[MapInformationRootItem]] = defaultdict(set)

        self.setStyleSheet("border: 0px")
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setScene(self._scene)
        self.fitInView(self._scene.sceneRect(), mode=Qt.AspectRatioMode.KeepAspectRatio)

        if self.world_signals:
            self.world_signals.color_pos.connect(profiled_slot(self.on_color_pos))
            self.world_signals.color_pos_batch.connect(profiled_slot(self.on_color_pos_batch))
            self.world_signals.arrow_pos.connect(profiled_slot(self.on_arrow_pos))
            self.world_signals.arrow_pos_batch.connect(profiled_slot(self.on_arrow_pos_batch))
            self.world_signals.reset_weight.connect(profiled_slot(self.on_reset_weight))
            self.world_signals.reset_path.connect(profiled_slot(self.on_reset_path))
            self.world_signals.curr_map_pos.connect(profiled_slot(self.on_curr_map))

    def resizeEvent(self, event: QResizeEvent | None) -> None:
        self.fitInView(self._scene.sceneRect(), mode=Qt.AspectRatioMode.KeepAspectRatio)
        return super().resizeEvent(event)

    @pyqtSlot(MapInformationRootItem)
    def on_curr_map(self, map_pos: MapInformationRootItem):
        coord = map_pos.posX, map_pos.posY
        if self.curr_map_info is None:
            state = MapCircle()
            self._scene.addItem(state)
            self.curr_map_info = CurrMapInfo(state=state, map_pos=map_pos)
        else:
            self.curr_map_info.map_pos = map_pos

        x, y = self.get_pos_by_coord(coord)
        self.curr_map_info.state.setPos(x, y)
        left = x - CELL_SIZE * LIMIT_GRID
        top = y - CELL_SIZE * LIMIT_GRID
        self._scene.setSceneRect(QRectF(left, top, WIDTH_AROUND_CURRENT_MAP, HEIGHT_AROUND_CURRENT_MAP))
        self.centerOn(x, y)

    def get_or_create_map(self, map_pos: MapInformationRootItem) -> SquareMap:
        coord = map_pos.posX, map_pos.posY
        if coord not in self.square_by_coord:
            self.map_pos_by_coord[coord].add(map_pos)
            square = SquareMap()
            x, y = self.get_pos_by_coord(coord)
            square.setPos(x, y)
            self.square_by_coord[coord] = square
            self._scene.addItem(square)

            if self.debug:
                text = GraphicText(text=f"{coord[0]},{coord[1]}")
                text.setPos(x, y)
                text.setZValue(2)
                self._scene.addItem(text)

        return self.square_by_coord[coord]

    def get_pos_by_coord(self, coord: Coord) -> tuple[int, int]:
        return coord[0] * CELL_SIZE, coord[1] * CELL_SIZE

    @pyqtSlot(MapInformationRootItem, tuple)
    def on_color_pos(self, map_pos: MapInformationRootItem, color: RGBColor):
        square_cell = self.get_or_create_map(map_pos)
        square_cell.add_color(map_pos.id, color)

    @pyqtSlot(list)
    def on_color_pos_batch(self, items: list[tuple[MapInformationRootItem, RGBColor]]):
        self.setUpdatesEnabled(False)
        for map_pos, color in items:
            square_cell = self.get_or_create_map(map_pos)
            square_cell.add_color(map_pos.id, color)
        self.setUpdatesEnabled(True)

    @pyqtSlot(MapInformationRootItem, MapInformationRootItem)
    def on_arrow_pos(self, map_pos_start: MapInformationRootItem, map_pos_end: MapInformationRootItem):
        """draw line from start to end pos"""
        start_square = self.get_or_create_map(map_pos_start)
        end_square = self.get_or_create_map(map_pos_end)
        line_item = QGraphicsLineItem(
            start_square.x() + CELL_SIZE / 2,
            start_square.y() + CELL_SIZE / 2,
            end_square.x() + CELL_SIZE / 2,
            end_square.y() + CELL_SIZE / 2,
        )
        pen = QPen(Qt.GlobalColor.green)
        pen.setWidth(2)
        line_item.setPen(pen)
        self.line_items.append(line_item)
        self._scene.addItem(line_item)

    @pyqtSlot(list)
    def on_arrow_pos_batch(self, items: list[tuple[MapInformationRootItem, MapInformationRootItem]]):
        self.setUpdatesEnabled(False)
        for map_pos_start, map_pos_end in items:
            start_square = self.get_or_create_map(map_pos_start)
            end_square = self.get_or_create_map(map_pos_end)
            line_item = QGraphicsLineItem(
                start_square.x() + CELL_SIZE / 2,
                start_square.y() + CELL_SIZE / 2,
                end_square.x() + CELL_SIZE / 2,
                end_square.y() + CELL_SIZE / 2,
            )
            pen = QPen(Qt.GlobalColor.green)
            pen.setWidth(2)
            line_item.setPen(pen)
            self.line_items.append(line_item)
            self._scene.addItem(line_item)
        self.setUpdatesEnabled(True)

    @pyqtSlot()
    def on_reset_path(self):
        self.setUpdatesEnabled(False)
        while self.line_items:
            line_item = self.line_items.pop()
            self._scene.removeItem(line_item)
        self.setUpdatesEnabled(True)

    @pyqtSlot()
    def on_reset_weight(self):
        self.setUpdatesEnabled(False)
        for square in self.square_by_coord.values():
            square.reset_color()
        self.setUpdatesEnabled(True)
