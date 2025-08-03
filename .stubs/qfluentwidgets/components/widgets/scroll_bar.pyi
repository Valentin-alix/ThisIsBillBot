from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QAbstractScrollArea
from qfluentwidgets.common.smooth_scroll import SmoothScroll as SmoothScroll

class SmoothScrollDelegate(QObject):
    verticalSmoothScroll: SmoothScroll
    horizonSmoothScroll: SmoothScroll
    def __init__(self, parent: QAbstractScrollArea, useAni: bool = False) -> None: ...
