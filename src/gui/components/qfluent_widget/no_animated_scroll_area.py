from PyQt6.QtWidgets import QScrollArea
from qfluentwidgets.common import SmoothMode
from qfluentwidgets.components.widgets.scroll_bar import SmoothScrollDelegate


class NoAnimatedScrollArea(QScrollArea):
    """Smooth scroll area"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrollDelagate = SmoothScrollDelegate(self)
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)

    def enableTransparentBackground(self):
        self.setStyleSheet("QScrollArea{border: none; background: transparent}")

        inner = self.widget()
        if inner:
            inner.setStyleSheet("QWidget{background: transparent}")
