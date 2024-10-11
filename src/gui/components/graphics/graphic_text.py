from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsTextItem

TEXT_COLOR = Qt.black
TEXT_SIZE = 9


class GraphicText(QGraphicsTextItem):
    def __init__(self, text: str):
        super().__init__(text)
