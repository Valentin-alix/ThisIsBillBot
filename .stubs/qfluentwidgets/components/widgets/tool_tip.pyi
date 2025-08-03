from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget

class ToolTipFilter(QObject):
    def __init__(self, parent: QWidget, showDelay: int = 300) -> None: ...
