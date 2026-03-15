from PyQt6.QtCore import QObject, QEasingCurve
from PyQt6.QtWidgets import QAbstractScrollArea, QWidget
from qfluentwidgets.common.smooth_scroll import SmoothScroll as SmoothScroll

class SmoothScrollBar(QWidget):
    def setScrollAnimation(self, duration: int, easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic) -> None: ...

class SmoothScrollDelegate(QObject):
    vScrollBar: SmoothScrollBar
    hScrollBar: SmoothScrollBar
    verticalSmoothScroll: SmoothScroll
    horizonSmoothScroll: SmoothScroll
    def __init__(self, parent: QAbstractScrollArea, useAni: bool = False) -> None: ...
