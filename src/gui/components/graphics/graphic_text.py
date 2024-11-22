from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsTextItem

TEXT_COLOR = Qt.GlobalColor.black
TEXT_SIZE = 9


class GraphicText(QGraphicsTextItem):
    def __init__(self, text: str):
        super().__init__(text)
